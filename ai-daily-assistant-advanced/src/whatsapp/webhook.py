"""Flask webhook server for WhatsApp messages."""

from typing import List
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import structlog
import os

logger = structlog.get_logger()


def _split_message(text: str, max_length: int = 1600) -> List[str]:
    """Split long messages into chunks for WhatsApp.

    Args:
        text: Message text to split
        max_length: Maximum length per chunk (WhatsApp limit is 1600)

    Returns:
        List of message chunks
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current = ""
    for paragraph in text.split('\n\n'):
        if len(current) + len(paragraph) > max_length:
            if current:
                chunks.append(current)
            current = paragraph
        else:
            current += ('\n\n' + paragraph if current else paragraph)

    if current:
        chunks.append(current)

    return chunks


def create_whatsapp_app(handler) -> Flask:
    """Create Flask app for WhatsApp webhook.

    Args:
        handler: WhatsApp message handler

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Get Twilio credentials for validation
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    validator = RequestValidator(auth_token) if auth_token else None

    @app.route("/webhook/whatsapp", methods=["POST"])
    def whatsapp_webhook():
        """Handle incoming WhatsApp messages."""
        # Get message details
        from_number = request.form.get("From", "")
        message_body = request.form.get("Body", "").strip()

        logger.info("Webhook received",
                   from_number=from_number,
                   message_length=len(message_body))

        # Validate request is from Twilio (in production)
        if os.getenv("WHATSAPP_VERIFY_SIGNATURE", "false").lower() == "true":
            if not validate_twilio_request(request):
                logger.warning("Invalid Twilio signature")
                return "Unauthorized", 401

        # Handle empty messages
        if not message_body:
            resp = MessagingResponse()
            resp.message("Please send a message!")
            return str(resp)

        # Handle message
        try:
            response_text = handler.handle_message(from_number, message_body)
        except Exception as e:
            logger.error("Handler error", error=str(e))
            response_text = f"❌ Sorry, something went wrong: {str(e)}"

        # Create Twilio response
        resp = MessagingResponse()

        # Split long messages into chunks
        message_chunks = _split_message(response_text)
        for i, chunk in enumerate(message_chunks):
            if i < len(message_chunks) - 1:
                # Add continuation marker for all but last chunk
                resp.message(chunk + "\n\n_...continued_")
            else:
                resp.message(chunk)

        return str(resp)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "whatsapp-webhook"}, 200

    @app.route("/", methods=["GET"])
    def index():
        """Root endpoint."""
        return {
            "service": "AI Daily Assistant - WhatsApp",
            "status": "running",
            "endpoints": {
                "webhook": "/webhook/whatsapp",
                "health": "/health"
            }
        }, 200

    def validate_twilio_request(req) -> bool:
        """Validate request is from Twilio.

        Args:
            req: Flask request object

        Returns:
            True if valid, False otherwise
        """
        if not validator:
            return True  # Skip validation if no auth token

        url = request.url
        signature = req.headers.get("X-Twilio-Signature", "")
        params = req.form.to_dict()
        return validator.validate(url, params, signature)

    return app
