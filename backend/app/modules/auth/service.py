"""Business logic for authentication."""

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.modules.students.models import Student
import secrets
import hashlib
import smtplib

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.auth.models import User, EmailOTP
from app.modules.auth.schemas import (
    RegisterRequest,
    OTPVerifyRequest,
    ResendOTPRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)


# PBKDF2-SHA256 is the default.
# Existing bcrypt hashes remain supported.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated=["bcrypt"],
    pbkdf2_sha256__rounds=600000,
)


# ------------------------------------------
# PASSWORD UTILITIES
# ------------------------------------------

def validate_password(password: str):
    """Validate password strength."""

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    if not any(char.isupper() for char in password):
        raise ValueError(
            "Password must contain at least one uppercase letter."
        )

    if not any(char.islower() for char in password):
        raise ValueError(
            "Password must contain at least one lowercase letter."
        )

    if not any(char.isdigit() for char in password):
        raise ValueError(
            "Password must contain at least one number."
        )

    if not any(
        not char.isalnum() and not char.isspace()
        for char in password
    ):
        raise ValueError(
            "Password must contain at least one special character."
        )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# ------------------------------------------
# OTP UTILITIES
# ------------------------------------------

def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(
        f"{settings.jwt_secret_key}:{otp}".encode()
    ).hexdigest()


def send_otp_email(email: str, otp: str):
    if not all([
        settings.smtp_host,
        settings.smtp_username,
        settings.smtp_password,
        settings.smtp_sender_email,
    ]):
        raise ValueError("Email service is not configured.")

    message = EmailMessage()
    message["Subject"] = "Study Planner - Email Verification"
    message["From"] = settings.smtp_sender_email
    message["To"] = email

    message.set_content(
        f"""
Welcome to Intelligent Adaptive Study Planner!

Your verification code is:

{otp}

This code expires in {settings.otp_expire_minutes} minutes.

If you did not request this code, please ignore this email.
"""
    )

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=15,
    ) as server:

        if settings.smtp_use_tls:
            server.starttls()

        server.login(
            settings.smtp_username,
            settings.smtp_password,
        )

        server.send_message(message)


def create_and_send_otp(
    session: Session,
    email: str,
):
    otp = generate_otp()

    record = EmailOTP(
        email=email,
        otp_hash=hash_otp(otp),
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=settings.otp_expire_minutes),
    )

    session.add(record)
    session.flush()

    send_otp_email(email, otp)


def verify_otp_record(
    session: Session,
    email: str,
    otp: str,
):
    record = session.exec(
        select(EmailOTP)
        .where(EmailOTP.email == email)
        .where(EmailOTP.is_used == False)
        .order_by(EmailOTP.created_at.desc())
    ).first()

    if not record:
        raise ValueError("Invalid or expired verification code.")

    current_time = datetime.now(timezone.utc)

    expires_at = record.expires_at

    # SQLite may return datetime values without timezone information.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < current_time:
        raise ValueError("Verification code has expired.")

    if not secrets.compare_digest(
        record.otp_hash,
        hash_otp(otp),
    ):
        raise ValueError("Incorrect verification code.")

    record.is_used = True
    session.add(record)

    return record


# ------------------------------------------
# JWT AUTHENTICATION
# ------------------------------------------

def create_access_token(user_id: int, email: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise ValueError("Invalid or expired authentication token.")


# ------------------------------------------
# USER REGISTRATION
# ------------------------------------------

def register_user(
    session: Session,
    data: RegisterRequest,
):
    validate_password(data.password)

    email = str(data.email).lower()

    existing = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing:
        raise ValueError("An account with this email already exists.")

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        is_verified=False,
        is_active=True,
    )

    try:
        session.add(user)
        session.flush()

        create_and_send_otp(session, email)

        session.commit()
        session.refresh(user)

        return user

    except Exception:
        session.rollback()
        raise


# ------------------------------------------
# EMAIL VERIFICATION
# ------------------------------------------

