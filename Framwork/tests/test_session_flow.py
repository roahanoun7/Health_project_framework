import unittest

from game_pages.session_flow import build_session_flow, normalize_activity


class SessionFlowTests(unittest.TestCase):
    def test_no_break_skips_activity_break_and_second_study(self):
        self.assertEqual(
            build_session_flow("No break"),
            (
                "study_1",
                "d2_pre",
                "pasat_pre",
                "comprehension",
                "post_survey",
                "results",
            ),
        )

    def test_activity_break_repeats_reaction_tests_and_study(self):
        self.assertEqual(
            build_session_flow("Doomscrolling"),
            (
                "study_1",
                "d2_pre",
                "pasat_pre",
                "activity_break",
                "d2_post",
                "pasat_post",
                "study_2",
                "comprehension",
                "post_survey",
                "results",
            ),
        )

    def test_unknown_activity_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Unsupported scheduled activity"):
            normalize_activity("cycling")


if __name__ == "__main__":
    unittest.main()
