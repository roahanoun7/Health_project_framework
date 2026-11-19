# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import yaml
import numpy as np
import pandas as pd
import os
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


# ---------- Configuration ----------
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'


# ---------- Results Page (non-editable) ----------
class ResultsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        tk.Label(self, text='Results', font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)
        self.results_label = tk.Label(self, text='', font=('Courier', 11), justify='left', bg=BG_COLOR, fg=FG_COLOR)
        self.results_label.pack(pady=6)
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text='Save results', command=self.save_results,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(side='left', padx=6)

        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        self.dataframe_folder_path = config["data_folder_path"]
        if not os.path.exists(self.dataframe_folder_path):
            print("Missing experiment_data folder, creating folder")
            os.makedirs(self.dataframe_folder_path)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_results()

    def display_results(self):
        s = (
            f"Session complete. Thank you, "
            f"{self.controller.participant_name.get().strip()}!\n"
            f"Week {self.controller.week_number}, session "
            f"{self.controller.session_number}: "
            f"{self.controller.scheduled_activity}.\n"
            "Press Save results to save and exit."
        )
        self.results_label.config(text=s)

    def save_results(self):
        """saves results of all the games, uses pandas to save all the scores, appends data to already existing dataframe if it already exists in given folder path"""
        participant_name = self.controller.participant_name.get().strip()
        questionnaire_answers = self.controller.questionnaire_answers
        post_test_answers = self.controller.post_test_answers

        digit_forw_score = self.controller.digit_forward_score
        digit_backw_score = self.controller.digit_backward_score
        all_sequence_answers = self.controller.all_sequence_answers

        d2_results = self.controller.d2_results

        QA_score = self.controller.QA_done
        reading_QA_results = self.controller.reading_QA_results

        date_time = self.controller.date_time
        random_seed = self.controller.random_seed
        game_timestamps = self.controller.game_timestamps

        # ======== main df ========
        main_data = {
            'participant_name': participant_name,
            'participant_id': self.controller.participant_id,
            'participant_language': self.controller.participant_language,
            'week': self.controller.week_number,
            'session': self.controller.session_number,
            'scheduled_activity': self.controller.scheduled_activity,
            'date_time': pd.to_datetime(date_time),
            'seed': random_seed,
            **questionnaire_answers,
            **post_test_answers,
            'digit_forward_score': digit_forw_score,
            'digit_backward_score': digit_backw_score,
            **d2_results,
            'QA_done': QA_score,
            'QA_score': np.nan
        }
        main_df = pd.DataFrame([main_data])
        main_df.set_index(['participant_name', 'date_time'], inplace=True)
   
        # ======== game times df ========
        all_games = []
        for game in game_timestamps:
            for times in game_timestamps[game]:
                digit_data = {'participant_name': participant_name, 'date_time': pd.to_datetime(date_time), "game_type": game, "start_time": pd.to_datetime(times[0]), "end_time": pd.to_datetime(times[1])}
                all_games.append(digit_data)

        games_times_df = pd.DataFrame(all_games)
        if not games_times_df.empty:
            games_times_df.set_index(['participant_name', 'date_time'], inplace=True)

        # ======== digit span df ========
        digit_counter = 0
        all_sequences = []
        for sequence_type in all_sequence_answers:
            for answer in all_sequence_answers[sequence_type]:
                digit_data = {'participant_name': participant_name, 'date_time': pd.to_datetime(date_time), "digit_id": digit_counter, "sequence_type": sequence_type, "answer_time": answer[0], "correct_sequence": answer[1], "answered_sequence": answer[2], "correct": answer[3]}
                all_sequences.append(digit_data)
            digit_counter += 1

        digit_span_df = pd.DataFrame(all_sequences)
        if not digit_span_df.empty:
            digit_span_df.set_index(['participant_name', 'date_time'], inplace=True)

        # ======== reading df ========
        all_reading = []
        for result in reading_QA_results:
            reading_data = {'participant_name': participant_name, 'date_time': pd.to_datetime(date_time), 'context_id': result['context_id'], 'question': result['question'], 'correct_answer': result['correct_answer'], 'player_answer': result['player_answer'], 'show_question': pd.to_datetime(result['show_question'])}
            all_reading.append(reading_data)

        read_df = pd.DataFrame(all_reading)
        if not read_df.empty:
            read_df.set_index(['participant_name', 'date_time'], inplace=True)

        # ======== add start-end timestamps to main df ========
        for index in games_times_df.index.unique():
            participant_times = games_times_df.loc[index]
            for game_type in participant_times["game_type"].unique():
                stage_times = participant_times.loc[
                    participant_times["game_type"] == game_type
                ]
                start = stage_times.iloc[0]["start_time"]
                end = stage_times.iloc[-1]["end_time"]
                main_df.loc[index, game_type + " start"] = pd.to_datetime(start)
                main_df.loc[index, game_type + " end"] = pd.to_datetime(end)

        self.save_df(main_df, 'main_df')
        self.save_df(games_times_df, "games_times_df")
        self.save_df(digit_span_df, "digit_span_df")
        self.save_df(read_df, "read_df")

        self.quit_app()

    def save_df(self, df, name):
        """helper function to save and append new dataframe to already existing dataframe"""
        if len(df) == 0:
            return
        df_path = os.path.join(self.dataframe_folder_path, f'{name}.pkl')
        if os.path.exists(df_path):
            print(f"already an existing with the name: {name}.pkl, combining dataframes")
            existing_df = pd.read_pickle(df_path)
            df = pd.concat([df, existing_df])
        df.sort_index(inplace=True)
        df.to_pickle(df_path)

    def quit_app(self):
        self.master.quit()