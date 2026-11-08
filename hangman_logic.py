"""
hangman_logic.py
----------------
Core game rules for the CodeAlpha Hangman project.

This module has NO input/output code, so the exact same rules power both the
console version (hangman_console.py) and the 3D window version (hangman_gui.py).

Concepts used: random, lists, sets, strings, if-else.
"""

import random

# Task requirement: a small list of 5 predefined words.
WORDS = ["python", "developer", "internship", "algorithm", "variable"]

# Task requirement: limit incorrect guesses to 6.
MAX_WRONG = 6


class HangmanGame:
    """Holds the state of one Hangman game and applies the rules."""

    CORRECT = "correct"
    WRONG = "wrong"
    REPEAT = "repeat"
    INVALID = "invalid"

    def __init__(self, words=None, max_wrong=MAX_WRONG):
        self.words = [w.lower() for w in (words or WORDS)]
        self.max_wrong = max_wrong
        self.word = ""
        self.guessed = []   # every letter tried, in order
        self.wrong = []     # only the incorrect letters
        self.new_round()

    # ------------------------------------------------------------------ setup
    def new_round(self):
        """Pick a random word (avoiding an immediate repeat) and reset."""
        choices = [w for w in self.words if w != self.word] or self.words
        self.word = random.choice(choices)
        self.guessed = []
        self.wrong = []

    # ------------------------------------------------------------------ rules
    def guess(self, letter):
        """Apply one guess and return CORRECT / WRONG / REPEAT / INVALID."""
        letter = letter.lower()
        if len(letter) != 1 or not letter.isalpha():
            return self.INVALID
        if letter in self.guessed:
            return self.REPEAT

        self.guessed.append(letter)
        if letter in self.word:
            return self.CORRECT
        self.wrong.append(letter)
        return self.WRONG

    # ------------------------------------------------------------------ state
    @property
    def wrong_count(self):
        return len(self.wrong)

    @property
    def lives_left(self):
        return self.max_wrong - self.wrong_count

    @property
    def revealed(self):
        """List like ['p', '_', 't', '_', '_', '_'] for display."""
        return [ch if ch in self.guessed else "_" for ch in self.word]

    @property
    def is_won(self):
        return "_" not in self.revealed

    @property
    def is_lost(self):
        return self.wrong_count >= self.max_wrong

    @property
    def is_over(self):
        return self.is_won or self.is_lost
