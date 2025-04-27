import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import smtplib
from email.mime.text import MIMEText

class EmailInput(BaseModel):
    recipient: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")

class EmailSender(BaseTool):
    name: str = "Email Sender"
    description: str = "Send an email to the user"

    args_schema: Type[BaseModel] = EmailInput

    def _run(self, recipient: str, subject: str, body: str) -> str:
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = os.getenv("EMAIL_FROM")
            msg['To'] = recipient

            with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
                server.starttls()
                server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
                server.send_message(msg)

            return f"Email sent successfully to {recipient}"

        except Exception as e:
            return f"Error sending email: {str(e)}"
