from app.core.database import AsyncSessionLocal
from app.services.url_processor import URLProcessor
from app.services.job_service import update_job_status
from app.models.job import Job
from datetime import datetime

url_processor = URLProcessor()


async def process_job_task(job_id: int):
    async with AsyncSessionLocal() as session:
        try:
            # Retrieve job
            job = await session.get(Job, job_id)

            # Process URLs
            processed_data = []
            for row in job.input_data["data"][1:]:
                our_url = row[2]
                our_url_result = await url_processor.extract_last_updated(our_url)

                # Additional processing similar to previous implementation

                processed_data.append(row)

            # Update job with results
            await update_job_status(
                session, job_id, "completed", {"processed_data": processed_data}
            )

        except Exception as e:
            await update_job_status(session, job_id, "failed", {"error": str(e)})
