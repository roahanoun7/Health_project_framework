"""Timed study sessions and explicit placeholders for not-yet-built tests."""

import time
import tkinter as tk
from datetime import datetime
from math import ceil


STUDY_DURATION_SECONDS = 25 * 60
BREAK_DURATION_SECONDS = 10 * 60

BG_COLOR = "#2e2e2e"
FG_COLOR = "#ffffff"
BUTTON_BG = "#444444"
BUTTON_FG = "#ffffff"
BUTTON_ACTIVE_BG = "#666666"
FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")


class StudySessionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.title_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.title_label.pack(pady=24)
        tk.Label(
            self,
            text=(
                "The reading dataset is not connected yet. This timed placeholder "
                "is for flow testing only, not for participant data collection."
            ),
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=760,
            justify="center",
        ).pack(pady=12)
        self.timer_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.timer_label.pack(pady=20)
        tk.Button(
            self,
            text="Skip study session (temporary)",
            command=self.skip_session,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
        ).pack(pady=12)
        self.active = False
        self.timer_id = None

    def start_session(self, session_label: str):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
        self.title_label.config(text=session_label)
        self.started_at = datetime.now().astimezone()
        self.deadline = time.monotonic() + STUDY_DURATION_SECONDS
        self.active = True
        self._update_timer()

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

    def skip_session(self):
        self._finish_session()

    def _finish_session(self):
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


class ActivityBreakPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.activity_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
        self.activity_label.pack(pady=40)
        self.timer_label = tk.Label(
            self, text="", font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR
        )
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
        self.title_label.pack(pady=30)
        self.message_label = tk.Label(
            self,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=760,
            justify="center",
        )
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
