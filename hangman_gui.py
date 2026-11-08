"""
hangman_gui.py
--------------
CodeAlpha Python Internship - Task 1: Hangman Game (3D-style window version).

Opens in its own window and uses only Python's built-in tkinter - nothing to
install. The "3D" look is created by layering shapes: gradients, drop shadows,
highlights, extruded text, shaded spheres and bevelled keys.

Run:  python hangman_gui.py

Controls:
    * Type letters on your keyboard, or click the on-screen keys
    * Enter  -> start a new game
    * Esc    -> quit
"""

import tkinter as tk

from hangman_logic import HangmanGame

# --------------------------------------------------------------------- layout
W, H = 1000, 640
LEFT_CARD = (30, 30, 520, 610)
RIGHT_CARD = (545, 30, 975, 610)
CENTER_X = 760          # horizontal centre of the right panel

# -------------------------------------------------------------------- palette
BG_TOP, BG_BOTTOM = "#222a5c", "#090b1e"
CARD_TOP, CARD_BOTTOM = "#2b3270", "#141838"
GOLD = "#ffd166"
TEXT_MUTED = "#9aa4d6"
WOOD = "#9a6431"
SKIN = "#f2b880"
SHIRT = "#4f8cff"
PANTS = "#2f56c9"
GOOD = "#2fbf71"
BAD = "#e05260"
SHADOW = "#05061a"

FONT = "Helvetica"


# ------------------------------------------------------------- colour helpers
def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in rgb)


def lerp(c1, c2, t):
    """Blend colour c1 into c2 (t = 0 -> c1, t = 1 -> c2)."""
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return rgb_to_hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


def shade(color, amount):
    """amount > 0 lightens, amount < 0 darkens (range -1 .. 1)."""
    if amount >= 0:
        return lerp(color, "#ffffff", amount)
    return lerp(color, "#000000", -amount)


