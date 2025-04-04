import re
import json
import requests
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load keyword-to-intent map
with open("keywords.json", "r", encoding="utf-8") as file:
    KEYWORDS_LIST = json.load(file)

# Convert list format into dict format
KEYWORDS = {}
for entry in KEYWORDS_LIST:
    for intent, keywords in entry.items():
        KEYWORDS[intent] = keywords

# Telegram bot credentials from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Email credentials and settings from .env
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def extract_name(text):
    match = re.search(r"Заявник:\s*(.+?)\s*-", text)
    return match.group(1) if match else "[Unknown Name]"

def detect_intent(body):
    body = body.lower()
    for intent, keywords in KEYWORDS.items():
        if any(word.lower() in body for word in keywords):
            return intent
    return "Too messy to classify. Check manually."

def parse_email(subject, body):
    name = extract_name(body)
    intent = detect_intent(body)
    return {
        "subject": subject.strip(),
        "name": name.strip(),
        "intent": intent.strip()
    }

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    return response.status_code == 200

def fetch_and_process_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, f'(UNSEEN FROM "{SENDER_EMAIL}")')
    email_ids = messages[0].split()

    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Decode subject
        raw_subject = decode_header(msg["Subject"])[0]
        subject = raw_subject[0]
        if isinstance(subject, bytes):
            subject = subject.decode(raw_subject[1] if raw_subject[1] else "utf-8")

        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" and part.get("Content-Disposition") is None:
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        result = parse_email(subject, body)
        message = f"\U0001F4BE Subject: {result['subject']}\n\U0001F464 Name: {result['name']}\n\U0001F4CC Intent: {result['intent']}"

        if send_to_telegram(message):
            print("Telegram message sent successfully.")
        else:
            print("Failed to send Telegram message.")

        mail.store(e_id, '+FLAGS', '\\Seen')  # Mark email as read

    mail.logout()

# Run the real inbox connection
if __name__ == "__main__":
    fetch_and_process_emails()
