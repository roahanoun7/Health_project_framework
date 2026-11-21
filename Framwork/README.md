# DSPH-DAVEY-CBS
Data Science Personal Health project with team D.A.V.E.Y. with the developed Cognitive Behavior Software.
The code is extracted from the original repo from DSPH class of 2025-2026 with the cognitive behavior game framework. 

## installation process:
### Requirements + config
First pip install the requirements from the `requirements.txt` file:

```
pip install -r requirements.txt
```

You need to create your own 'config.yaml' file inside the root directory folder
Example structure of the `config.yaml` file:

```
data_folder_path: 'path/to/folder/for/saving/experiment/data'
break_schedule_path: 'data/break_schedule.xlsx'
participants_path: 'participants.local.yaml'
```

The session schedule is stored at `data/break_schedule.xlsx`. Keep participant
names and language preferences in the local, git-ignored `participants.local.yaml`:

```
participants:
  example_user:
    name: Example User
    participant: 1
    language: Arabic
```

The app asks for the roster name and a session number from 1 to 24, then looks
up that participant's scheduled condition. The study session, PASAT, and
comprehension pages are currently placeholders pending the reading dataset and
PASAT implementation; do not use this flow for participant data collection yet.
The optional reading page accepts a pandas DataFrame from its caller; no
pickled dataset setup is required.

## Start game
After setting everything up, you then can run the game by calling: `Game.py` and try to play the game yourself.

## misc files

Session tables are appended as CSV files under `data_folder_path`.
Use `QA_score_grader.py` to grade answers from `read_df.csv`; scores are saved
to `main_df.csv`.

combine muse or polar data using the `get_csv_files.py`. currently only support for combining the muse athena data is implemented.  