# ------------------------------------------------------------------ the app
class HangmanApp(tk.Tk):
    KEY_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    KEY_SIZE, KEY_PITCH, KEY_DEPTH = 36, 42, 5

    def __init__(self):
        super().__init__()
        self.title("CodeAlpha  |  3D Hangman")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=W, height=H,
                                highlightthickness=0, bg=BG_BOTTOM)
        self.canvas.pack()

        self.game = HangmanGame()
        self.status = "Guess a letter!"
        self.status_color = TEXT_MUTED
        self.key_boxes = {}                 # letter -> (x0, y0, x1, y1)
        self.new_game_box = (660, 530, 860, 574)

        self.draw_static()
        self.render()

        self.bind("<Key>", self.on_key)
        self.bind("<Escape>", lambda e: self.destroy())
        self.canvas.bind("<Button-1>", self.on_click)
        self.center_window()

    # ---------------------------------------------------------------- window
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - W) // 2
        y = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{max(x, 0)}+{max(y, 0)}")

    # ------------------------------------------------------- drawing helpers
    def vgradient(self, x0, y0, x1, y1, top, bottom, tag):
        """Vertical gradient built from 1-pixel-high strips."""
        height = max(int(y1 - y0), 1)
        for i in range(height):
            color = lerp(top, bottom, i / height)
            self.canvas.create_rectangle(x0, y0 + i, x1, y0 + i + 1,
                                         fill=color, outline="", tags=tag)

    def sphere(self, cx, cy, r, base, tag):
        """A shaded ball: stacked circles drifting toward a highlight."""
        light = shade(base, 0.65)
        dark = shade(base, -0.35)
        for i in range(r, 0, -1):
            t = i / r
            off = (r - i) * 0.38
            color = lerp(light, lerp(base, dark, 0.6), t)
            self.canvas.create_oval(cx - i - off, cy - i - off,
                                    cx + i - off, cy + i - off,
                                    fill=color, outline="", tags=tag)

    def tube(self, p0, p1, width, color, tag):
        """A rounded limb with a drop shadow and a glossy highlight."""
        (x0, y0), (x1, y1) = p0, p1
        c = self.canvas
        c.create_line(x0 + 4, y0 + 5, x1 + 4, y1 + 5, width=width + 2,
                      fill=SHADOW, capstyle=tk.ROUND, tags=tag)
        c.create_line(x0, y0, x1, y1, width=width,
                      fill=shade(color, -0.25), capstyle=tk.ROUND, tags=tag)
        c.create_line(x0, y0, x1, y1, width=width * 0.72,
                      fill=color, capstyle=tk.ROUND, tags=tag)
        c.create_line(x0 - width * 0.18, y0 - width * 0.1,
                      x1 - width * 0.18, y1 - width * 0.1,
                      width=max(width * 0.22, 2),
                      fill=shade(color, 0.45), capstyle=tk.ROUND, tags=tag)

    def box3d(self, x0, y0, x1, y1, depth, color, tag):
        """An extruded block: front face + lighter top + darker side."""
        c = self.canvas
        c.create_polygon(x0, y0, x0 + depth, y0 - depth,
                         x1 + depth, y0 - depth, x1, y0,
                         fill=shade(color, 0.3), outline="", tags=tag)
        c.create_polygon(x1, y0, x1 + depth, y0 - depth,
                         x1 + depth, y1 - depth, x1, y1,
                         fill=shade(color, -0.35), outline="", tags=tag)
        c.create_rectangle(x0, y0, x1, y1, fill=color, outline="", tags=tag)
        # wood-grain feel: a soft highlight along the front face
        c.create_line(x0, y0 + 2, x1, y0 + 2,
                      fill=shade(color, 0.25), tags=tag)

    def text3d(self, x, y, text, size, color, depth, tag, anchor="center"):
        """Extruded text: dark copies stacked behind the bright top layer."""
        font = (FONT, size, "bold")
        for i in range(depth, 0, -1):
            self.canvas.create_text(x + i, y + i, text=text, font=font,
                                    fill=lerp(shade(color, -0.75),
                                              shade(color, -0.45), i / depth),
                                    anchor=anchor, tags=tag)
        self.canvas.create_text(x, y, text=text, font=font, fill=color,
                                anchor=anchor, tags=tag)

    def card(self, box):
        x0, y0, x1, y1 = box
        self.canvas.create_rectangle(x0 + 8, y0 + 12, x1 + 8, y1 + 12,
                                     fill="#04051a", outline="", tags="static")
        self.vgradient(x0, y0, x1, y1, CARD_TOP, CARD_BOTTOM, "static")
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="#4756b8",
                                     width=2, tags="static")

    # ------------------------------------------------------ static scenery
    def draw_static(self):
        c = self.canvas
        self.vgradient(0, 0, W, H, BG_TOP, BG_BOTTOM, "static")
        self.card(LEFT_CARD)
        self.card(RIGHT_CARD)

        # ---- gallows --------------------------------------------------
        c.create_oval(80, 556, 490, 596, fill="#0a0c26", outline="",
                      tags="static")                       # ground shadow
        self.box3d(80, 540, 460, 565, 16, WOOD, "static")  # base
        self.box3d(130, 120, 160, 540, 16, WOOD, "static")  # upright
        self.box3d(130, 100, 400, 130, 16, WOOD, "static")  # top beam
        self.tube((160, 235), (232, 130), 16, shade(WOOD, -0.1), "static")  # brace
        # rope
        c.create_line(332, 114, 332, 188, width=7, fill="#6b5130",
                      capstyle=tk.ROUND, tags="static")
        c.create_line(331, 114, 331, 188, width=4, fill="#e0c088",
                      capstyle=tk.ROUND, tags="static")
        for y in range(120, 186, 8):                       # twisted-rope marks
            c.create_line(328, y, 336, y + 5, fill="#8a6a3c", tags="static")

        # ---- titles ---------------------------------------------------
        self.text3d(CENTER_X, 78, "HANGMAN", 40, GOLD, 7, "static")
        c.create_text(CENTER_X, 124, text="Guess the word before the man hangs!",
                      font=(FONT, 11), fill=TEXT_MUTED, tags="static")
        c.create_text(CENTER_X, 592,
                      text="Type letters or click keys   |   Enter = new game   |   Esc = quit",
                      font=(FONT, 9), fill="#6e78b8", tags="static")
        c.create_text(275, 596, text="CodeAlpha Python Internship  -  Task 1",
                      font=(FONT, 9), fill="#6e78b8", tags="static")

    # ---------------------------------------------------- dynamic drawing
    def render(self):
        self.canvas.delete("dynamic")
        self.draw_figure()
        self.draw_word()
        self.draw_status()
        self.draw_lives()
        self.draw_keyboard()
        self.draw_new_game_button()

    def draw_figure(self):
        n, tag, cx = self.game.wrong_count, "dynamic", 332
        c = self.canvas

        # Draw order: back limbs first, head last so it sits on top.
        if n >= 5:
            self.tube((cx - 4, 372), (cx - 40, 462), 15, PANTS, tag)   # left leg
        if n >= 6:
            self.tube((cx + 4, 372), (cx + 40, 462), 15, PANTS, tag)   # right leg
        if n >= 2:
            self.tube((cx, 262), (cx, 378), 24, SHIRT, tag)            # body
        if n >= 3:
            self.tube((cx - 8, 285), (cx - 56, 346), 13, SKIN, tag)    # left arm
        if n >= 4:
            self.tube((cx + 8, 285), (cx + 56, 346), 13, SKIN, tag)    # right arm
        if n >= 1:
            c.create_oval(cx - 30, 192, cx + 38, 262, fill=SHADOW,
                          outline="", tags=tag)                       # head shadow
            self.sphere(cx, 226, 34, SKIN, tag)
            self.draw_face(cx, 226)

    def draw_face(self, cx, cy):
        c, tag = self.canvas, "dynamic"
        ink = "#3b2412"
        if self.game.is_lost:                       # X X eyes + flat mouth
            for ex in (cx - 11, cx + 11):
                c.create_line(ex - 5, cy - 11, ex + 5, cy - 1, width=3,
                              fill=ink, capstyle=tk.ROUND, tags=tag)
                c.create_line(ex - 5, cy - 1, ex + 5, cy - 11, width=3,
                              fill=ink, capstyle=tk.ROUND, tags=tag)
            c.create_line(cx - 9, cy + 15, cx + 9, cy + 15, width=3,
                          fill=ink, capstyle=tk.ROUND, tags=tag)
        else:                                       # worried face
            for ex in (cx - 11, cx + 11):
                c.create_oval(ex - 4, cy - 10, ex + 4, cy - 2,
                              fill="white", outline=ink, tags=tag)
                c.create_oval(ex - 2, cy - 8, ex + 2, cy - 4,
                              fill=ink, outline="", tags=tag)
            c.create_arc(cx - 9, cy + 8, cx + 9, cy + 22, start=0, extent=180,
                         style=tk.ARC, width=3, outline=ink, tags=tag)

    def draw_word(self):
        game, c = self.game, self.canvas
        n = len(game.word)
        gap = 6
        tile_w = min(44, (400 - (n - 1) * gap) // n)
        tile_h = 58
        total = n * tile_w + (n - 1) * gap
        x = CENTER_X - total / 2
        y = 160

        for ch, shown in zip(game.word, game.revealed):
            missed = game.is_lost and shown == "_"
            if shown != "_":
                top, bottom, edge, txt = "#ffe29a", "#f2a72c", "#a86a0c", "#3a2400"
                letter = ch.upper()
            elif missed:
                top, bottom, edge, txt = "#ff8a96", "#c2323f", "#7a1620", "#ffffff"
                letter = ch.upper()
            else:
                top, bottom, edge, txt = "#4656b4", "#2a3578", "#171d4a", "#ffffff"
                letter = ""

            c.create_rectangle(x + 4, y + 8, x + tile_w + 4, y + tile_h + 8,
                               fill=SHADOW, outline="", tags="dynamic")
            c.create_rectangle(x, y + 6, x + tile_w, y + tile_h + 6,
                               fill=edge, outline="", tags="dynamic")   # thickness
            self.vgradient(x, y, x + tile_w, y + tile_h, top, bottom, "dynamic")
            c.create_line(x, y, x + tile_w, y, fill=shade(top, 0.5),
                          tags="dynamic")
            c.create_text(x + tile_w / 2 + 1, y + tile_h / 2 + 2, text=letter,
                          font=(FONT, 24, "bold"), fill=shade(bottom, -0.5),
                          tags="dynamic")
            c.create_text(x + tile_w / 2, y + tile_h / 2, text=letter,
                          font=(FONT, 24, "bold"), fill=txt, tags="dynamic")
            x += tile_w + gap

    def draw_status(self):
        game = self.game
        if game.is_won:
            self.text3d(CENTER_X, 252, "YOU WIN!", 26, "#5dff9d", 5, "dynamic")
        elif game.is_lost:
            self.text3d(CENTER_X, 252, "GAME OVER", 26, "#ff6b7a", 5, "dynamic")
            self.canvas.create_text(CENTER_X, 284,
                                    text=f"The word was  {game.word.upper()}",
                                    font=(FONT, 12, "bold"), fill=GOLD,
                                    tags="dynamic")
        else:
            self.canvas.create_text(CENTER_X, 252, text=self.status,
                                    font=(FONT, 14, "bold"),
                                    fill=self.status_color, tags="dynamic")

    def draw_lives(self):
        game, c = self.game, self.canvas
        c.create_text(590, 318, text="LIVES", anchor="w",
                      font=(FONT, 11, "bold"), fill=TEXT_MUTED, tags="dynamic")
        for i in range(game.max_wrong):
            cx = 665 + i * 36
            alive = i < game.lives_left
            c.create_oval(cx - 11, 312, cx + 15, 334, fill=SHADOW,
                          outline="", tags="dynamic")
            self.sphere(cx, 318, 11, BAD if alive else "#3a4070", "dynamic")
        wrong = ", ".join(l.upper() for l in game.wrong) or "none"
        c.create_text(CENTER_X, 350, text=f"Wrong letters: {wrong}",
                      font=(FONT, 10), fill=TEXT_MUTED, tags="dynamic")

    def draw_keyboard(self):
        c, game = self.canvas, self.game
        size, pitch, depth = self.KEY_SIZE, self.KEY_PITCH, self.KEY_DEPTH
        self.key_boxes = {}

        for r, row in enumerate(self.KEY_ROWS):
            row_w = len(row) * pitch - (pitch - size)
            x = CENTER_X - row_w / 2
            y = 378 + r * 48
            for letter in row:
                used = letter in game.guessed
                hit = letter in game.word
                if used:
                    top, bottom = (("#46dd8c", "#1f9e58") if hit
                                   else ("#f2707d", "#b02c3a"))
                    txt, lift = "#ffffff", depth - 1       # key is pushed down
                    edge = shade(bottom, -0.4)
                else:
                    top, bottom = "#f4f6ff", "#bcc5f5"
                    txt, lift = "#1d2250", 0
                    edge = "#6672c4"

                fy = y + lift
                c.create_rectangle(x, y + depth + 2, x + size, y + size + depth + 2,
                                   fill=SHADOW, outline="", tags="dynamic")
                c.create_rectangle(x, fy + depth, x + size, fy + size + depth - lift,
                                   fill=edge, outline="", tags="dynamic")
                self.vgradient(x, fy, x + size, fy + size - lift, top, bottom,
                               "dynamic")
                c.create_line(x, fy, x + size, fy, fill=shade(top, 0.6),
                              tags="dynamic")
                c.create_text(x + size / 2, fy + (size - lift) / 2,
                              text=letter.upper(), font=(FONT, 13, "bold"),
                              fill=txt, tags="dynamic")
                self.key_boxes[letter] = (x, y, x + size, y + size + depth)
                x += pitch

    def draw_new_game_button(self):
        x0, y0, x1, y1 = self.new_game_box
        c = self.canvas
        c.create_rectangle(x0 + 3, y0 + 10, x1 + 3, y1 + 10, fill=SHADOW,
                           outline="", tags="dynamic")
        c.create_rectangle(x0, y0 + 6, x1, y1 + 6, fill="#a8520b",
                           outline="", tags="dynamic")
        self.vgradient(x0, y0, x1, y1, "#ffbe5c", "#f07f1d", "dynamic")
        c.create_line(x0, y0, x1, y0, fill="#ffe0aa", tags="dynamic")
        c.create_text((x0 + x1) / 2 + 1, (y0 + y1) / 2 + 2, text="NEW GAME",
                      font=(FONT, 15, "bold"), fill="#8a4306", tags="dynamic")
        c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="NEW GAME",
                      font=(FONT, 15, "bold"), fill="#ffffff", tags="dynamic")

    # ---------------------------------------------------------------- input
    def handle_letter(self, letter):
        if self.game.is_over:
            return
        result = self.game.guess(letter)
        up = letter.upper()
        if result == HangmanGame.CORRECT:
            self.status, self.status_color = f"Nice!  '{up}' is in the word.", "#5dff9d"
        elif result == HangmanGame.WRONG:
            self.status, self.status_color = f"Oops!  No '{up}'.", "#ff6b7a"
        elif result == HangmanGame.REPEAT:
            self.status, self.status_color = f"You already tried '{up}'.", GOLD
        self.render()

    def new_game(self):
        self.game.new_round()
        self.status, self.status_color = "Guess a letter!", TEXT_MUTED
        self.render()

    def on_key(self, event):
        if event.keysym in ("Return", "KP_Enter"):
            self.new_game()
        elif event.char and event.char.isalpha() and len(event.char) == 1:
            self.handle_letter(event.char)

    def on_click(self, event):
        x0, y0, x1, y1 = self.new_game_box
        if x0 <= event.x <= x1 and y0 <= event.y <= y1 + 6:
            self.new_game()
            return
        for letter, (kx0, ky0, kx1, ky1) in self.key_boxes.items():
            if kx0 <= event.x <= kx1 and ky0 <= event.y <= ky1:
                self.handle_letter(letter)
                return


def main():
    HangmanApp().mainloop()


if __name__ == "__main__":
    main()
