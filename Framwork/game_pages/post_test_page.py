# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
from tkinter import ttk


FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'
FG_COLOR = '#ffffff'
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'


class PostTestPage(tk.Frame):
    """Post-test questionnaire shown after all games are completed."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        tk.Label(
            self,
            text='Post-test Survey',
            font=HEADER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR
        ).pack(pady=24)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=10)

        self.interruption_var = tk.StringVar(value='No')
        self.interruption_count_var = tk.StringVar()
        self.interruption_details_var = tk.StringVar()

        self._add_choice(
            form,
            0,
            'Did you have any interruption while studying?',
            self.interruption_var,
            ('Yes', 'No')
        )
        self._add_entry(
            form,
            1,
            'How many interruptions?',
            self.interruption_count_var
        )
        self._add_entry(
            form,
            2,
            'What were they?',
            self.interruption_details_var,
            width=48
        )

        tk.Button(
            self,
            text='Continue to Results',
            command=self.submit,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG
        ).pack(pady=20)

    @staticmethod
    def _add_entry(form, row, label, variable, width=32):
        tk.Label(form, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=row, column=0, sticky='w', padx=(0, 12), pady=8
        )
        ttk.Entry(form, textvariable=variable, font=FONT, width=width).grid(
            row=row, column=1, sticky='w', pady=8
        )

    @staticmethod
    def _add_choice(form, row, label, variable, choices):
        tk.Label(form, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=row, column=0, sticky='w', padx=(0, 12), pady=8
        )
        choice_frame = tk.Frame(form, bg=BG_COLOR)
        choice_frame.grid(row=row, column=1, sticky='w', pady=8)
        for choice in choices:
            tk.Radiobutton(
                choice_frame,
                text=choice,
                variable=variable,
                value=choice,
                bg=BG_COLOR,
                fg=FG_COLOR,
                selectcolor=BG_COLOR
            ).pack(side='left')

    def submit(self):
        self.controller.post_test_answers = {
            'post_interruption': self.interruption_var.get(),
            'post_interruption_count': self.interruption_count_var.get().strip(),
            'post_interruption_details': self.interruption_details_var.get().strip()
        }
        self.controller.game_finished()
