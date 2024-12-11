import asyncio
from app.services.url_processor import URLProcessor

# Sample data mimicking Google Sheets input
SAMPLE_SHEET_DATA = [
    # Header row
    [
        "Keyword",
        "Search Volume",
        "Our URL",
        "Our Last Updated",
        "Competitor 1 URL",
        "Competitor 1 Last Updated",
        "Competitor 2 URL",
        "Competitor 2 Last Updated",
        "Competitor 3 URL",
        "Competitor 3 Last Updated",
        "Competitors Newer",
    ],
    # Data row
    [
        "keyword1",
        "5000",
        "https://www.whatcar.com/lexus/nx/estate/review/n132",
        "2024-01-01T00:00:00",
        "https://www.autoexpress.co.uk/lexus/nx",
        "2024-01-02T00:00:00",
        "https://www.autocar.co.uk/car-review/lexus/nx",
        "2024-01-03T00:00:00",
        "https://www.topgear.com/car-reviews/lexus/nx",
        "2024-01-04T00:00:00",
        0,
    ],
]


async def main():
    # Initialize services
    url_processor = URLProcessor()

    # Process data starting from the second row (skipping headers)
    for row in SAMPLE_SHEET_DATA[1:]:
        our_url = row[2]

        # Collect competitor URLs
        competitor_urls = [row[4], row[6], row[8]]
        competitor_urls = [url for url in competitor_urls if url]

        print(f"\nProcessing URLs for {our_url}")

        # Process URLs concurrently
        results = await url_processor.process_urls(competitor_urls)

        # Analyze results
        for result in results:
            print(f"URL: {result['url']}")
            print(f"Last Updated: {result['last_updated']}")
            print(f"Errors: {result.get('error', 'None')}")

        # Simulate email sending (optional)
        email_updates = []
        # Add logic to create email updates based on results

        if email_updates:
            print("Email result:", email_updates)


if __name__ == "__main__":
    asyncio.run(main())
