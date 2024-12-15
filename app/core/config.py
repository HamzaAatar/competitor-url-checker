import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # URL Processing
    URL_PROCESSOR_TIMEOUT = int(os.getenv("URL_PROCESSOR_TIMEOUT", 10))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))

    # Authentication
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://localhost/competitor_url_checker"
    )


settings = Settings()
