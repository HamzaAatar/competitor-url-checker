import logging
from typing import List, Dict, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import settings


class EmailSender:
    def __init__(
        self,
        api_key: str = settings.SENDGRID_API_KEY,
        sender_email: str = settings.SENDER_EMAIL,
        receiver_email: str = settings.RECEIVER_EMAIL,
    ):
        self.sendgrid_client = SendGridAPIClient(api_key)
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.logger = logging.getLogger(__name__)

    def send_updates_email(self, updates: List[Dict]) -> Optional[Dict]:
        try:
            email_body = "Competitor URL Updates:\n\n" + "\n".join(
                [
                    f"Competitor: www.{update['competitor_url']} "
                    f"(Volume: {update['search_volume']}) "
                    f"Your Page: www.{update['our_url']} "
                    f"({update['days_older']} days older)"
                    for update in updates
                ]
            )

            message = Mail(
                from_email=self.sender_email,
                to_emails=self.receiver_email,
                subject="Competitor URL Updates",
                plain_text_content=email_body,
            )

            response = self.sendgrid_client.send(message)
            return {
                "status": response.status_code,
                "message": "Email sent successfully",
            }
        except Exception as e:
            self.logger.error(f"Email sending error: {e}")
            return None
