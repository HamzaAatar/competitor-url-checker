import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    URL_PROCESSOR_TIMEOUT = int(os.getenv("URL_PROCESSOR_TIMEOUT", 10))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))
    REDIS_CLOUD_HOST = os.getenv("REDIS_CLOUD_HOST")
    REDIS_CLOUD_PORT = os.getenv("REDIS_CLOUD_PORT", 12345)
    REDIS_CLOUD_PASSWORD = os.getenv("REDIS_CLOUD_PASSWORD")


settings = Settings()
