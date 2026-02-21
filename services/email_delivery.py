import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Only request permission to send email
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class EmailDeliveryService:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        # Load existing token if it exists
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If no valid token, run the OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for next time
            with open("token.json", "w") as f:
                f.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def send(self, to_email: str, subject: str, body: str) -> dict:
        message = MIMEText(body)
        message["to"] = to_email
        message["subject"] = subject

        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = self.service.users().messages().send(
            userId="me",
            body={"raw": encoded}
        ).execute()

        return {"message_id": result["id"], "status": "delivered"}