#!/usr/bin/env python3
"""Entry point: send today's daily problems email."""

from dotenv import load_dotenv
load_dotenv()

import yaml
from pathlib import Path
from bot.problems import pick_problems
from bot.mailer import send_daily_problems

settings = yaml.safe_load((Path("config") / "settings.yaml").read_text())
n = settings.get("problems_per_day", 2)
problems = pick_problems(n)
send_daily_problems(problems)
