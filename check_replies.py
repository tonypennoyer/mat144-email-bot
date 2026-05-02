#!/usr/bin/env python3
"""Check Gmail for a reply to today's problems and send graded results."""

from dotenv import load_dotenv
load_dotenv()

from bot.mailer import check_and_grade

try:
    check_and_grade()
except FileNotFoundError as e:
    print(f"Skipping: {e}")
