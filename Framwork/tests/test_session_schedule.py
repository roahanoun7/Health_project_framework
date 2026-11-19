import tempfile
import unittest
from pathlib import Path

import yaml
from openpyxl import Workbook

from game_pages.session_schedule import load_session_assignment


class SessionScheduleTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.schedule_path = self.directory / "schedule.xlsx"
        self.participants_path = self.directory / "participants.yaml"

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Schedule"
        sheet.append(
            [
                "Week",
                "Session",
                "Participant 1",
                "Participant 2",
                "Participant 3",
                "Participant 4",
                "Participant 5",
                "Participant 6",
            ]
        )
        sheet.append(
            [
                1,
                1,
                "Doomscrolling",
                "Walking",
                "Walking",
                "No break",
                "No break",
                "Doomscrolling",
            ]
        )
        sheet.append([None, "No break", "8", "8", "8", "8", "8", "8"])
        workbook.save(self.schedule_path)
        workbook.close()

        self.participants_path.write_text(
            yaml.safe_dump(
                {
                    "participants": {
                        "Roa": {
                            "name": "ROA",
                            "participant": 1,
                            "language": "Arabic",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_lookup_is_case_insensitive_and_returns_scheduled_activity(self):
        assignment = load_session_assignment(
            self.schedule_path, self.participants_path, "roa", 1
        )
        self.assertEqual(assignment.participant_name, "ROA")
        self.assertEqual(assignment.participant_number, 1)
        self.assertEqual(assignment.language, "Arabic")
        self.assertEqual(assignment.week, 1)
        self.assertEqual(assignment.activity, "doomscrolling_break")
        self.assertEqual(assignment.activity_label, "Doomscrolling")

    def test_schedule_activity_labels_are_normalized(self):
        self.participants_path.write_text(
            yaml.safe_dump(
                {
                    "participants": {
                        "Roa": {
                            "participant": 2,
                            "language": "Arabic",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        walking = load_session_assignment(
            self.schedule_path, self.participants_path, "ROA", 1
        )
        self.assertEqual(walking.activity, "walking_break")
        self.assertEqual(walking.activity_label, "Walking")
        self.participants_path.write_text(
            yaml.safe_dump(
                {
                    "participants": {
                        "Roa": {
                            "participant": 4,
                            "language": "Arabic",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        no_break = load_session_assignment(
            self.schedule_path, self.participants_path, "ROA", 1
        )
        self.assertEqual(no_break.activity, "no_break")
        self.assertEqual(no_break.activity_label, "No break")

    def test_unknown_participant_is_reported(self):
        with self.assertRaisesRegex(ValueError, "is not in the roster"):
            load_session_assignment(
                self.schedule_path, self.participants_path, "Unknown", 1
            )

    def test_unknown_session_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Session 2 is not present"):
            load_session_assignment(
                self.schedule_path, self.participants_path, "ROA", 2
            )


if __name__ == "__main__":
    unittest.main()
