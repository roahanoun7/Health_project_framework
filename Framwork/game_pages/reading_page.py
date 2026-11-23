# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

from datetime import datetime
import tkinter as tk

from game_pages.reading_material import (
    QUESTIONS_PER_SECTION,
    ReadingMaterial,
    ReadingQuestion,
    questions_for_sections,
)


FONT = ("Helvetica", 14)
HEADER_FONT = ("Helvetica", 24, "bold")
BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
SURFACE_COLOR = "#1e293b"
BUTTON_BG = "#38bdf8"
BUTTON_FG = "#06202e"
BUTTON_ACTIVE_BG = "#7dd3fc"


class ReadingPage(tk.Frame):
    """Present comprehension questions for sections read during study."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.material = None
        self.questions = ()
        self.sections_read = 0
        self.question_index = 0
        self.option_buttons = []
        self.answer_var = tk.StringVar()
        self.question_shown_at = None
        self.started_at = None
        self.test_finished = False

        title = tk.Label(
            self,
            text="Comprehension test",
            font=HEADER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        title._theme_role = "title"
        title.pack(pady=(20, 2))
        self.topic_label = tk.Label(
            self,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        self.topic_label.pack(pady=(0, 10))

        self.stage_container = tk.Frame(self, bg=BG_COLOR)
        self.stage_container.pack(fill="both", expand=True, padx=36, pady=(0, 28))

        self.question_view = tk.Frame(self.stage_container, bg=BG_COLOR)
        self.completion_view = tk.Frame(self.stage_container, bg=BG_COLOR)
        for view in (self.question_view, self.completion_view):
            view.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_question_view()
        self._build_completion_view()

    def _build_question_view(self):
        self.question_progress = tk.Label(
            self.question_view,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        self.question_progress.pack(pady=(0, 8))

        card = tk.Frame(
            self.question_view,
            bg=SURFACE_COLOR,
            padx=28,
            pady=24,
        )
        card._theme_role = "card"
        card.pack(fill="both", expand=True)

        self.question_label = tk.Label(
            card,
            text="",
            font=HEADER_FONT,
            bg=SURFACE_COLOR,
            fg=FG_COLOR,
            wraplength=860,
            justify="left",
            anchor="w",
        )
        self.question_label._theme_role = "title"
        self.question_label.pack(fill="x", pady=(0, 18))

        self.option_frame = tk.Frame(card, bg=SURFACE_COLOR)
        self.option_frame.pack(fill="x")
        self.question_status = tk.Label(
            card,
            text="",
            font=FONT,
            bg=SURFACE_COLOR,
            fg=FG_COLOR,
        )
        self.question_status.pack(pady=(12, 0))

        self.submit_answer_button = tk.Button(
            self.question_view,
            text="Submit answer",
            command=self.submit_answer,
            state="disabled",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        )
        self.submit_answer_button.pack(pady=(14, 0))

    def _build_completion_view(self):
        card = tk.Frame(
            self.completion_view,
            bg=SURFACE_COLOR,
            padx=32,
            pady=28,
        )
        card._theme_role = "card"
        card.pack(expand=True, pady=40)

        title = tk.Label(
            card,
            text="Comprehension complete",
            font=HEADER_FONT,
            bg=SURFACE_COLOR,
            fg=FG_COLOR,
        )
        title._theme_role = "title"
        title.pack(pady=(0, 12))
        self.completion_message = tk.Label(
            card,
            text="",
            font=FONT,
            bg=SURFACE_COLOR,
            fg=FG_COLOR,
            justify="center",
        )
        self.completion_message.pack()

        self.continue_button = tk.Button(
            self.completion_view,
            text="Continue",
            command=self.controller.game_finished,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        )
        self.continue_button.pack(pady=12)

    def start_game(self, material: ReadingMaterial, sections_read: int):
        """Start comprehension questions for the sections read during study."""
        if not material.sections:
            raise ValueError("The reading material contains no sections.")
        if len(material.questions) != (
            len(material.sections) * QUESTIONS_PER_SECTION
        ):
            raise ValueError(
                "The reading material must contain exactly two questions per section."
            )
        if not 1 <= sections_read <= len(material.sections):
            raise ValueError(
                "The number of sections read must be between 1 and the total "
                "number of sections."
            )

        self.material = material
        self.sections_read = sections_read
        self.question_index = 0
        self.questions = questions_for_sections(material, sections_read)
        self.started_at = datetime.now().astimezone()
        self.test_finished = False
        self.controller.reading_QA_results = []
        self.controller.QA_done = 0
        self.topic_label.config(text=material.title)
        self._create_option_buttons()
        self._show_question()

    def _create_option_buttons(self):
        if self.material is None:
            raise RuntimeError("Reading material has not been loaded.")
        for button in self.option_buttons:
            button.destroy()
        self.option_buttons = []

        max_options = max(len(question.options) for question in self.questions)
        is_right_to_left = self.material.language_code in ("ar", "fa")
        for option_index in range(max_options):
            button = tk.Radiobutton(
                self.option_frame,
                text="",
                variable=self.answer_var,
                value=str(option_index + 1),
                command=self._answer_selected,
                font=FONT,
                bg=SURFACE_COLOR,
                fg=FG_COLOR,
                selectcolor="#334155",
                activebackground=SURFACE_COLOR,
                activeforeground=FG_COLOR,
                anchor="e" if is_right_to_left else "w",
                justify="right" if is_right_to_left else "left",
                wraplength=820,
            )
            button.pack(fill="x", anchor="e" if is_right_to_left else "w", pady=5)
            self.option_buttons.append(button)

    def _show_question(self):
        if self.material is None:
            raise RuntimeError("Reading material has not been loaded.")
        question = self.questions[self.question_index]
        is_right_to_left = self.material.language_code in ("ar", "fa")

        self.question_progress.config(
            text=f"Question {self.question_index + 1} of {len(self.questions)}"
        )
        self.question_label.config(
            text=question.question,
            justify="right" if is_right_to_left else "left",
            anchor="e" if is_right_to_left else "w",
        )
        self.answer_var.set("")
        for option_index, button in enumerate(self.option_buttons):
            if option_index < len(question.options):
                button.config(
                    text=question.options[option_index],
                    value=str(option_index + 1),
                )
                button.pack(fill="x", pady=5)
            else:
                button.pack_forget()
        self.question_status.config(text="")
        self.submit_answer_button.config(state="disabled")
        self.question_shown_at = datetime.now().astimezone()
        self.question_view.tkraise()

    def _answer_selected(self):
        self.question_status.config(text="")
        self.submit_answer_button.config(state="normal")

    def submit_answer(self):
        if self.material is None or self.question_shown_at is None:
            raise RuntimeError("No comprehension question is currently active.")
        selected_option = self.answer_var.get()
        if not selected_option:
            self.question_status.config(text="Select an answer before continuing.")
            return

        question: ReadingQuestion = self.questions[self.question_index]
        selected_index = int(selected_option) - 1
        self.controller.reading_QA_results.append(
            {
                "context_id": (
                    f"{self.material.topic_id}-section-{question.section_number}"
                ),
                "topic_id": self.material.topic_id,
                "language": self.material.language_code,
                "section_number": question.section_number,
                "question_id": question.question_id,
                "question": question.question,
                "correct_answer": question.options[question.correct_option - 1],
                "player_answer": question.options[selected_index],
                "show_question": self.question_shown_at.isoformat(
                    timespec="milliseconds"
                ),
            }
        )
        self.controller.QA_done += 1

        if self.question_index + 1 < len(self.questions):
            self.question_index += 1
            self._show_question()
        else:
            self._finish_questions()

    def _finish_questions(self):
        if self.test_finished or self.started_at is None:
            return
        self.test_finished = True
        finished_at = datetime.now().astimezone()
        self.controller.add_game_timestamp(
            (
                self.started_at.isoformat(timespec="milliseconds"),
                finished_at.isoformat(timespec="milliseconds"),
            )
        )
        self.completion_message.config(
            text=(
                f"You read {self.sections_read} section(s) and answered "
                f"{len(self.questions)} question(s)."
            )
        )
        self.completion_view.tkraise()
