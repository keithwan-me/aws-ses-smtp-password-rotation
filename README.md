# AWS SES SMTP Password Rotation

Converts an AWS IAM secret access key into an Amazon SES SMTP password.

## How It Works

AWS SES requires a specially derived SMTP password generated from your IAM secret key using HMAC-SHA256. This script handles the derivation and optionally tests the SMTP connection.

## Prerequisites

- Python 3.6+
- AWS IAM credentials with SES send permissions

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your AWS credentials

## Usage

Generate SMTP password:
```bash
python main.py
```

Output: Your SMTP password for use with any SMTP client.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| AWS_SECRET_ACCESS_KEY | Yes | - | IAM secret access key |
| AWS_ACCESS_KEY_ID | For test | - | IAM access key ID |
| AWS_REGION | No | us-east-1 | AWS region |
| TEST_SMTP | No | false | Send test email |
| SENDER_EMAIL | For test | - | Verified sender address |
| RECIPIENT_EMAIL | For test | - | Test recipient address |

## Test SMTP Connection

Set `TEST_SMTP=true` and provide sender/recipient emails, then run the script:
```bash
python main.py
```
