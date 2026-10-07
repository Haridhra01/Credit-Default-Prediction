from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings.

    Values are loaded from the .env file.
    """

    # Application information
    PROJECT_NAME: str = "ExplainBI"
    PROJECT_VERSION: str = "1.0.0"

    # Security configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database configuration
    DATABASE_URL: str = "sqlite:///./explainbi.db"

    # Configuration for loading environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Create a single settings object for the application
settings = Settings()