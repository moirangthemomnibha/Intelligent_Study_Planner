"""Centralized environment configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Intelligent Adaptive Study Planner"

    database_url: str = "sqlite:///./study_planner.db"

    # JWT authentication
    jwt_secret_key: str = "CHANGE_THIS_IN_ENV"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Email OTP configuration
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender_email: str = ""
    smtp_use_tls: bool = True
    otp_expire_minutes: int = 5

    # Frontend
    frontend_origin: str = "http://localhost:5173"

    # AI
    ai_provider_api_key: str | None = None
    ai_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()