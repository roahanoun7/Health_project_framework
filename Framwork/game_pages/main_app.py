# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import random
from datetime import datetime
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


# ---------- Main Application ----------
class App(tk.Tk):
    """Main application of the game, controlls the states of the game, also saves all the scores of the games"""
    def __init__(self):
        """create instanses of all scores and other necessary game variables, creates seed using datetime, loads in IntroPage always"""
        super().__init__()
        self.title('Mental Performance Test')
        self.configure(bg=BG_COLOR)
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
        self.digit_forward_score = 0
        self.digit_backward_score = 0
        self.d2_results = {}
        self.QA_done = 0
        self.game_timestamps = {}
        self.all_sequence_answers = {}
        self.reading_QA_results = []

        self.date_time = datetime.now().isoformat()
        self.random_seed = self.date_time
        random.seed(self.random_seed)

        self.flow = ()
        self.current_stage_index = -1
        self.current_stage = None

        # Container frame (use tk.Frame so bg applies consistently)
        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill='both', expand=True)

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
                page = F(container, self, rounds=1)
            else:
                page = F(container, self)
            self.frames[F.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

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
