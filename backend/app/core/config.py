"""Centralized environment configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application
    app_name: str = "Intelligent Adaptive Study Planner"

    # Database
    database_url: str = "sqlite:///./study_planner.db"

    # JWT Authentication
    jwt_secret_key: str = "CHANGE_THIS_IN_ENV"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Email OTP Configuration
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender_email: str = ""
    smtp_use_tls: bool = True
    otp_expire_minutes: int = 5

    # Google Authentication
    google_client_id: str = ""
    google_client_secret: str = ""

    # Frontend
    frontend_origin: str = "http://localhost:5173"

    # AI Configuration
    ai_provider_api_key: str | None = None
    ai_model: str | None = None

    openai_api_key: str | None = None
    ai_model: str = "gpt-5.4"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()