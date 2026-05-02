"""Combinatorics problem bank with grading logic."""

import random
from dataclasses import dataclass
from typing import Union


@dataclass
class Problem:
    question: str
    answer: Union[int, str]
    hint: str
    solution: str
    topic: str = "combinatorics"


COMBINATORICS_PROBLEMS = [
    Problem(
        question="In how many ways can you arrange the letters in the word MATH?",
        answer=24,
        hint="Use the factorial formula: n! for n distinct items.",
        solution=(
            "There are 4 distinct letters, so we arrange all 4 of them.\n"
            "Number of arrangements = 4! = 4 × 3 × 2 × 1 = 24."
        ),
    ),
    Problem(
        question=(
            "A committee of 3 is chosen from 7 people. "
            "How many different committees are possible?"
        ),
        answer=35,
        hint="Use combinations: C(7,3) = 7! / (3! × 4!).",
        solution=(
            "Order doesn't matter (a committee is a committee), so use combinations.\n"
            "C(7,3) = 7! / (3! × 4!) = 5040 / (6 × 24) = 5040 / 144 = 35."
        ),
    ),
    Problem(
        question=(
            "How many 3-digit PIN codes can be made from digits 1–9 "
            "if repetition is not allowed?"
        ),
        answer=504,
        hint="Use permutations: P(9,3) = 9 × 8 × 7.",
        solution=(
            "Order matters (PIN 1-2-3 differs from 3-2-1), so use permutations.\n"
            "P(9,3) = 9 × 8 × 7 = 504.\n"
            "Alternatively: 9! / (9-3)! = 9! / 6! = 504."
        ),
    ),
    Problem(
        question="A pizza shop offers 5 toppings. How many different 2-topping pizzas can be made?",
        answer=10,
        hint="Use combinations: C(5,2) = 5! / (2! × 3!).",
        solution=(
            "Order doesn't matter (pepperoni+mushroom = mushroom+pepperoni), so use combinations.\n"
            "C(5,2) = 5! / (2! × 3!) = 120 / (2 × 6) = 120 / 12 = 10."
        ),
    ),
    Problem(
        question="How many ways can 4 students sit in a row of 4 chairs?",
        answer=24,
        hint="Use the factorial formula: 4! = 4 × 3 × 2 × 1.",
        solution=(
            "Each seat assignment is a different arrangement, so order matters — use permutations.\n"
            "4! = 4 × 3 × 2 × 1 = 24."
        ),
    ),
    Problem(
        question="From a deck of 52 cards, how many 5-card hands are possible?",
        answer=2598960,
        hint="Use combinations: C(52,5) = 52! / (5! × 47!).",
        solution=(
            "Order doesn't matter in a hand of cards, so use combinations.\n"
            "C(52,5) = 52! / (5! × 47!)\n"
            "= (52 × 51 × 50 × 49 × 48) / (5 × 4 × 3 × 2 × 1)\n"
            "= 311,875,200 / 120\n"
            "= 2,598,960."
        ),
    ),
    Problem(
        question="How many ways can you choose 2 books from a shelf of 8?",
        answer=28,
        hint="Use combinations: C(8,2) = 8! / (2! × 6!).",
        solution=(
            "Order doesn't matter (choosing book A then B is the same as B then A).\n"
            "C(8,2) = 8! / (2! × 6!) = (8 × 7) / (2 × 1) = 56 / 2 = 28."
        ),
    ),
    Problem(
        question="In how many ways can 6 people be seated at a circular table?",
        answer=120,
        hint="Circular permutations: (n-1)! = 5!.",
        solution=(
            "In a circle, rotations of the same arrangement are identical.\n"
            "Fix one person in place, then arrange the remaining 5.\n"
            "(6-1)! = 5! = 5 × 4 × 3 × 2 × 1 = 120."
        ),
    ),
]


def pick_problems(n: int = 2) -> list:
    """Return n randomly selected problems."""
    return random.sample(COMBINATORICS_PROBLEMS, min(n, len(COMBINATORICS_PROBLEMS)))


def grade_answer(problem: Problem, user_answer: str) -> bool:
    """Return True if user_answer matches the expected answer."""
    try:
        return int(user_answer.strip()) == int(problem.answer)
    except (ValueError, AttributeError):
        return str(user_answer).strip().lower() == str(problem.answer).strip().lower()
