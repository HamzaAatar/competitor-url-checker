from fastapi import FastAPI
from app.api import auth, endpoints, jobs
from app.core.database import async_engine, Base

app = FastAPI(title="Competitor URL Checker")


@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(endpoints.router, tags=["Endpoints"])
