from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.sheet_data import SheetData
from app.services.url_processor import URLProcessor
from app.services.email_sender import EmailSender
from app.core.config import settings

router = APIRouter()
url_processor = URLProcessor()
email_sender = EmailSender()


@router.post("/check-urls")
async def process_sheet_data(sheet_data: SheetData):
    try:
        processed_data = []
        email_updates = []

        for row in sheet_data.data[1:]:  # Skip header row
            our_url = row[2]
            our_last_updated = datetime.fromisoformat(row[3])
            search_volume = row[1]

            competitor_urls = [url for url in [row[4], row[6], row[8]] if url]

            competitor_results = await url_processor.process_urls(competitor_urls)

            competitors_newer = 0
            for result in competitor_results:
                if result["last_updated"]:
                    competitor_last_updated = datetime.fromisoformat(
                        result["last_updated"]
                    )
                    if competitor_last_updated > our_last_updated:
                        competitors_newer += 1
                        days_older = (competitor_last_updated - our_last_updated).days

                        email_updates.append(
                            {
                                "competitor_url": result["url"],
                                "search_volume": search_volume,
                                "our_url": our_url,
                                "days_older": days_older,
                            }
                        )

            processed_row = row.copy()
            processed_row[10] = competitors_newer
            processed_data.append(processed_row)

        if email_updates:
            email_result = email_sender.send_updates_email(email_updates)

        return {"processed_data": processed_data, "email_sent": bool(email_updates)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
