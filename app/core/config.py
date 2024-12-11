import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "default@example.com")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "recipient@example.com")

    URL_PROCESSOR_TIMEOUT = int(os.getenv("URL_PROCESSOR_TIMEOUT", 10))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))


settings = Settings()
