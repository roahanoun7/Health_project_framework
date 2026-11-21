# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import random
from datetime import datetime
from tkinter import ttk
from game_pages.between_page import BetweenGamesPage
from game_pages.intro_page import IntroPage
from Games.D2 import AttentionPracticeApp
from game_pages.planned_pages import ActivityBreakPage, PendingStagePage, StudySessionPage
from game_pages.post_test_page import PostTestPage
from game_pages.results_page import ResultsPage
from game_pages.session_flow import build_session_flow
from game_pages.session_schedule import load_session_assignment_from_config

FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)
THEMES = {
    "dark": {
        "background": "#2e2e2e",
        "foreground": "#ffffff",
        "button": "#444444",
        "button_foreground": "#ffffff",
        "hover": "#38bdf8",
        "hover_foreground": "#111827",
        "border": "#777777",
        "separator": "#666666",
        "input": "#e5e5e5",
        "input_foreground": "#202020",
        "muted": "#aaaaaa",
    },
    "light": {
        "background": "#f4f4f4",
        "foreground": "#202020",
        "button": "#ffffff",
        "button_foreground": "#202020",
        "hover": "#38bdf8",
        "hover_foreground": "#111827",
        "border": "#555555",
        "separator": "#b8b8b8",
        "input": "#ffffff",
        "input_foreground": "#202020",
        "muted": "#666666",
    },
}


