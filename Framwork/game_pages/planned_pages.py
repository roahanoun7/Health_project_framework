"""Timed study sessions with reading material and explicit test placeholders."""

import time
import tkinter as tk
from datetime import datetime
from math import ceil
from tkinter import ttk

from game_pages.reading_material import ReadingMaterial


STUDY_DURATION_SECONDS = 25 * 60
BREAK_DURATION_SECONDS = 10 * 60

BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
BUTTON_BG = "#38bdf8"
BUTTON_FG = "#06202e"
BUTTON_ACTIVE_BG = "#7dd3fc"
FONT = ("Helvetica", 14)
HEADER_FONT = ("Helvetica", 24, "bold")


class StudySessionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.material = None
        self.section_index = 0
        self.title_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.title_label._theme_role = "title"
        self.title_label.pack(pady=(10, 4))
        session_info = tk.Frame(self, bg=BG_COLOR)
        session_info.pack(fill="x", padx=36, pady=(0, 6))
        self.section_status = tk.Label(
            session_info, text="", font=FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.section_status.pack(side="left")
        self.timer_label = tk.Label(
            session_info, text="", font=FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.timer_label.pack(side="right")
        navigation = tk.Frame(self, bg=BG_COLOR)
        navigation.pack(pady=(0, 8))
        self.next_section_button = tk.Button(
            navigation,
            text="Next section",
            command=self.next_section,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        )
        self.next_section_button.pack(side="left", padx=8)
        self.finish_session_button = tk.Button(
            navigation,
            text="Finish study session",
            command=self.finish_session,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        )
        self.finish_session_button.pack(side="left", padx=8)
        card = tk.Frame(self, bg="#1e293b", padx=14, pady=14)
        card._theme_role = "card"
        card.pack(fill="both", expand=True, padx=36)
        card.rowconfigure(0, weight=1)
        card.columnconfigure(0, weight=1)
        self.reading_text = tk.Text(
            card,
            wrap="word",
            font=FONT,
            bg="#1e293b",
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            relief="flat",
            padx=18,
            pady=18,
            spacing1=4,
            spacing3=8,
            height=12,
            state="disabled",
        )
        self.reading_text.grid(row=0, column=0, sticky="nsew")
        self.reading_scrollbar = ttk.Scrollbar(
            card,
            orient="vertical",
            command=self.reading_text.yview,
        )
        self.reading_scrollbar.grid(row=0, column=1, sticky="ns")
        self.reading_text.configure(yscrollcommand=self.reading_scrollbar.set)
        self.reading_text.tag_configure("reading_content", justify="left")
        self.active = False
        self.timer_id = None

    def start_session(
        self,
        session_label: str,
        material: ReadingMaterial,
        first_section_index: int,
    ):
        if not 0 <= first_section_index <= len(material.sections):
            raise ValueError("The first unread section is outside the reading material.")
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.material = material
        self.section_index = first_section_index
        self.title_label.config(text=session_label)
        self._show_section()
        self.started_at = datetime.now().astimezone()
        self.deadline = time.monotonic() + STUDY_DURATION_SECONDS
        self.active = True
        self._update_timer()

    def _show_section(self):
        if self.material is None:
            raise RuntimeError("Reading material has not been loaded.")
        if self.section_index >= len(self.material.sections):
            self.section_status.config(text="All reading sections are complete.")
            section_text = "You have already read all available sections."
            self.next_section_button.pack_forget()
        else:
            self.section_status.config(
                text=f"Section {self.section_index + 1} of "
                f"{len(self.material.sections)}"
            )
            section_text = self.material.sections[self.section_index]
            if self.section_index + 1 < len(self.material.sections):
                self.next_section_button.pack(side="left", padx=8)
            else:
                self.next_section_button.pack_forget()

        is_right_to_left = self.material.language_code in ("ar", "fa")
        self.reading_text.tag_configure(
            "reading_content",
            justify="right" if is_right_to_left else "left",
        )
        self.reading_text.configure(state="normal")
        self.reading_text.delete("1.0", "end")
        self.reading_text.insert("1.0", section_text, "reading_content")
        self.reading_text.configure(state="disabled")
        self.reading_text.yview_moveto(0)

    def _mark_current_section_read(self):
        if (
            self.material is not None
            and self.section_index < len(self.material.sections)
        ):
            self.controller.reading_sections_read = max(
                self.controller.reading_sections_read,
                self.section_index + 1,
            )

    def next_section(self):
        if self.material is None:
            raise RuntimeError("Reading material has not been loaded.")
        if self.section_index >= len(self.material.sections):
            return
        self._mark_current_section_read()
        self.section_index += 1
        self._show_section()

    def _update_timer(self):
        self.timer_id = None
        if not self.active:
            return
        remaining = max(0, ceil(self.deadline - time.monotonic()))
        minutes, seconds = divmod(remaining, 60)
        self.timer_label.config(text=f"Time remaining: {minutes:02d}:{seconds:02d}")
        if remaining == 0:
            self._finish_session()
            return
        self.timer_id = self.after(1000, self._update_timer)

    def finish_session(self):
        self._finish_session()

    def _finish_session(self):
        if not self.active:
            return
        self.active = False
        self._mark_current_section_read()
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        finished_at = datetime.now().astimezone()
        self.controller.add_game_timestamp(
            (
                self.started_at.isoformat(timespec="milliseconds"),
                finished_at.isoformat(timespec="milliseconds"),
            )
        )
        self.controller.game_finished()


class ActivityBreakPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.activity_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.activity_label._theme_role = "title"
        self.activity_label.pack(pady=40)
        self.timer_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.timer_label._theme_role = "title"
        self.timer_label.pack(pady=20)
        tk.Button(
            self,
            text="Skip break (temporary)",
            command=self.skip_break,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        ).pack(pady=12)
        self.active = False
        self.timer_id = None

    def start_break(self, activity: str):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
        self.activity_label.config(text=f"Break activity: {activity}")
        self.started_at = datetime.now().astimezone()
        self.deadline = time.monotonic() + BREAK_DURATION_SECONDS
        self.active = True
        self._update_timer()

    def _update_timer(self):
        self.timer_id = None
        if not self.active:
            return
        remaining = max(0, ceil(self.deadline - time.monotonic()))
        minutes, seconds = divmod(remaining, 60)
        self.timer_label.config(text=f"Break ends in: {minutes:02d}:{seconds:02d}")
        if remaining == 0:
            self._finish_break()
            return
        self.timer_id = self.after(1000, self._update_timer)

    def skip_break(self):
        self._finish_break()

    def _finish_break(self):
        if not self.active:
            return
        self.active = False
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        finished_at = datetime.now().astimezone()
        self.controller.add_game_timestamp(
            (
                self.started_at.isoformat(timespec="milliseconds"),
                finished_at.isoformat(timespec="milliseconds"),
            )
        )
        self.controller.game_finished()


class PendingStagePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.title_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.title_label._theme_role = "title"
        self.title_label.pack(pady=30)
        self.message_label = tk.Label(
            self,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=760,
            justify="center",
            padx=28,
            pady=18,
        )
        self.message_label._theme_role = "card"
        self.message_label.pack(pady=20)
        tk.Button(
            self,
            text="Continue",
            command=self.controller.game_finished,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        ).pack(pady=24)

    def show_stage(self, title: str, message: str):
        self.title_label.config(text=title)
        self.message_label.config(text=message)
