import sys
import os
from pathlib import Path
import smtplib
import ssl
from email.message import EmailMessage
import hmac
import hashlib
import base64

def load_env(filepath: str = ".env") -> None:
    dotenv_path = Path(filepath)
    if not dotenv_path.is_file():
        return
    with dotenv_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            val = val.strip().strip("'\"")
            os.environ.setdefault(key.strip(), val)

load_env()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TEST_SMTP = os.getenv("TEST_SMTP", "false").lower() == "true"
SMTP_HOST = f"email-smtp.{AWS_REGION}.amazonaws.com"
SMTP_PORT = 587
SENDER = os.getenv("SENDER_EMAIL")
RECIPIENT = os.getenv("RECIPIENT_EMAIL")

def convert_secret_key_to_smtp_password(secret_key: str, region: str = "us-east-1") -> str:
    # AWS Hardcoded Constant
    date = "11111111"
    service = "ses"
    terminal = "aws4_request"
    message = "SendRawEmail"
    version = 0x04

    signature = hmac.new(("AWS4" + secret_key).encode("utf-8"), date.encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(signature, region.encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(signature, service.encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(signature, terminal.encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(signature, message.encode("utf-8"), hashlib.sha256).digest()

    signature_and_version = bytes([version]) + signature
    return base64.b64encode(signature_and_version).decode("utf-8")

def send_test_email(smtp_host: str, smtp_port: int, smtp_username: str, smtp_password: str, sender: str, recipient: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = "SES SMTP Test"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("Testing SES SMTP.")

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        server.set_debuglevel(1)
        server.starttls(context=context)
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

def main() -> None:
    if not AWS_SECRET_ACCESS_KEY:
        raise ValueError("AWS_SECRET_ACCESS_KEY is not set in the environment variables.")
    SMTP_PASSWORD = convert_secret_key_to_smtp_password(AWS_SECRET_ACCESS_KEY, AWS_REGION)
    print(f"SMTP Password: {SMTP_PASSWORD}")
    if TEST_SMTP:
        if not AWS_ACCESS_KEY_ID or not SENDER or not RECIPIENT:
            raise ValueError("AWS_ACCESS_KEY_ID, SENDER_EMAIL and RECIPIENT_EMAIL must be set in the environment variables for testing SMTP.")
        send_test_email(SMTP_HOST, SMTP_PORT, AWS_ACCESS_KEY_ID, SMTP_PASSWORD, SENDER, RECIPIENT)
        print("Email sent successfully!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    sys.exit(0)