# ---------- Main Application ----------
class App(tk.Tk):
    """Main application of the game, controlls the states of the game, also saves all the scores of the games"""
    def __init__(self):
        """create instanses of all scores and other necessary game variables, creates seed using datetime, loads in IntroPage always"""
        super().__init__()
        self.title('Mental Performance Test')
        self.configure(bg=BG_COLOR)
        self.theme_mode = "dark"
        self._ttk_style = ttk.Style(self)
        self._ttk_style.theme_use("clam")
        self.geometry('1024x768')
        self.fullscreen = False
        self.bind('<F11>', self.toggle_fullscreen)
        self.bind('<Escape>', self.exit_fullscreen)

        # Participant & questionnaire
        self.participant_name = tk.StringVar()
        self.participant_id = ""
        self.participant_language = ""
        self.session_number = None
        self.week_number = None
        self.scheduled_activity = ""
        self.activity_condition = ""
        self.questionnaire_answers = {}
        self.post_test_answers = {}

        # Scores
        #self.digit_forward_score = 0
        #self.digit_backward_score = 0
        self.d2_results = {}
        self.QA_done = 0 # not work yet
        self.game_timestamps = {}
        self.all_sequence_answers = {} # this is can be used for Pasat test, but not work yet
        self.reading_QA_results = [] # not work yet

        # Create a session-specific random sequence so each run generates different game stimuli.
        self.date_time = datetime.now().isoformat()
        self.random_seed = self.date_time
        random.seed(self.random_seed)

        self.flow = ()
        self.current_stage_index = -1
        self.current_stage = None

        # Container frame (use tk.Frame so bg applies consistently)
        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill='both', expand=True)

        self.theme_toggle = tk.Button(
            self,
            command=self.toggle_theme,
            relief="solid",
            bd=1,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.theme_toggle.place(relx=0.985, rely=0.012, anchor="ne")

        self.frames = {}
        for F in (
            IntroPage,
            AttentionPracticeApp,
            StudySessionPage,
            PendingStagePage,
            ActivityBreakPage,
            BetweenGamesPage,
            PostTestPage,
            ResultsPage,
        ):
            if F is AttentionPracticeApp:
                page = F(container, self, rounds=3)
            else:
                page = F(container, self)
            self.frames[F.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.apply_theme()
        self.show_frame('IntroPage')

    def toggle_fullscreen(self, event=None):
        """toggles fullscreen when pressing f11 on keyboard"""
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)

    def exit_fullscreen(self, event=None):
        """exits fullscreen when pressing f11 on keyboard"""
        if self.fullscreen:
            self.fullscreen = False
            self.attributes('-fullscreen', False)

    def show_frame(self, name):
        """shows next frame"""
        frame = self.frames[name]
        frame.tkraise()
        self.after_idle(self.apply_theme)

    def toggle_theme(self):
        """Switch the colors used across the application."""
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()

    def _apply_ttk_theme(self, colors):
        style = self._ttk_style
        style.configure(
            ".",
            background=colors["background"],
            foreground=colors["foreground"],
        )
        style.configure("TFrame", background=colors["background"])
        style.configure(
            "TLabel",
            background=colors["background"],
            foreground=colors["foreground"],
        )
        style.configure(
            "TButton",
            background=colors["button"],
            foreground=colors["button_foreground"],
            bordercolor=colors["border"],
            focusthickness=1,
            focuscolor=colors["hover"],
        )
        style.map(
            "TButton",
            background=[("disabled", colors["background"]), ("active", colors["hover"])],
            foreground=[
                ("disabled", colors["muted"]),
                ("active", colors["hover_foreground"]),
            ],
        )
        style.configure(
            "Action.TButton",
            background=colors["button"],
            foreground=colors["button_foreground"],
            bordercolor=colors["border"],
        )
        style.map(
            "Action.TButton",
            background=[("disabled", colors["background"]), ("active", colors["hover"])],
            foreground=[("active", colors["hover_foreground"])],
        )
        for label_style in ("Title.TLabel", "Instructions.TLabel", "Timer.TLabel"):
            style.configure(
                label_style,
                background=colors["background"],
                foreground=colors["foreground"],
            )
        for widget_style in ("TEntry", "TCombobox"):
            style.configure(
                widget_style,
                fieldbackground=colors["input"],
                foreground=colors["input_foreground"],
                background=colors["button"],
                arrowcolor=colors["foreground"],
            )
            style.map(
                widget_style,
                fieldbackground=[
                    ("readonly", colors["input"]),
                    ("disabled", colors["background"]),
                ],
                foreground=[("disabled", colors["muted"])],
            )
        for widget_style in ("TRadiobutton", "TCheckbutton"):
            style.configure(
                widget_style,
                background=colors["background"],
                foreground=colors["foreground"],
            )
            style.map(
                widget_style,
                background=[("active", colors["background"])],
                foreground=[("disabled", colors["muted"])],
            )
        style.configure(
            "Treeview",
            background=colors["input"],
            fieldbackground=colors["input"],
            foreground=colors["foreground"],
        )
        style.map(
            "Treeview",
            background=[("selected", colors["hover"])],
            foreground=[("selected", colors["hover_foreground"])],
        )
        style.configure(
            "Treeview.Heading",
            background=colors["button"],
            foreground=colors["button_foreground"],
        )
        style.map("Treeview.Heading", background=[("active", colors["hover"])])
        style.configure(
            "TScrollbar",
            background=colors["button"],
            troughcolor=colors["background"],
            arrowcolor=colors["foreground"],
        )

    def _theme_widget(self, widget, colors):
        if getattr(widget, "_theme_role", None) == "separator":
            widget.configure(bg=colors["separator"])
        elif isinstance(widget, (tk.Frame, tk.Canvas)):
            if not (
                isinstance(widget, tk.Canvas)
                and widget.cget("background").lower() == "#f7f7f7"
            ):
                widget.configure(bg=colors["background"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=colors["background"], fg=colors["foreground"])
        elif isinstance(widget, (tk.Radiobutton, tk.Checkbutton)):
            widget.configure(
                bg=colors["background"],
                fg=colors["foreground"],
                activebackground=colors["background"],
                activeforeground=colors["foreground"],
                selectcolor=colors["background"],
            )
        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=colors["button"],
                fg=colors["button_foreground"],
                activebackground=colors["hover"],
                activeforeground=colors["hover_foreground"],
                highlightbackground=colors["border"],
            )
            if not getattr(widget, "_theme_hover_bound", False):
                widget.bind("<Enter>", self._on_theme_button_enter, add="+")
                widget.bind("<Leave>", self._on_theme_button_leave, add="+")
                widget._theme_hover_bound = True
        elif isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Entry):
            widget.configure(
                bg=colors["input"],
                fg=colors["input_foreground"],
                insertbackground=colors["input_foreground"],
                selectbackground=colors["hover"],
            )

        for child in widget.winfo_children():
            self._theme_widget(child, colors)

    def _on_theme_button_enter(self, event):
        if event.widget.cget("state") != "disabled":
            event.widget.configure(bg=THEMES[self.theme_mode]["hover"])

    def _on_theme_button_leave(self, event):
        if event.widget.cget("state") != "disabled":
            event.widget.configure(bg=THEMES[self.theme_mode]["button"])

    def get_theme_colors(self):
        return THEMES[self.theme_mode]

    def apply_theme(self):
        """Apply the selected palette to existing Tk and ttk widgets."""
        colors = THEMES[self.theme_mode]
        self._apply_ttk_theme(colors)
        self.option_add("*Canvas.background", colors["background"])
        self.configure(bg=colors["background"])
        self.theme_toggle.configure(
            text=f"Switch to {'light' if self.theme_mode == 'dark' else 'dark'} mode"
        )
        self._theme_widget(self, colors)
        intro_page = self.frames.get("IntroPage")
        if intro_page is not None:
            intro_page.apply_theme()

    def add_game_timestamp(self, time_value):
        """Record a significant interval for the active session stage."""
        if self.current_stage is None:
            raise RuntimeError("Cannot record a timestamp without an active stage.")
        self.game_timestamps.setdefault(self.current_stage, []).append(time_value)

    def begin_session(self, participant_name, session_number):
        """Resolve the schedule assignment and start the first study session."""
        assignment = load_session_assignment_from_config(
            participant_name, session_number
        )
        self.participant_name.set(assignment.participant_name)
        self.participant_id = f"Participant {assignment.participant_number}"
        self.participant_language = assignment.language
        self.session_number = assignment.session
        self.week_number = assignment.week
        self.scheduled_activity = assignment.activity_label
        self.activity_condition = assignment.activity
        self.date_time = datetime.now().isoformat()
        self.random_seed = self.date_time
        random.seed(self.random_seed)
        self.flow = build_session_flow(assignment.activity)
        self.current_stage_index = -1
        self.start_next_stage()

    def start_next_stage(self):
        self.current_stage_index += 1
        if self.current_stage_index >= len(self.flow):
            raise RuntimeError("The session flow ended without a results stage.")

        self.current_stage = self.flow[self.current_stage_index]
        stage = self.current_stage

        if stage in ("study_1", "study_2"):
            self.show_frame("StudySessionPage")
            session_number = 1 if stage == "study_1" else 2
            self.frames["StudySessionPage"].start_session(
                f"Study session {session_number}"
            )
        elif stage in ("d2_pre", "d2_post"):
            self.show_frame("AttentionPracticeApp")
            if stage == "d2_post":
                timepoint = "after_break"
            elif self.activity_condition == "no_break":
                timepoint = "end_of_experiment"
            else:
                timepoint = "pre_break"
            self.frames["AttentionPracticeApp"].start_game(
                condition=self.activity_condition,
                timepoint=timepoint,
            )
        elif stage in ("pasat_pre", "pasat_post"):
            self.show_frame("PendingStagePage")
            timepoint = "before the break" if stage == "pasat_pre" else "after the break"
            self.frames["PendingStagePage"].show_stage(
                "PASAT (not implemented)",
                f"The PASAT test for {timepoint} will be added later. "
                "This placeholder is not a test.",
            )
        elif stage == "activity_break":
            self.show_frame("ActivityBreakPage")
            self.frames["ActivityBreakPage"].start_break(self.scheduled_activity)
        elif stage == "comprehension":
            self.show_frame("PendingStagePage")
            self.frames["PendingStagePage"].show_stage(
                "Comprehension test (not implemented)",
                "Reading questions will be loaded from the multilingual dataset later. "
                "This placeholder is not a test.",
            )
        elif stage == "post_survey":
            self.show_frame("PostTestPage")
        elif stage == "results":
            self.show_frame("ResultsPage")
        else:
            raise RuntimeError(f"Unknown session stage: {stage}")

    def game_finished(self):
        """Advance after a timed stage or an explicit placeholder continuation."""
        if self.current_stage is None or self.current_stage == "results":
            raise RuntimeError("Cannot advance because no session stage is active.")
        self.start_next_stage()

    def start_next_game(self):
        """Keep the legacy continue page compatible with this controller."""
        self.game_finished()
