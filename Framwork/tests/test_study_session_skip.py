import unittest
from datetime import datetime
from types import SimpleNamespace

from game_pages.planned_pages import ActivityBreakPage, StudySessionPage


class FakeController:
    def __init__(self):
        self.timestamps = []
        self.finished_stages = 0
        self.reading_sections_read = 0

    def add_game_timestamp(self, timestamp):
        self.timestamps.append(timestamp)

    def game_finished(self):
        self.finished_stages += 1


class StudySessionTests(unittest.TestCase):
    def test_finish_records_elapsed_interval_and_advances_once(self):
        page = StudySessionPage.__new__(StudySessionPage)
        page.controller = FakeController()
        page.started_at = datetime.now().astimezone()
        page.timer_id = None
        page.active = True
        page.material = None

        page.finish_session()
        page.finish_session()

        self.assertFalse(page.active)
        self.assertEqual(len(page.controller.timestamps), 1)
        self.assertEqual(page.controller.finished_stages, 1)

    def test_next_section_saves_progress_for_the_following_study_session(self):
        page = StudySessionPage.__new__(StudySessionPage)
        page.controller = FakeController()
        page.controller.reading_sections_read = 1
        page.material = SimpleNamespace(sections=("one", "two", "three"))
        page.section_index = 1
        page._show_section = lambda: None

        page.next_section()

        self.assertEqual(page.controller.reading_sections_read, 2)
        self.assertEqual(page.section_index, 2)


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
