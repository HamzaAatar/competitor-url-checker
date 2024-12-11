import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    URL_PROCESSOR_TIMEOUT = int(os.getenv("URL_PROCESSOR_TIMEOUT", 10))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))


settings = Settings()
