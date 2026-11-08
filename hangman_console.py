"""
hangman_console.py
------------------
CodeAlpha Python Internship - Task 1: Hangman Game (console version).

Run:  python hangman_console.py
"""

from hangman_logic import HangmanGame

# One drawing per number of wrong guesses (0 to 6).
STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========""",
]


def show_board(game):
    print(STAGES[game.wrong_count])
    print("\n  Word:   " + " ".join(game.revealed))
    print("  Wrong:  " + (", ".join(game.wrong) if game.wrong else "-"))
    print(f"  Lives:  {game.lives_left}/{game.max_wrong}\n")


def play_round(game):
    print("\n" + "=" * 40)
    print("        H A N G M A N")
    print("=" * 40)

    while not game.is_over:
        show_board(game)
        choice = input("Guess a letter: ").strip()
        result = game.guess(choice)

        if result == game.INVALID:
            print(">> Please type a single letter (a-z).")
        elif result == game.REPEAT:
            print(f">> You already tried '{choice.lower()}'.")
        elif result == game.CORRECT:
            print(f">> Nice! '{choice.lower()}' is in the word.")
        else:
            print(f">> Sorry, no '{choice.lower()}'.")

    show_board(game)
    if game.is_won:
        print(f"*** YOU WIN! The word was '{game.word}'. ***")
    else:
        print(f"*** GAME OVER! The word was '{game.word}'. ***")


def main():
    game = HangmanGame()
    while True:
        play_round(game)
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing! Goodbye.")
            break
        game.new_round()


if __name__ == "__main__":
    main()