def verify_email_otp(
    session: Session,
    data: OTPVerifyRequest,
):
    email = str(data.email).lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise ValueError("Account not found.")

    if user.is_verified:
        raise ValueError("Email is already verified.")

    try:
        verify_otp_record(session, email, data.otp)

        user.is_verified = True
        session.add(user)
        session.flush()

        student = session.exec(
            select(Student).where(Student.user_id == user.id)
        ).first()

        if not student:
            student = session.exec(
                select(Student).where(Student.email == email)
            ).first()

        if student:
            student.user_id = user.id
        else:
            student = Student(
                user_id=user.id,
                full_name="",
                email=email,
            )

        session.add(student)
        session.commit()
        session.refresh(user)

        return {"message": "Email verified and student profile created."}

    except Exception:
        session.rollback()
        raise


# ------------------------------------------
# RESEND OTP
# ------------------------------------------

def resend_email_otp(
    session: Session,
    data: ResendOTPRequest,
):
    email = str(data.email).lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise ValueError("Account not found.")

    if user.is_verified:
        raise ValueError("Email is already verified.")

    try:
        # Mark previous unused OTPs as used
        old_otps = session.exec(
            select(EmailOTP)
            .where(EmailOTP.email == email)
            .where(EmailOTP.is_used == False)
        ).all()

        for old_otp in old_otps:
            old_otp.is_used = True
            session.add(old_otp)

        # Generate and send a fresh OTP
        create_and_send_otp(session, email)

        session.commit()

        return {
            "message": "A new verification code has been sent."
        }

    except Exception:
        session.rollback()
        raise


# ------------------------------------------
# USER LOGIN
# ------------------------------------------

def login_user(
    session: Session,
    data: LoginRequest,
):
    email = str(data.email).lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user or not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise ValueError("Invalid email or password.")

    # Automatically upgrade old bcrypt hashes
    # to PBKDF2-SHA256 after successful login.
    if pwd_context.needs_update(user.hashed_password):
        user.hashed_password = hash_password(data.password)
        session.add(user)
        session.commit()

    if not user.is_verified:
        raise ValueError("Please verify your email before logging in.")

    if not user.is_active:
        raise ValueError("This account is inactive.")

    token = create_access_token(user.id, user.email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }


# ------------------------------------------
# FORGOT PASSWORD
# ------------------------------------------

def forgot_password(
    session: Session,
    data: ForgotPasswordRequest,
):
    email = str(data.email).lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if user and user.is_active and user.is_verified:
        try:
            create_and_send_otp(session, email)
            session.commit()

        except Exception:
            session.rollback()
            raise

    return {
        "message": "If the account exists, a password reset code will be sent."
    }


# ------------------------------------------
# RESET PASSWORD
# ------------------------------------------

def reset_password(
    session: Session,
    data: ResetPasswordRequest,
):
    validate_password(data.new_password)

    email = str(data.email).lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user or not user.is_verified:
        raise ValueError("Invalid password reset request.")

    try:
        verify_otp_record(session, email, data.otp)

        user.hashed_password = hash_password(data.new_password)

        session.add(user)
        session.commit()

        return {"message": "Password reset successfully."}

    except Exception:
        session.rollback()
        raise

# ------------------------------------------
# GOOGLE AUTHENTICATION
# ------------------------------------------

def google_login(session: Session, credential: str):
    if not settings.google_client_id:
        raise ValueError("Google authentication is not configured.")

    try:
        google_user = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except Exception:
        raise ValueError("Invalid Google authentication. Please try again.")

    email = google_user.get("email", "").lower()

    if not email or not google_user.get("email_verified"):
        raise ValueError("Google email is not verified.")

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    try:
        if user:
            if not user.is_active:
                raise ValueError("This account is inactive.")
            user.is_verified = True
        else:
            user = User(
                email=email,
                hashed_password=hash_password(
                    secrets.token_urlsafe(48)
                ),
                is_verified=True,
                is_active=True,
            )
            session.add(user)
            session.flush()

        student = session.exec(
            select(Student).where(Student.user_id == user.id)
        ).first()

        if not student:
            student = session.exec(
                select(Student).where(Student.email == email)
            ).first()

        if student:
            student.user_id = user.id
        else:
            student = Student(
                user_id=user.id,
                full_name="",
                email=email,
            )

        session.add(student)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {
            "access_token": create_access_token(user.id, user.email),
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
        }

    except Exception:
        session.rollback()
        raise