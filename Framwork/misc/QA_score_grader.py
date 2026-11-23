# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

"""
QA_score_grader.py gathers tests whose QA answers have not been graded yet.
Human review is needed because answer wording and typos can make automatic
grading unreliable.

Scores are saved to main_df.csv. Set a test's QA_score to numpy.nan to grade it again.
"""

from pathlib import Path

import pandas as pd
import numpy as np
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"
# Read the configured data folder and build paths to the grading input files.
with CONFIG_PATH.open(encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

data_folder_path = Path(config["data_folder_path"])
if not data_folder_path.is_absolute():
    data_folder_path = CONFIG_PATH.parent / data_folder_path
df_path_read = data_folder_path / "read_df.csv"
df_path_main = data_folder_path / "main_df.csv"

print(df_path_main)
print(df_path_read)
print()

# Stop with an error message if either required CSV file is missing.
if not df_path_read.exists():
    print("not exists: ",df_path_read)
if not df_path_main.exists():
    print("not exists: ",df_path_main)


if not df_path_read.exists() or not df_path_main.exists():
    print("df not correctly installed/couldnt find them. so cant make it work :(")
    raise SystemExit(1)

# Load the answer details and test summary, using participant and timestamp
# together to identify each test.
df_read = pd.read_csv(df_path_read, parse_dates=["date_time"])
df_read.set_index(["participant_name", "date_time"], inplace=True)
df_main = pd.read_csv(df_path_main, parse_dates=["date_time"])
df_main.set_index(["participant_name", "date_time"], inplace=True)

# Add a blank score column when this is the first time grading the tests.
if "QA_score" not in df_main.columns:
    df_main["QA_score"] =  np.nan

# Select tests whose QA scores are missing so they can be reviewed.
df_main_na = df_main["QA_score"].isna()
df_removed_na = df_main[df_main_na]


# Review each ungraded test and ask the reviewer whether each answer is correct.
for index, x in df_removed_na.iterrows():
    name = index[0]
    timestamp = index[1]

    # Count the test's correct answers; unmatched tests keep a score of zero.
    QA_score = 0
    if index in df_read.index:
        data = df_read.loc[[index]]
        for _, row in data.iterrows():
            print("Question:        ", row.question)
            print("Correct answer:  ", row.correct_answer)
            print("Player's answer: ", row.player_answer)
            print()
            
            response = ""
            while len(response) == 0:
                response = input("Y/N or yes/no if answer is correct or wrong:\n")
            
            if response.lower() == "y" or response.lower() == "yes":
                print("graded correct answer")
                QA_score += 1
            else:
                print("graded wrong answer")

            print("\n\n")

    # Save the updated score immediately, so completed grading is retained.
    print(f"QA score updated of the test on {timestamp}: ", QA_score)
    df_main.loc[index, "QA_score"] = QA_score
    df_main.to_csv(df_path_main)
    print("Updated dataframe with latest score")

    print("\n\n\n\n\n\n\n\n\n\n\n\n")

print("\n\n\n\n\n\n\n\n\n\n\n\n")
print("Done with grading the scores, thank you!")