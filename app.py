import os
import hmac
import hashlib
import requests

from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
APP_SECRET = os.getenv("APP_SECRET", "")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "")


@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Support Bot is running!"


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


def verify_signature(payload, signature):
    if not APP_SECRET:
        return False

    expected = "sha256=" + hmac.new(
        APP_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature or "")


def get_reply(message):
    text = message.strip().lower()

    menu = (
        f"Welcome to {os.getenv('BUSINESS_NAME', 'our business')}!\n\n"
        "How can we help you?\n\n"
        "1. Products and services\n"
        "2. Order enquiries\n"
        "3. Delivery information\n"
        "4. Payment information\n"
        "5. Business hours\n"
        "6. Speak to an agent\n\n"
        "Reply with a number to continue."
    )

    if text in ["hi", "hello", "hey", "start", "menu", "help"]:
        return menu

    if text == "1":
        return os.getenv(
            "PRODUCT_INFO",
            "Please contact us for product information."
        )

    if text == "2":
        return "Please provide your order number so we can assist you."

    if text == "3":
        return os.getenv(
            "DELIVERY_INFO",
            "Please contact us for delivery information."
        )

    if text == "4":
        return os.getenv(
            "PAYMENT_INFO",
            "Please contact us for payment information."
        )

    if text == "5":
        return os.getenv(
            "BUSINESS_HOURS",
            "Please contact us for business hours."
        )

    if text == "6":
        return (
            "Please contact our support team at "
            + os.getenv("BUSINESS_PHONE", "our business phone number")
        )

    return "Sorry, I didn't understand that.\n\n" + menu


def send_whatsapp_message(to, message):
    if not all([
        WHATSAPP_TOKEN,
        PHONE_NUMBER_ID,
        GRAPH_API_VERSION
    ]):
        print("WhatsApp API environment variables are missing.")
        return

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )
        response.raise_for_status()
        print("Message sent successfully.")

    except requests.RequestException as error:
        print("WhatsApp API error:", error)


@app.route("/webhook", methods=["POST"])
def receive_message():
    if APP_SECRET:
        signature = request.headers.get(
            "X-Hub-Signature-256", ""
        )

        if not verify_signature(request.get_data(), signature):
            return "Invalid signature", 403

    data = request.get_json(silent=True) or {}

    try:
        entries = data.get("entry", [])

        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for message in value.get("messages", []):
                    sender = message.get("from")
                    message_type = message.get("type")

                    if message_type == "text" and sender:
                        incoming = message["text"].get("body", "")
                        reply = get_reply(incoming)

                        send_whatsapp_message(sender, reply)

    except (KeyError, TypeError, AttributeError) as error:
        print("Webhook processing error:", error)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
