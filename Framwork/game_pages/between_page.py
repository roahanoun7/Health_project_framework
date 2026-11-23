# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk

# ---------- Configuration ----------
HEADER_FONT = ("Helvetica", 24, "bold")
BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
BUTTON_BG = "#38bdf8"
BUTTON_FG = "#06202e"
BUTTON_ACTIVE_BG = "#7dd3fc"


# ---------- Between Games Page (Continue only when needed) ----------
class BetweenGamesPage(tk.Frame):
    """
    BetweenGamesPage class creates a page in between games for the participant to be able to give some breating space for the participant after each test.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.message_var = tk.StringVar()
        message_card = tk.Frame(self, bg=BG_COLOR, padx=32, pady=24)
        message_card._theme_role = "card"
        message_card.pack(pady=40)
        message = tk.Label(
            message_card,
            textvariable=self.message_var,
            font=HEADER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=760,
            justify="center",
        )
        message._theme_role = "title"
        message.pack()
        tk.Button(self, text='Continue', command=self.on_continue,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(pady=30)

    def set_message(self, txt: str):
        """
        Set message after game has been completed, the name of the last completed game is displayed in here
        """
        self.message_var.set(txt)

    def on_continue(self):
        """closes the page and continues to the next page/game in sequence based on the order of the games in the controller application"""
        self.controller.start_next_game()