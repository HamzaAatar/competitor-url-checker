from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(title="Competitor URL Checker")
app.include_router(router)
