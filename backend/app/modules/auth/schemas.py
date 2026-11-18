from pydantic import BaseModel, EmailStr, Field


# User Registration
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# Email OTP Verification
class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)


# Resend OTP
class ResendOTPRequest(BaseModel):
    email: EmailStr


# User Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Authentication Response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: EmailStr


# Forgot Password
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Reset Password
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


# User Information
class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    is_active: bool