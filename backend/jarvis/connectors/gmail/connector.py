import logging
import base64
from email.mime.text import MIMEText
from typing import Optional

from jarvis.connectors.base import ConnectorBase, ConnectorAuth, ConnectorResponse

logger = logging.getLogger("jarvis.connector.gmail")


class GmailConnector(ConnectorBase):

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        super().__init__(config, auth)
        self._service = None

    async def initialize(self) -> bool:
        try:
            creds = self.auth.credentials if self.auth else {}
            token_path = creds.get("token_path") or self.config.get("token_path")
            credentials_path = creds.get("credentials_path") or self.config.get("credentials_path")

            if not credentials_path:
                logger.warning("Gmail credentials not configured, using mock")
                return True

            try:
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request
                from googleapiclient.discovery import build

                SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
                creds_obj = None

                if token_path:
                    import json
                    with open(token_path) as f:
                        token_data = json.load(f)
                    creds_obj = Credentials.from_authorized_user_info(token_data, SCOPES)

                if not creds_obj or not creds_obj.valid:
                    if creds_obj and creds_obj.expired and creds_obj.refresh_token:
                        creds_obj.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                        creds_obj = flow.run_local_server(port=0)

                    if token_path:
                        with open(token_path, "w") as f:
                            f.write(creds_obj.to_json())

                self._service = build("gmail", "v1", credentials=creds_obj)
                logger.info("Gmail connector initialized")
                return True

            except ImportError:
                logger.warning("google client libraries not installed, using mock")
                return True

        except Exception as e:
            logger.error("Gmail initialization failed: %s", e)
            return False

    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        try:
            action_map = {
                "send_email": self._send_email,
                "list_messages": self._list_messages,
                "get_message": self._get_message,
                "search_messages": self._search_messages,
                "create_draft": self._create_draft,
                "mark_as_read": self._mark_as_read,
                "trash_message": self._trash_message,
                "list_labels": self._list_labels,
            }

            handler = action_map.get(action)
            if not handler:
                return ConnectorResponse(success=False, error=f"Unknown Gmail action: {action}")

            result = await handler(params)
            return ConnectorResponse(success=True, data=result)

        except Exception as e:
            logger.error("Gmail action '%s' failed: %s", action, e)
            return ConnectorResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        self._service = None

    async def _send_email(self, params: dict) -> dict:
        to = params.get("to", [])
        if isinstance(to, str):
            to = [to]
        cc = params.get("cc", [])
        bcc = params.get("bcc", [])
        subject = params.get("subject", "")
        body = params.get("body", "")
        body_type = params.get("body_type", "plain")

        message = MIMEText(body, body_type)
        message["To"] = ", ".join(to)
        message["Cc"] = ", ".join(cc) if cc else ""
        message["Subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        if not self._service:
            return {"message_id": f"mock_{subject[:20]}", "status": "mock_sent"}

        sent = self._service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"message_id": sent.get("id"), "thread_id": sent.get("threadId")}

    async def _list_messages(self, params: dict) -> list:
        max_results = params.get("max_results", 20)
        label_ids = params.get("label_ids", ["INBOX"])

        if not self._service:
            return [{"id": "mock_msg_1", "subject": "Mock Email"}] * min(max_results, 5)

        result = self._service.users().messages().list(
            userId="me", maxResults=max_results, labelIds=label_ids
        ).execute()
        return result.get("messages", [])

    async def _get_message(self, params: dict) -> dict:
        message_id = params.get("message_id")
        if not message_id:
            raise ValueError("message_id required")

        if not self._service:
            return {"id": message_id, "snippet": "Mock email content"}

        msg = self._service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()
        return msg

    async def _search_messages(self, params: dict) -> list:
        query = params.get("query", "")
        max_results = params.get("max_results", 20)

        if not self._service:
            return [{"id": "mock_search_1"}] * min(max_results, 5)

        result = self._service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        return result.get("messages", [])

    async def _create_draft(self, params: dict) -> dict:
        to = params.get("to", [])
        subject = params.get("subject", "")
        body = params.get("body", "")

        message = MIMEText(body)
        message["To"] = ", ".join(to) if isinstance(to, list) else to
        message["Subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        if not self._service:
            return {"draft_id": f"mock_draft_{subject[:20]}"}

        draft = self._service.users().drafts().create(
            userId="me", body={"message": {"raw": raw}}
        ).execute()
        return {"draft_id": draft.get("id")}

    async def _mark_as_read(self, params: dict) -> dict:
        message_id = params.get("message_id")
        if not message_id:
            raise ValueError("message_id required")

        if not self._service:
            return {"status": "mock_read"}

        self._service.users().messages().modify(
            userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return {"status": "marked_read"}

    async def _trash_message(self, params: dict) -> dict:
        message_id = params.get("message_id")
        if not message_id:
            raise ValueError("message_id required")

        if not self._service:
            return {"status": "mock_trashed"}

        self._service.users().messages().trash(userId="me", id=message_id).execute()
        return {"status": "trashed"}

    async def _list_labels(self, params: dict) -> list:
        if not self._service:
            return [{"id": "MOCK", "name": "Mock Label"}]

        result = self._service.users().labels().list(userId="me").execute()
        return result.get("labels", [])
