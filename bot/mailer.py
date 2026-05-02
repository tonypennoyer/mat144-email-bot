"""Email sending and grading via Gmail SMTP."""

import os
import random
import smtplib
import json
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from bot.problems import Problem, grade_answer

CONFIG_DIR = Path(__file__).parent.parent / "config"


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


def send_daily_problems(problems: list[Problem]) -> None:
    """Send the daily problem email."""
    settings = _load_settings()
    messages = _load_messages()
    recipient = settings["recipient"]

    body_lines = [
        f"Hi {recipient['name']},\n",
        "Here are your discrete math problems for today. Reply with just "
        "your numeric answers, one per line, in order.\n",
    ]
    for i, p in enumerate(problems, 1):
        body_lines.append(f"Problem {i}: {p.question}")

    body_lines.append(
        "\nReply to this email with your answers and we'll grade them!"
    )

    # Embed problem data as hidden JSON so the grader can parse it later.
    payload = json.dumps([
        {"question": p.question, "answer": p.answer, "hint": p.hint}
        for p in problems
    ])
    body_lines.append(f"\n<!-- problems:{payload} -->")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = messages["subjects"]["daily_problem"]
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = recipient["email"]
    msg.attach(MIMEText("\n".join(body_lines), "plain"))

    server, address = _smtp_connection()
    server.sendmail(address, recipient["email"], msg.as_string())
    server.quit()
    print(f"Daily problems sent to {recipient['email']}")


def grade_and_reply(raw_email_body: str, user_answers: list[str]) -> None:
    """Parse embedded problem data, grade answers, and send result email."""
    import re

    settings = _load_settings()
    messages = _load_messages()
    recipient = settings["recipient"]
    name = recipient["name"]

    match = re.search(r"<!-- problems:(.+?) -->", raw_email_body, re.DOTALL)
    if not match:
        print("Could not find problem data in email body.")
        return

    problems_data = json.loads(match.group(1))
    result_lines = [f"Hi {name}, here are your results:\n"]

    for i, (pdata, user_ans) in enumerate(zip(problems_data, user_answers), 1):
        problem = Problem(
            question=pdata["question"],
            answer=pdata["answer"],
            hint=pdata["hint"],
        )
        correct = grade_answer(problem, user_ans)
        if correct:
            template = random.choice(messages["correct"])
            feedback = template.format(name=name)
        else:
            template = random.choice(messages["incorrect"])
            feedback = template.format(
                name=name, answer=problem.answer, hint=problem.hint
            )
        result_lines.append(f"Problem {i}: {feedback}")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = messages["subjects"]["grade_response"]
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = recipient["email"]
    msg.attach(MIMEText("\n".join(result_lines), "plain"))

    server, address = _smtp_connection()
    server.sendmail(address, recipient["email"], msg.as_string())
    server.quit()
    print(f"Grade results sent to {recipient['email']}")
