# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
from tkinter import messagebox, ttk
from zipfile import BadZipFile
import yaml
from openpyxl.utils.exceptions import InvalidFileException

FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'
FG_COLOR = '#ffffff'
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'


class IntroPage(tk.Frame):
    """Introduction and pre-test questionnaire."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        tk.Label(
            self,
            text='\nWelcome — Mental Performance survey\n\nPlease answer the following questions before starting the session.',
            font=HEADER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR
        ).pack(pady=18)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=10)

        self.participant_name = controller.participant_name
        self.participant_name.set("")
        self._add_entry(form, 0, 'Name / login:', self.participant_name, width=32)

        self.session_number_var = tk.StringVar()
        self._add_entry(form, 1, 'Session number (1-24):', self.session_number_var)

        self.exam_deadline_var = tk.StringVar(value='No')
        self._add_choice(form, 2, 'Do you have an exam or major deadline this week?', self.exam_deadline_var, ('Yes', 'No'))

        self.glasses_var = tk.StringVar(value='No')
        self._add_choice(form, 3, 'Are you wearing glasses?', self.glasses_var, ('Yes', 'No'))

        self.breakfast_var = tk.StringVar(value='No')
        self._add_choice(form, 4, 'Did you eat breakfast?', self.breakfast_var, ('Yes', 'No'))

        self.caffeine_var = tk.StringVar(value='No')
        self._add_choice(form, 5, 'Have you had caffeine today?', self.caffeine_var, ('Yes', 'No'))

        self.alcohol_var = tk.StringVar(value='No')
        self._add_choice(form, 6, 'Have you had alcohol within the last 24 hours?', self.alcohol_var, ('Yes', 'No'))

        self.sleep_hours_var = tk.StringVar()
        self._add_entry(form, 7, 'How many hours did you sleep?', self.sleep_hours_var)

        self.sleep_quality_var = tk.StringVar(value='good')
        self._add_choice(form, 8, 'How well did you sleep?', self.sleep_quality_var, ('good', 'fair', 'poor'))

        self.awake_hours_var = tk.StringVar()
        self._add_entry(form, 9, 'How long have you been awake?', self.awake_hours_var)

        self.screen_time_var = tk.StringVar()
        self._add_entry(form, 10, 'How much screen time have you had today?', self.screen_time_var)

        self.room_light_var = tk.StringVar()
        self._add_entry(form, 11, 'What is the light level in your room?', self.room_light_var)

        self.stress_var = tk.StringVar(value='not at all')
        self._add_choice(form, 12, 'How stressed do you feel right now?', self.stress_var, ('not at all', 'moderately', 'very'))

        self.ill_var = tk.StringVar(value='No')
        self._add_choice(form, 13, 'Do you feel ill/have a cold?', self.ill_var, ('Yes', 'No'))

        self.confirmed_var = tk.StringVar(value='No')
        self._add_choice(
            form,
            14,
            'I confirm that the above information is correct and that I am able to participate in the test.',
            self.confirmed_var,
            ('Yes', 'No')
        )

        tk.Button(
            self,
            text='Start Session',
            command=self.on_start,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG
        ).pack(pady=14)

    @staticmethod
    def _add_entry(form, row, label, variable, width=32):
        tk.Label(form, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=row, column=0, sticky='w', padx=(0, 12), pady=3
        )
        ttk.Entry(form, textvariable=variable, font=FONT, width=width).grid(
            row=row, column=1, sticky='w', pady=3
        )

    @staticmethod
    def _add_choice(form, row, label, variable, choices):
        tk.Label(form, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=row, column=0, sticky='w', padx=(0, 12), pady=3
        )
        choice_frame = tk.Frame(form, bg=BG_COLOR)
        choice_frame.grid(row=row, column=1, sticky='w', pady=3)
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

    def on_start(self):
        """Validate the participant name and start the first game."""
        name = self.participant_name.get().strip()
        if not name:
            messagebox.showwarning('Name required', 'Please enter your name or login.')
            return
        try:
            session_number = int(self.session_number_var.get().strip())
        except ValueError:
            messagebox.showwarning(
                'Session number required',
                'Please enter a session number from 1 to 24.',
            )
            return
        if session_number not in range(1, 25):
            messagebox.showwarning(
                'Invalid session number',
                'Please enter a session number from 1 to 24.',
            )
            return

        # These keys become columns in the participant results row.
        self.controller.questionnaire_answers = {
            'exam_deadline': self.exam_deadline_var.get(),
            'wearing_glasses': self.glasses_var.get(),
            'ate_breakfast': self.breakfast_var.get(),
            'had_caffeine': self.caffeine_var.get(),
            'had_alcohol_last_24h': self.alcohol_var.get(),
            'sleep_hours': self.sleep_hours_var.get().strip(),
            'sleep_quality': self.sleep_quality_var.get(),
            'hours_awake': self.awake_hours_var.get().strip(),
            'screen_time': self.screen_time_var.get().strip(),
            'room_light_level': self.room_light_var.get().strip(),
            'stress_level': self.stress_var.get(),
            'feeling_ill': self.ill_var.get(),
            'confirmed': self.confirmed_var.get()
        }

        try:
            self.controller.begin_session(name, session_number)
        except (
            OSError,
            ValueError,
            yaml.YAMLError,
            InvalidFileException,
            BadZipFile,
        ) as error:
            messagebox.showerror('Cannot start session', str(error))
