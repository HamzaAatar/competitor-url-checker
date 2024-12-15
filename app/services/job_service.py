from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from app.schemas.job import JobCreate


async def create_job(session: AsyncSession, user_id: int, job_data: JobCreate):
    job = Job(user_id=user_id, input_data=job_data.input_data)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, job_id: int, user_id: int):
    result = await session.execute(
        select(Job).filter(Job.id == job_id, Job.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_job_status(
    session: AsyncSession, job_id: int, status: str, result: dict = None
):
    job = await session.get(Job, job_id)
    if job:
        job.status = status
        if result:
            job.result = result
        await session.commit()
        await session.refresh(job)
    return job
