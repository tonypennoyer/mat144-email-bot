# Setup Guide

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Gmail

1. Enable 2FA on your Google account.
2. Generate an **App Password** at myaccount.google.com → Security → App Passwords.
3. Copy `.env.example` to `.env` and fill in your Gmail address and app password.

## 3. Customize settings

Edit `config/settings.yaml` to set your name, email, and how many problems per day (max 2).

Edit `config/messages.yaml` to customize the feedback messages for correct and incorrect answers.

## 4. Send the daily email

```bash
python send_daily.py
```

## 5. Grade a response

When you reply to the daily email, run:

```bash
python grade_reply.py
```

(See `grade_reply.py` for how to pipe in a raw email body.)

## 6. Schedule daily sends (macOS)

Use `cron` or `launchd` to run `send_daily.py` every morning:

```cron
0 8 * * * cd /path/to/mat144_email_bot && python send_daily.py
```
