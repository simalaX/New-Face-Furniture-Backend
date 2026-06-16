from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./furniture.db"

    # ── Admin credentials ─────────────────────────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"

    # ── Secret key for signing session tokens ─────────────────────────────────
    # Generate a strong value with: python -c "import secrets; print(secrets.token_hex(32))"
    # Then add it to your .env file as: SECRET_KEY=<generated_value>
    SECRET_KEY: str = "change-this-to-a-random-secret-in-production"

    # ── Cloudinary ────────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()