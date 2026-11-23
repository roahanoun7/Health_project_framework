# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
from tkinter import messagebox, ttk
from zipfile import BadZipFile
import yaml
from openpyxl.utils.exceptions import InvalidFileException

FONT = ("Helvetica", 14)
HEADER_FONT = ("Helvetica", 24, "bold")
BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
SEPARATOR_COLOR = "#334155"


class IntroPage(tk.Frame):
    """Introduction and pre-test questionnaire."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        title = tk.Label(
            self,
            text="Mental Performance",
            font=HEADER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        title._theme_role = "title"
        title.pack(pady=(24, 4))
        tk.Label(
            self,
            text="Please answer the following questions before starting the session.",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        ).pack(pady=(0, 12))

        form = tk.Frame(self, bg=BG_COLOR, padx=24, pady=16)
        form._theme_role = "card"
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
        self._add_combobox(
            form,
            7,
            'How many hours did you sleep?',
            self.sleep_hours_var,
            values=('under 6', '6-8', '8-10', 'above 10'),
        )

        self.sleep_quality_var = tk.StringVar(value='good')
        self._add_choice(form, 8, 'How well did you sleep?', self.sleep_quality_var, ('good', 'fair', 'poor'))

        self.awake_hours_var = tk.StringVar()
        self._add_combobox(
            form,
            9,
            'How long have you been awake?',
            self.awake_hours_var,
            values=tuple(str(hours) for hours in range(1, 9)),
        )

        self.screen_time_var = tk.StringVar()
        self._add_combobox(
            form,
            10,
            'How much screen time have you had today?',
            self.screen_time_var,
            values=tuple(str(hours) for hours in range(1, 6)),
        )

        self.room_light_var = tk.StringVar()
        self._add_combobox(
            form,
            11,
            'What is the light level in your room?',
            self.room_light_var,
            values=tuple(f'{percentage}%-{percentage + 10}%' for percentage in range(10, 100, 20)),
        )

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

        self.start_button = tk.Canvas(
            self,
            width=260,
            height=64,
            bg=BG_COLOR,
            highlightthickness=0,
            takefocus=True,
            cursor='hand2',
        )
        self.start_button.pack(pady=14)
        self.start_button.bind('<Button-1>', self._start_from_button)
        self.start_button.bind('<Enter>', self._start_button_enter)
        self.start_button.bind('<Leave>', self._start_button_leave)
        self.start_button.bind('<Return>', self._start_from_button)
        self.start_button.bind('<space>', self._start_from_button)
        self._start_button_hovered = False
        self.apply_theme()

    @staticmethod
    def _add_entry(form, row, label, variable, width=32):
        question = IntroPage._question_row(form, row)
        tk.Label(question, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=0, column=0, sticky='w', padx=(0, 12), pady=2
        )
        ttk.Entry(question, textvariable=variable, font=FONT, width=width).grid(
            row=0, column=1, sticky='w', pady=2
        )
        IntroPage._add_separator(question)

    @staticmethod
    def _add_choice(form, row, label, variable, choices):
        question = IntroPage._question_row(form, row)
        tk.Label(question, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=0, column=0, sticky='w', padx=(0, 12), pady=2
        )
        choice_frame = tk.Frame(question, bg=BG_COLOR)
        choice_frame.grid(row=0, column=1, sticky='w', pady=2)
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
        IntroPage._add_separator(question)

    @staticmethod
    def _add_combobox(form, row, label, variable, values):
        question = IntroPage._question_row(form, row)
        tk.Label(question, text=label, font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=0, column=0, sticky='w', padx=(0, 12), pady=2
        )
        ttk.Combobox(
            question,
            textvariable=variable,
            values=values,
            state='readonly',
            font=FONT,
            width=29,
        ).grid(row=0, column=1, sticky='w', pady=2)
        IntroPage._add_separator(question)

    @staticmethod
    def _question_row(form, row):
        question = tk.Frame(form, bg=BG_COLOR)
        question.grid(row=row, column=0, columnspan=2, sticky='ew')
        question.columnconfigure(1, weight=1)
        return question

    @staticmethod
    def _add_separator(question):
        separator = tk.Frame(question, height=1, bg=SEPARATOR_COLOR)
        separator._theme_role = "separator"
        separator.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(3, 0))

    def apply_theme(self):
        colors = self.controller.get_theme_colors()
        self.start_button.configure(bg=colors["background"])
        self.start_button.delete("all")
        self.start_button.create_polygon(
            18, 3, 242, 3, 257, 18, 257, 46, 242, 61, 18, 61, 3, 46, 3, 18,
            smooth=True,
            splinesteps=24,
            fill=colors["hover"] if self._start_button_hovered else colors["button"],
            outline=colors["hover"] if self._start_button_hovered else colors["border"],
            width=3,
        )
        self.start_button.create_text(
            130,
            32,
            text='Start Session',
            font=('Helvetica', 14, 'bold'),
            fill=(
                colors["hover_foreground"]
                if self._start_button_hovered
                else colors["button_foreground"]
            ),
        )

    def _start_button_enter(self, _event):
        self._start_button_hovered = True
        self.apply_theme()

    def _start_button_leave(self, _event):
        self._start_button_hovered = False
        self.apply_theme()

    def _start_from_button(self, _event):
        self.on_start()
        return 'break'

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

        if self.confirmed_var.get() != 'Yes':
            messagebox.showwarning(
                'Confirmation required',
                'Please confirm that the information is correct and that you are able to participate.',
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
