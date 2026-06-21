import logging
import hashlib
import hmac
from typing import Optional
import httpx

from jarvis.connectors.base import ConnectorBase, ConnectorAuth, ConnectorResponse

logger = logging.getLogger("jarvis.connector.whatsapp")


class WhatsAppConnector(ConnectorBase):

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        super().__init__(config, auth)
        self._http_client = None
        self._api_base = "https://graph.facebook.com/v18.0"
        self._phone_number_id = None
        self._access_token = None
        self._webhook_verify_token = None

    async def initialize(self) -> bool:
        try:
            creds = self.auth.credentials if self.auth else {}
            self._phone_number_id = creds.get("phone_number_id") or self.config.get("phone_number_id")
            self._access_token = creds.get("access_token") or self.config.get("access_token")
            self._webhook_verify_token = self.config.get("webhook_verify_token", "jarvis_verify_token")

            if not self._access_token or not self._phone_number_id:
                logger.error("WhatsApp credentials incomplete")
                return False

            self._http_client = httpx.AsyncClient(
                base_url=self._api_base,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            logger.info("WhatsApp connector initialized for phone: %s", self._phone_number_id)
            return True

        except Exception as e:
            logger.error("WhatsApp initialization failed: %s", e)
            return False

    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        if not self._http_client:
            success = await self.initialize()
            if not success:
                return ConnectorResponse(success=False, error="WhatsApp not initialized")

        try:
            action_map = {
                "send_text": self._send_text,
                "send_template": self._send_template,
                "send_image": self._send_image,
                "send_document": self._send_document,
                "send_button": self._send_button,
                "mark_as_read": self._mark_as_read,
                "get_messages": self._get_messages,
                "verify_webhook": self._verify_webhook,
            }

            handler = action_map.get(action)
            if not handler:
                return ConnectorResponse(success=False, error=f"Unknown WhatsApp action: {action}")

            result = await handler(params)
            return ConnectorResponse(success=True, data=result)

        except Exception as e:
            logger.error("WhatsApp action '%s' failed: %s", action, e)
            return ConnectorResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        try:
            if not self._http_client:
                return False
            resp = await self._http_client.get(f"/{self._phone_number_id}/messages")
            return resp.status_code < 500
        except Exception:
            return False

    async def close(self) -> None:
        if self._http_client:
            await self._http_client.aclose()

    async def _send_text(self, params: dict) -> dict:
        to = params.get("to")
        text = params.get("text")
        preview_url = params.get("preview_url", False)

        if not to or not text:
            raise ValueError("'to' and 'text' required")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": preview_url, "body": text},
        }

        resp = await self._http_client.post(
            f"/{self._phone_number_id}/messages",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    async def _send_template(self, params: dict) -> dict:
        to = params.get("to")
        template_name = params.get("template_name")
        language = params.get("language", "en")
        components = params.get("components", [])

        if not to or not template_name:
            raise ValueError("'to' and 'template_name' required")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components,
            },
        }

        resp = await self._http_client.post(
            f"/{self._phone_number_id}/messages",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    async def _send_image(self, params: dict) -> dict:
        to = params.get("to")
        image_url = params.get("image_url")
        image_id = params.get("image_id")
        caption = params.get("caption")

        if not to or not (image_url or image_id):
            raise ValueError("'to' and 'image_url' or 'image_id' required")

        media = {}
        if image_url:
            media["link"] = image_url
        if image_id:
            media["id"] = image_id
        if caption:
            media["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": media,
        }

        resp = await self._http_client.post(
            f"/{self._phone_number_id}/messages",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    async def _send_document(self, params: dict) -> dict:
        to = params.get("to")
        doc_url = params.get("document_url")
        doc_id = params.get("document_id")
        filename = params.get("filename")
        caption = params.get("caption")

        if not to or not (doc_url or doc_id):
            raise ValueError("'to' and 'document_url' or 'document_id' required")

        media = {}
        if doc_url:
            media["link"] = doc_url
        if doc_id:
            media["id"] = doc_id
        if filename:
            media["filename"] = filename
        if caption:
            media["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "document",
            "document": media,
        }

        resp = await self._http_client.post(
            f"/{self._phone_number_id}/messages",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    async def _send_button(self, params: dict) -> dict:
        to = params.get("to")
        text = params.get("text")
        buttons = params.get("buttons", [])

        if not to or not text or not buttons:
            raise ValueError("'to', 'text', and 'buttons' required")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {"buttons": buttons},
            },
        }

        resp = await self._http_client.post(
            f"/{self._phone_number_id}/messages",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    async def _mark_as_read(self, params: dict) -> dict:
        message_id = params.get("message_id")
        if not message_id:
            raise ValueError("message_id required")

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        resp = await self._http_client.post(
            f"/{self._phone_number_id}/messages",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    async def _get_messages(self, params: dict) -> dict:
        return {"note": "WhatsApp webhook receives messages; query message history from DB"}

    async def _verify_webhook(self, params: dict) -> bool:
        mode = params.get("hub_mode")
        token = params.get("hub_verify_token")
        challenge = params.get("hub_challenge")

        if mode == "subscribe" and token == self._webhook_verify_token:
            logger.info("WhatsApp webhook verified")
            return challenge

        logger.warning("WhatsApp webhook verification failed")
        raise ValueError("Verification failed")

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        app_secret = self.config.get("app_secret", "")
        expected = hmac.new(
            app_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
