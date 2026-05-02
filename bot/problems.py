"""Combinatorics problem bank with grading logic."""

import random
from dataclasses import dataclass


@dataclass
class Problem:
    question: str
    answer: int | str
    hint: str
    topic: str = "combinatorics"


COMBINATORICS_PROBLEMS = [
    Problem(
        question=(
            "In how many ways can you arrange the letters in the word MATH?"
        ),
        answer=24,
        hint="Use the factorial formula: n! for n distinct items.",
    ),
    Problem(
        question=(
            "A committee of 3 is chosen from 7 people. How many different "
            "committees are possible?"
        ),
        answer=35,
        hint="Use combinations: C(7,3) = 7! / (3! * 4!).",
    ),
    Problem(
        question=(
            "How many 3-digit PIN codes can be made from digits 1–9 if "
            "repetition is not allowed?"
        ),
        answer=504,
        hint="Use permutations: P(9,3) = 9 * 8 * 7.",
    ),
    Problem(
        question=(
            "A pizza shop offers 5 toppings. How many different 2-topping "
            "pizzas can be made?"
        ),
        answer=10,
        hint="Use combinations: C(5,2) = 5! / (2! * 3!).",
    ),
    Problem(
        question=(
            "How many ways can 4 students sit in a row of 4 chairs?"
        ),
        answer=24,
        hint="Use the factorial formula: 4! = 4 * 3 * 2 * 1.",
    ),
    Problem(
        question=(
            "From a deck of 52 cards, how many 5-card hands are possible?"
        ),
        answer=2598960,
        hint="Use combinations: C(52,5) = 52! / (5! * 47!).",
    ),
    Problem(
        question=(
            "How many ways can you choose 2 books from a shelf of 8?"
        ),
        answer=28,
        hint="Use combinations: C(8,2) = 8! / (2! * 6!).",
    ),
    Problem(
        question=(
            "In how many ways can 6 people be seated at a circular table?"
        ),
        answer=120,
        hint="Circular permutations: (n-1)! = 5!.",
    ),
]


def pick_problems(n: int = 2) -> list[Problem]:
    """Return n randomly selected problems."""
    return random.sample(COMBINATORICS_PROBLEMS, min(n, len(COMBINATORICS_PROBLEMS)))


def grade_answer(problem: Problem, user_answer: str) -> bool:
    """Return True if user_answer matches the expected answer."""
    try:
        return int(user_answer.strip()) == int(problem.answer)
    except (ValueError, AttributeError):
        return str(user_answer).strip().lower() == str(problem.answer).strip().lower()
