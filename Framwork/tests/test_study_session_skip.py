import unittest
from datetime import datetime

from game_pages.planned_pages import ActivityBreakPage, StudySessionPage


class FakeController:
    def __init__(self):
        self.timestamps = []
        self.finished_stages = 0

    def add_game_timestamp(self, timestamp):
        self.timestamps.append(timestamp)

    def game_finished(self):
        self.finished_stages += 1


class StudySessionSkipTests(unittest.TestCase):
    def test_skip_records_elapsed_interval_and_advances_once(self):
        page = StudySessionPage.__new__(StudySessionPage)
        page.controller = FakeController()
        page.started_at = datetime.now().astimezone()
        page.timer_id = None
        page.active = True

        page.skip_session()
        page.skip_session()

        self.assertFalse(page.active)
        self.assertEqual(len(page.controller.timestamps), 1)
        self.assertEqual(page.controller.finished_stages, 1)


class ActivityBreakSkipTests(unittest.TestCase):
    def test_skip_records_elapsed_interval_and_advances_once(self):
        page = ActivityBreakPage.__new__(ActivityBreakPage)
        page.controller = FakeController()
        page.started_at = datetime.now().astimezone()
        page.timer_id = None
        page.active = True

        page.skip_break()
        page.skip_break()

        self.assertFalse(page.active)
        self.assertEqual(len(page.controller.timestamps), 1)
        self.assertEqual(page.controller.finished_stages, 1)


if __name__ == "__main__":
    unittest.main()
