from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.sheet_data import SheetData
from app.services.url_processor import URLProcessor

import time

router = APIRouter()
url_processor = URLProcessor()


@router.post("/check-urls")
async def process_sheet_data(sheet_data: SheetData):
    try:
        start_time = time.time()
        processed_data = []
        email_updates = []

        for row in sheet_data.data[1:]:  # Skip header row
            our_url = row[2]
            search_volume = row[1]

            # Dynamically get our last updated time
            our_url_result = await url_processor.extract_last_updated(our_url)
            our_last_updated = (
                datetime.strptime(our_url_result["last_updated"], "%d %b %Y")
                if our_url_result["last_updated"]
                else None
            )

            if not our_last_updated:
                continue  # Skip if we can't determine our URL's last updated time

            competitor_urls = [url for url in [row[4], row[6], row[8]] if url]
            competitor_results = await url_processor.process_urls(competitor_urls)

            competitors_newer = 0
            for result, original_row_index in zip(competitor_results, [5, 7, 9]):
                if result["last_updated"]:
                    competitor_last_updated = datetime.strptime(
                        result["last_updated"], "%d %b %Y"
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
            processed_row[3] = our_last_updated.strftime("%d %b %Y")

            # Update competitor last updated dates
            for i, result in zip([5, 7, 9], competitor_results):
                if result["last_updated"]:
                    processed_row[i] = result["last_updated"]

            processed_row[10] = competitors_newer
            processed_data.append(processed_row)

        process_time = time.time() - start_time
        return {
            "process_time": process_time,
            "processed_data": processed_data,
            "email_updates": email_updates,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
