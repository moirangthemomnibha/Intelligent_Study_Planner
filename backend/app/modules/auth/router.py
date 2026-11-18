"""HTTP endpoints for authentication."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database.session import get_session
from app.modules.auth.schemas import (
    RegisterRequest,
    OTPVerifyRequest,
    ResendOTPRequest,
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserRead,
)
from app.modules.auth.service import (
    register_user,
    verify_email_otp,
    resend_email_otp,
    login_user,
    forgot_password,
    reset_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
def register(
    data: RegisterRequest,
    session: Session = Depends(get_session),
):
    try:
        return register_user(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/verify-email")
def verify_email(
    data: OTPVerifyRequest,
    session: Session = Depends(get_session),
):
    try:
        return verify_email_otp(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/resend-otp")
def resend_otp(
    data: ResendOTPRequest,
    session: Session = Depends(get_session),
):
    try:
        return resend_email_otp(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    session: Session = Depends(get_session),
):
    try:
        return login_user(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/forgot-password")
def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    session: Session = Depends(get_session),
):
    return forgot_password(session, data)


@router.post("/reset-password")
def reset_password_endpoint(
    data: ResetPasswordRequest,
    session: Session = Depends(get_session),
):
    try:
        return reset_password(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))