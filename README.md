# CodeAlpha_Hangman

**CodeAlpha Python Programming Internship — Task 1: Hangman Game**

A Hangman game in pure Python with two ways to play:

| File | What it is |
|------|------------|
| `hangman_console.py` | Classic text-based version (the original task scope) |
| `hangman_gui.py` | Professional **3D-style window** version that opens on its own screen |
| `hangman_logic.py` | Shared game rules used by both versions |

## Features

- Random word picked from **5 predefined words** (`python`, `developer`, `internship`, `algorithm`, `variable`)
- **6 incorrect guesses** allowed
- Repeated and invalid guesses are detected and don't cost a life
- Play-again option
- 3D window version: extruded title, gradient cards, shaded hangman, bevelled letter tiles, clickable 3D keyboard, glossy life orbs

## How to run

Requires **Python 3.8+**. No external libraries — `tkinter` ships with Python.

```bash
# 3D window version
python hangman_gui.py

# Console version
python hangman_console.py
```

> **Linux:** if you get `No module named tkinter`, run `sudo apt install python3-tk`.

## Controls (3D version)

- Type letters on your keyboard **or** click the on-screen keys
- `Enter` — new game
- `Esc` — quit

## Concepts used

`random`, `while` loop, `if / elif / else`, strings, lists, sets, classes, `tkinter` Canvas drawing.

## Project structure

```
CodeAlpha_Hangman/
├── hangman_logic.py     # rules: word choice, guesses, win/lose
├── hangman_console.py   # text interface
├── hangman_gui.py       # 3D-style tkinter interface
└── README.md
```

## Author

Your Name — CodeAlpha Python Programming Intern
