# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
from tkinter import messagebox, ttk


FONT = ("Helvetica", 14)
HEADER_FONT = ("Helvetica", 24, "bold")
BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
BUTTON_BG = "#38bdf8"
BUTTON_FG = "#06202e"
BUTTON_ACTIVE_BG = "#7dd3fc"


class PostTestPage(tk.Frame):
    """Post-test questionnaire shown after all games are completed."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(
            self,
            text='Post-test Survey',
            font=HEADER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        title._theme_role = "title"
        title.pack(pady=24)

        form = tk.Frame(self, bg=BG_COLOR, padx=28, pady=20)
        form._theme_role = "card"
        form.pack(pady=10)

        self.interruption_var = tk.StringVar(value='No')
        self.interruption_count_var = tk.StringVar(value='0')
        self.interruption_details_var = tk.StringVar(value='None')

        self._add_choice(
            form,
            0,
            'Did you have any interruption while studying?',
            self.interruption_var,
            ('Yes', 'No'),
            command=self._update_interruption_fields,
        )

        self.interruption_fields = tk.Frame(form, bg=BG_COLOR)
        self.interruption_fields.grid(
            row=1, column=0, columnspan=2, sticky='w'
        )
        tk.Label(
            self.interruption_fields,
            text='How many interruptions?',
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        ).grid(row=0, column=0, sticky='w', padx=(0, 12), pady=8)
        self.interruption_count_dropdown = ttk.Combobox(
            self.interruption_fields,
            textvariable=self.interruption_count_var,
            values=tuple(str(count) for count in range(1, 11)),
            state='readonly',
            font=FONT,
            width=29,
        )
        self.interruption_count_dropdown.grid(row=0, column=1, sticky='w', pady=8)
        self._add_entry(
            self.interruption_fields,
            1,
            'What were they?',
            self.interruption_details_var,
            width=48,
        )
        self.interruption_fields.grid_remove()

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
    def _add_choice(form, row, label, variable, choices, command=None):
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
                selectcolor=BG_COLOR,
                command=command,
            ).pack(side='left')

    def _update_interruption_fields(self):
        if self.interruption_var.get() == 'Yes':
            if self.interruption_count_var.get() == '0':
                self.interruption_count_var.set('')
            if self.interruption_details_var.get() == 'None':
                self.interruption_details_var.set('')
            self.interruption_fields.grid()
        else:
            self.interruption_count_var.set('0')
            self.interruption_details_var.set('None')
            self.interruption_fields.grid_remove()

    def submit(self):
        if self.interruption_var.get() == 'Yes':
            count_text = self.interruption_count_var.get().strip()
            details = self.interruption_details_var.get().strip()
            if not count_text:
                messagebox.showwarning(
                    'Interruption count required',
                    'Select how many interruptions you had.',
                )
                return
            if not details:
                messagebox.showwarning(
                    'Interruption details required',
                    'Enter a brief description of the interruptions.',
                )
                return
            try:
                interruption_count = int(count_text)
            except ValueError:
                messagebox.showwarning(
                    'Invalid interruption count',
                    'Select a count from 1 to 10.',
                )
                return
            if interruption_count not in range(1, 11):
                messagebox.showwarning(
                    'Invalid interruption count',
                    'Select a count from 1 to 10.',
                )
                return
            interruption_details = details
        else:
            interruption_count = 0
            interruption_details = None

        self.controller.post_test_answers = {
            'post_interruption': self.interruption_var.get(),
            'post_interruption_count': interruption_count,
            'post_interruption_details': interruption_details,
        }
        self.controller.game_finished()
