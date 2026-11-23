import json
import tempfile
import unittest
from pathlib import Path

from game_pages.reading_material import (
    load_reading_material,
    questions_for_sections,
)


class ReadingMaterialTests(unittest.TestCase):
    def test_loads_each_roster_language_and_pairs_two_questions_per_section(self):
        language_names = ("Arabic", "Bangla", "Dutch", "English", "Persian")
        expected_codes = ("ar", "bn-BD", "nl", "en", "fa")

        for language, expected_code in zip(language_names, expected_codes):
            with self.subTest(language=language):
                material = load_reading_material(language)
                self.assertEqual(material.language_code, expected_code)
                self.assertEqual(len(material.sections), 40)
                self.assertEqual(len(material.questions), 80)
                self.assertEqual(material.questions[0].section_number, 1)
                self.assertEqual(material.questions[-1].section_number, 40)

    def test_three_sections_select_six_matching_questions(self):
        material = load_reading_material("English")

        questions = questions_for_sections(material, 3)

        self.assertEqual(len(questions), 6)
        self.assertEqual(
            [question.section_number for question in questions],
            [1, 1, 2, 2, 3, 3],
        )

    def test_rejects_an_unsupported_language(self):
        with self.assertRaisesRegex(ValueError, "Unsupported participant language"):
            load_reading_material("Klingon")

    def test_rejects_question_count_that_does_not_match_section_count(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "technology_en.json"
            path.write_text(
                json.dumps(
                    {
                        "topic_id": "technology",
                        "language": "en",
                        "reading": {
                            "title": "Technology",
                            "content": "Section 1: Introduction\n\nReading text.",
                        },
                        "questions": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "expected 2"):
                load_reading_material(
                    "English",
                    data_directory=Path(temporary_directory),
                )


if __name__ == "__main__":
    unittest.main()
