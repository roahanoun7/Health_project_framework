"""Load a participant's scheduled activity and profile for one session."""

from dataclasses import dataclass
from pathlib import Path

import yaml
from openpyxl import load_workbook

from game_pages.session_flow import ACTIVITY_LABELS, normalize_activity


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"
PARTICIPANT_HEADERS = tuple(f"Participant {number}" for number in range(1, 7))


@dataclass(frozen=True)
class SessionAssignment:
    participant_name: str
    participant_number: int
    language: str
    week: int
    session: int
    activity: str
    activity_label: str


def _resolve_path(config_path: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Configured data paths must be non-empty strings.")
    path = Path(value)
    return path if path.is_absolute() else config_path.parent / path


def load_session_assignment(
    schedule_path: Path,
    participants_path: Path,
    participant_name: str,
    session_number: int,
) -> SessionAssignment:
    with participants_path.open(encoding="utf-8") as participants_file:
        participants_config = yaml.safe_load(participants_file)

    if not isinstance(participants_config, dict):
        raise ValueError(f"{participants_path} must contain a YAML mapping.")
    participants = participants_config.get("participants")
    if not isinstance(participants, dict):
        raise ValueError(
            f"{participants_path} must contain a 'participants' mapping."
        )

    profiles = {}
    participant_numbers = set()
    for name, profile in participants.items():
        if not isinstance(profile, dict):
            raise ValueError(f"Roster entry for {name!r} must be a mapping.")
        try:
            participant_number = int(profile["participant"])
            language = str(profile["language"]).strip()
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"Roster entry for {name!r} needs a participant number and language."
            ) from error
        if participant_number not in range(1, 7):
            raise ValueError("Roster participant numbers must be between 1 and 6.")
        if participant_number in participant_numbers:
            raise ValueError(
                f"Roster assigns Participant {participant_number} more than once."
            )
        if not language:
            raise ValueError(f"Roster entry for {name!r} has no language.")
        participant_numbers.add(participant_number)

        canonical_name = str(profile.get("name", name)).strip()
        if not canonical_name:
            raise ValueError(f"Roster entry for {name!r} has no display name.")
        normalized_name = str(name).strip().casefold()
        if not normalized_name or normalized_name in profiles:
            raise ValueError(f"Roster contains an empty or duplicate name: {name!r}.")
        profiles[normalized_name] = (
            canonical_name,
            participant_number,
            language,
        )

    profile = profiles.get(participant_name.strip().casefold())
    if profile is None:
        raise ValueError(f"Participant {participant_name!r} is not in the roster.")
    canonical_name, participant_number, language = profile

    workbook = load_workbook(schedule_path, data_only=True, read_only=True)
    try:
        if "Schedule" not in workbook.sheetnames:
            raise ValueError(f"{schedule_path} must contain a 'Schedule' sheet.")
        sheet = workbook["Schedule"]
        rows = sheet.iter_rows(values_only=True)
        try:
            headers = next(rows)
        except StopIteration as error:
            raise ValueError(f"{schedule_path} has an empty Schedule sheet.") from error

        header_indexes = {
            str(value).strip(): index
            for index, value in enumerate(headers)
            if value is not None
        }
        required_headers = ("Week", "Session", *PARTICIPANT_HEADERS)
        missing_headers = [
            header for header in required_headers if header not in header_indexes
        ]
        if missing_headers:
            raise ValueError(
                f"Schedule is missing required columns: {', '.join(missing_headers)}."
            )

        session_row = None
        for row in rows:
            raw_session = row[header_indexes["Session"]]
            if raw_session is None:
                continue
            try:
                row_session = int(raw_session)
            except (TypeError, ValueError) as error:
                if row[header_indexes["Week"]] is None:
                    continue
                raise ValueError(
                    f"Invalid session number in schedule: {raw_session!r}."
                ) from error
            if row_session == session_number:
                if session_row is not None:
                    raise ValueError(f"Schedule contains duplicate session {session_number}.")
                session_row = row

        if session_row is None:
            raise ValueError(f"Session {session_number} is not present in the schedule.")

        try:
            week = int(session_row[header_indexes["Week"]])
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Session {session_number} has an invalid week number."
            ) from error

        raw_activity = session_row[
            header_indexes[PARTICIPANT_HEADERS[participant_number - 1]]
        ]
        if raw_activity is None:
            raise ValueError(
                f"Session {session_number} has no activity for Participant "
                f"{participant_number}."
            )
        try:
            activity = normalize_activity(str(raw_activity))
        except ValueError as error:
            raise ValueError(
                f"Unsupported scheduled activity for session {session_number}, "
                f"Participant {participant_number}: {raw_activity!r}."
            ) from error
        activity_label = ACTIVITY_LABELS[activity]

        return SessionAssignment(
            participant_name=canonical_name,
            participant_number=participant_number,
            language=language,
            week=week,
            session=session_number,
            activity=activity,
            activity_label=activity_label,
        )
    finally:
        workbook.close()


def load_session_assignment_from_config(
    participant_name: str,
    session_number: int,
    config_path: Path = CONFIG_PATH,
) -> SessionAssignment:
    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if not isinstance(config, dict):
        raise ValueError(f"{config_path} must contain a YAML mapping.")

    try:
        schedule_path = _resolve_path(config_path, config["break_schedule_path"])
        participants_path = _resolve_path(config_path, config["participants_path"])
    except KeyError as error:
        raise ValueError(
            f"{config_path} must define break_schedule_path and participants_path."
        ) from error

    return load_session_assignment(
        schedule_path,
        participants_path,
        participant_name,
        session_number,
    )
