import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_async_session
from app.services.job_service import create_job, get_job, update_job_status
from app.services.url_processor import URLProcessor
from app.schemas.job import JobCreate, JobResponse
from app.schemas.sheet_data import SheetData
from app.core.tasks import process_job_task

router = APIRouter()
url_processor = URLProcessor()


@router.post("/process-urls", response_model=JobResponse)
async def process_urls(
    sheet_data: SheetData, session: AsyncSession = Depends(get_async_session)
):
    # Create a job record
    job = await create_job(
        session, user_id=1, job_data=JobCreate(input_data=sheet_data.dict())
    )

    # Schedule background task
    asyncio.create_task(process_job_task(job.id))

    return job


@router.get("/job/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: int, session: AsyncSession = Depends(get_async_session)
):
    job = await get_job(session, job_id, user_id=1)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
