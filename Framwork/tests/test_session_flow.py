import unittest

from game_pages.session_flow import (
    build_session_flow,
    normalize_activity,
    pasat_metadata_for_stage,
)


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

    def test_pasat_metadata_matches_activity_and_stage(self):
        self.assertEqual(
            pasat_metadata_for_stage("No break", "pasat_pre"),
            ("no_break", "final"),
        )
        self.assertEqual(
            pasat_metadata_for_stage("Walking", "pasat_pre"),
            ("walking", "pre_break"),
        )
        self.assertEqual(
            pasat_metadata_for_stage("Doomscrolling", "pasat_post"),
            ("doomscrolling", "post_break"),
        )

    def test_pasat_metadata_rejects_non_pasat_stage(self):
        with self.assertRaisesRegex(ValueError, "Unsupported PASAT stage"):
            pasat_metadata_for_stage("Walking", "activity_break")


if __name__ == "__main__":
    unittest.main()
