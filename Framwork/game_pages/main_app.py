# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import random
from datetime import datetime
from tkinter import ttk
from typing import Optional
from game_pages.between_page import BetweenGamesPage
from game_pages.intro_page import IntroPage
from Games.D2 import AttentionPracticeApp
from Games.PASAT_Breakpoint.pasat import PasatPage
from game_pages.planned_pages import ActivityBreakPage, PendingStagePage, StudySessionPage
from game_pages.post_test_page import PostTestPage
from game_pages.reading_material import ReadingMaterial, load_reading_material
from game_pages.reading_page import ReadingPage
from game_pages.results_page import ResultsPage
from game_pages.session_flow import build_session_flow, pasat_metadata_for_stage
from game_pages.session_schedule import load_session_assignment_from_config

FONT = ("Helvetica", 14)
HEADER_FONT = ("Helvetica", 24, "bold")
BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
THEMES = {
    "dark": {
        "background": "#0f172a",
        "foreground": "#e2e8f0",
        "surface": "#1e293b",
        "surface_alt": "#334155",
        "button": "#38bdf8",
        "button_foreground": "#06202e",
        "hover": "#7dd3fc",
        "hover_foreground": "#06202e",
        "border": "#334155",
        "separator": "#334155",
        "input": "#1e293b",
        "input_foreground": "#e2e8f0",
        "muted": "#94a3b8",
        "accent": "#38bdf8",
    },
    "light": {
        "background": "#f1f5f9",
        "foreground": "#0f172a",
        "surface": "#ffffff",
        "surface_alt": "#e2e8f0",
        "button": "#0ea5e9",
        "button_foreground": "#082f49",
        "hover": "#38bdf8",
        "hover_foreground": "#082f49",
        "border": "#94a3b8",
        "separator": "#cbd5e1",
        "input": "#ffffff",
        "input_foreground": "#0f172a",
        "muted": "#64748b",
        "accent": "#0284c7",
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
        self.QA_done = 0
        self.game_timestamps = {}
        self.pasat_results = {}
        self.all_sequence_answers = {} # this is can be used for Pasat test, but not work yet
        self.reading_QA_results = []
        self.reading_material: Optional[ReadingMaterial] = None
        self.reading_sections_read = 0

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
            ReadingPage,
            PasatPage,
        ):
            if F is AttentionPracticeApp:
                page = F(container, self, rounds=3)
            elif F is PasatPage:
                page = F(
                    container,
                    self,
                    results_dir=self.frames["ResultsPage"].dataframe_folder_path,
                )
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
            font=("Helvetica", 12, "bold"),
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
                foreground=(
                    colors["accent"]
                    if label_style == "Title.TLabel"
                    else colors["foreground"]
                ),
            )
        style.configure(
            "Card.TFrame",
            background=colors["surface"],
        )
        style.configure(
            "Card.TLabel",
            background=colors["surface"],
            foreground=colors["foreground"],
        )
        style.configure(
            "Card.TCheckbutton",
            background=colors["surface"],
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
            background=colors["surface"],
            fieldbackground=colors["surface"],
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
        if isinstance(widget, PasatPage):
            return
        role = getattr(widget, "_theme_role", None)
        parent_background = (
            getattr(widget.master, "_theme_background", None)
            if widget.master is not None
            else None
        ) or colors["background"]
        child_background = (
            colors["surface"] if role == "card" else parent_background
        )

        if role == "separator":
            widget.configure(bg=colors["separator"])
        elif isinstance(widget, (tk.Frame, tk.Canvas)):
            widget.configure(bg=child_background)
        elif isinstance(widget, tk.Label):
            widget.configure(
                bg=child_background,
                fg=colors["accent"] if role == "title" else colors["foreground"],
            )
        elif isinstance(widget, (tk.Radiobutton, tk.Checkbutton)):
            widget.configure(
                bg=child_background,
                fg=colors["foreground"],
                activebackground=child_background,
                activeforeground=colors["foreground"],
                selectcolor=colors["surface_alt"],
            )
        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=colors["button"],
                fg=colors["button_foreground"],
                activebackground=colors["hover"],
                activeforeground=colors["hover_foreground"],
                highlightbackground=colors["border"],
                font=("Helvetica", 12, "bold"),
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
        elif isinstance(widget, tk.Text):
            widget.configure(
                bg=parent_background,
                fg=colors["foreground"],
                insertbackground=colors["foreground"],
                selectbackground=colors["hover"],
                selectforeground=colors["hover_foreground"],
                relief="flat",
            )

        widget._theme_background = child_background
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

    def add_pasat_result(self, result):
        """Store summary metrics for the active PASAT session stage."""
        if self.current_stage not in ("pasat_pre", "pasat_post"):
            raise RuntimeError("Cannot record PASAT results outside a PASAT stage.")
        self.pasat_results[self.current_stage] = result

    def begin_session(self, participant_name, session_number):
        """Resolve the schedule assignment and start the first study session."""
        assignment = load_session_assignment_from_config(
            participant_name, session_number
        )
        self.reading_material = load_reading_material(
            assignment.language,
            data_directory=self.frames["ResultsPage"].dataframe_folder_path,
        )
        self.reading_sections_read = 0
        self.participant_name.set(assignment.participant_name)
        self.participant_id = f"Participant {assignment.participant_number}"
        self.participant_language = assignment.language
        self.session_number = assignment.session
        self.week_number = assignment.week
        self.scheduled_activity = assignment.activity_label
        self.activity_condition = assignment.activity
        self.game_timestamps = {}
        self.pasat_results = {}
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
            if self.reading_material is None:
                raise RuntimeError(
                    "Reading material must be loaded before a study session."
                )
            self.show_frame("StudySessionPage")
            session_number = 1 if stage == "study_1" else 2
            self.frames["StudySessionPage"].start_session(
                f"Study session {session_number}",
                self.reading_material,
                self.reading_sections_read,
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
            self.show_frame("PasatPage")
            condition, timepoint = pasat_metadata_for_stage(
                self.activity_condition, stage
            )
            self.frames["PasatPage"].start_session(
                participant_id=self.participant_id,
                session=self.session_number,
                condition=condition,
                timepoint=timepoint,
            )
        elif stage == "activity_break":
            self.show_frame("ActivityBreakPage")
            self.frames["ActivityBreakPage"].start_break(self.scheduled_activity)
        elif stage == "comprehension":
            if self.reading_material is None:
                raise RuntimeError(
                    "Reading material must be loaded before the comprehension stage."
                )
            self.show_frame("ReadingPage")
            self.frames["ReadingPage"].start_game(
                self.reading_material,
                self.reading_sections_read,
            )
        elif stage == "post_survey":
            self.show_frame("PostTestPage")
        elif stage == "results":
            self.show_frame("ResultsPage")
        else:
            raise RuntimeError(f"Unknown session stage: {stage}")

    def game_finished(self):
        """Advance after the active timed or interactive stage."""
        if self.current_stage is None or self.current_stage == "results":
            raise RuntimeError("Cannot advance because no session stage is active.")
        self.start_next_stage()

    def start_next_game(self):
        """Keep the legacy continue page compatible with this controller."""
        self.game_finished()
