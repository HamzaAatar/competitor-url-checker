from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.sheet_data import SheetData
from app.services.url_processor import URLProcessor


router = APIRouter()
url_processor = URLProcessor()


@router.post("/check-urls")
async def process_sheet_data(sheet_data: SheetData):
    try:
        processed_data = []
        email_updates = []

        for row in sheet_data.data[1:]:  # Skip header row
            our_url = row[2]
            search_volume = row[1]
            processed_row = row.copy()

            # Original competitor last updated dates
            original_competitor_dates = [row[5], row[7], row[9]]

            # Our URL processing (unchanged)
            our_url_result = await url_processor.extract_last_updated(our_url)
            our_last_updated = (
                datetime.strptime(our_url_result["last_updated"], "%d %b %Y")
                if our_url_result["last_updated"]
                else None
            )

            processed_row[3] = (
                our_last_updated.strftime("%d %b %Y") if our_last_updated else "N/A"
            )

            # Competitor URLs with explicit handling for missing URLs
            competitor_urls_with_indices = [
                (row[4], 5),  # URL and its corresponding row index
                (row[6], 7),
                (row[8], 9),
            ]

            # Filter out empty URLs while preserving their original indices
            non_empty_competitor_urls = [
                (url, index) for (url, index) in competitor_urls_with_indices if url
            ]

            # Process only non-empty URLs
            competitor_results = await url_processor.process_urls(
                [url for (url, _) in non_empty_competitor_urls]
            )

            competitors_newer = 0
            for result, (original_url, original_row_index) in zip(
                competitor_results, non_empty_competitor_urls
            ):
                # Update only the specific column for the non-empty URL
                if result["last_updated"]:
                    processed_row[original_row_index] = result["last_updated"]
                else:
                    processed_row[original_row_index] = "N/A"

                # Check if the last updated date has changed from the original input
                original_date = original_competitor_dates[
                    non_empty_competitor_urls.index((original_url, original_row_index))
                ]

                # Existing newer competitor logic with date change check
                if our_last_updated and result["last_updated"]:
                    competitor_last_updated = datetime.strptime(
                        result["last_updated"], "%d %b %Y"
                    )
                    if competitor_last_updated > our_last_updated:
                        competitors_newer += 1
                        days_older = (competitor_last_updated - our_last_updated).days

                        # Only add to email updates if the date is different from the original
                        if result["last_updated"] != original_date:
                            email_updates.append(
                                {
                                    "competitor_url": result["url"],
                                    "search_volume": search_volume,
                                    "our_url": our_url,
                                    "our_page_date": our_last_updated.strftime(
                                        "%d %b %Y"
                                    )
                                    if our_last_updated
                                    else "N/A",
                                    "days_older": days_older,
                                }
                            )

            processed_row[10] = competitors_newer
            processed_data.append(processed_row)

        return {
            "processed_data": processed_data,
            "email_updates": email_updates,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
