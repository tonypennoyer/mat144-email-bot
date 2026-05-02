"""Email sending and grading via Gmail SMTP/IMAP."""

import email
import email.utils
import imaplib
import json
import os
import random
import smtplib
import yaml
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from bot.problems import Problem, grade_answer

CONFIG_DIR = Path(__file__).parent.parent / "config"
DATA_DIR = Path(__file__).parent.parent / "data"
PROBLEMS_FILE = DATA_DIR / "current_problems.json"


def _load_settings() -> dict:
    with open(CONFIG_DIR / "settings.yaml") as f:
        return yaml.safe_load(f)


def _load_messages() -> dict:
    with open(CONFIG_DIR / "messages.yaml") as f:
        return yaml.safe_load(f)


def _smtp_connection():
    address = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(address, password)
    return server, address


def _save_state(problems: list, message_id: str) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    payload = {
        "date": str(date.today()),
        "message_id": message_id,
        "graded": False,
        "problems": [
            {
                "question": p.question,
                "answer": p.answer,
                "hint": p.hint,
                "solution": p.solution,
            }
            for p in problems
        ],
    }
    PROBLEMS_FILE.write_text(json.dumps(payload, indent=2))


def _load_state() -> dict:
    if not PROBLEMS_FILE.exists():
        raise FileNotFoundError("No problems file found. Run send_daily.py first.")
    return json.loads(PROBLEMS_FILE.read_text())


def send_daily_problems(problems: list) -> None:
    """Send the daily problem email and save problems + Message-ID locally."""
    settings = _load_settings()
    messages = _load_messages()
    recipient = settings["recipient"]

    message_id = email.utils.make_msgid(domain="gmail.com")

    body_lines = [
        f"Hi {recipient['name']},\n",
        "Here are your discrete math problems for today. Reply with just "
        "your numeric answers, one per line, in order.\n",
    ]
    for i, p in enumerate(problems, 1):
        body_lines.append(f"Problem {i}: {p.question}")
    body_lines.append("\nReply to this email with your answers and we'll grade them!")

    msg = MIMEMultipart("alternative")
    msg["Message-ID"] = message_id
    msg["Subject"] = messages["subjects"]["daily_problem"]
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = recipient["email"]
    msg.attach(MIMEText("\n".join(body_lines), "plain"))

    server, address = _smtp_connection()
    server.sendmail(address, recipient["email"], msg.as_string())
    server.quit()

    _save_state(problems, message_id)
    print(f"Daily problems sent to {recipient['email']}")


def _fetch_reply_answers():
    """Check Gmail inbox via IMAP for a reply to today's problem email.
    Returns a list of answer strings, or None if no ungraded reply found.
    """
    state = _load_state()
    if state.get("graded"):
        print("Today's problems have already been graded.")
        return None

    messages = _load_messages()
    subject = messages["subjects"]["daily_problem"]
    address = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(address, password)
    mail.select("inbox")

    today = date.today().strftime("%d-%b-%Y")
    _, data = mail.search(None, f'(SINCE "{today}" SUBJECT "Re: {subject}")')
    ids = data[0].split()

    if not ids:
        mail.logout()
        return None

    _, msg_data = mail.fetch(ids[-1], "(RFC822)")
    mail.logout()

    raw_msg = email.message_from_bytes(msg_data[0][1])
    body = ""
    if raw_msg.is_multipart():
        for part in raw_msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="replace")
                break
    else:
        body = raw_msg.get_payload(decode=True).decode(errors="replace")

    # Collect answer lines, stopping at quoted text
    answers = []
    for line in body.splitlines():
        line = line.strip()
        if line.startswith(">") or line.lower().startswith("on "):
            break
        if line:
            answers.append(line)

    return answers if answers else None


def check_and_grade() -> None:
    """Check for a reply, grade it, and send feedback as a thread reply."""
    settings = _load_settings()
    messages = _load_messages()
    recipient = settings["recipient"]
    name = recipient["name"]

    print("Checking inbox for reply...")
    user_answers = _fetch_reply_answers()
    if user_answers is None:
        return

    state = _load_state()
    problems_data = state["problems"]
    original_message_id = state["message_id"]

    result_lines = [f"Hi {name}, here are your results:\n"]

    for i, (pdata, user_ans) in enumerate(zip(problems_data, user_answers), 1):
        problem = Problem(
            question=pdata["question"],
            answer=pdata["answer"],
            hint=pdata["hint"],
            solution=pdata["solution"],
        )
        correct = grade_answer(problem, user_ans)
        if correct:
            template = random.choice(messages["correct"])
            result_lines.append(f"Problem {i}: " + template.format(name=name))
        else:
            template = random.choice(messages["incorrect"])
            result_lines.append(
                f"Problem {i}: "
                + template.format(
                    name=name,
                    your_answer=user_ans,
                    answer=problem.answer,
                    hint=problem.hint,
                )
            )
            result_lines.append(f"\nWhy? {problem.solution}\n")

    subject = f"Re: {messages['subjects']['daily_problem']}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = recipient["email"]
    msg["In-Reply-To"] = original_message_id
    msg["References"] = original_message_id
    msg.attach(MIMEText("\n".join(result_lines), "plain"))

    server, address = _smtp_connection()
    server.sendmail(address, recipient["email"], msg.as_string())
    server.quit()

    # Mark graded so repeat polls don't re-send
    state["graded"] = True
    PROBLEMS_FILE.write_text(json.dumps(state, indent=2))
    print(f"Grade results sent to {recipient['email']}")
