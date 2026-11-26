"""Load localized reading passages and their matching comprehension questions."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Union


DEFAULT_TOPIC_ID = "technology"
DEFAULT_DATA_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "Technology_5_Languages_Complete_80_Questions"
)
QUESTIONS_PER_SECTION = 2
QUESTIONS_TO_PRESENT_PER_SECTION = 1

LANGUAGE_CODES = {
    "ar": "ar",
    "arabic": "ar",
    "bn-bd": "bn-BD",
    "bangla": "bn-BD",
    "bengali": "bn-BD",
    "en": "en",
    "english": "en",
    "fa": "fa",
    "farsi": "fa",
    "persian": "fa",
    "nl": "nl",
    "dutch": "nl",
}

SECTION_HEADER_PATTERNS = {
    "ar": re.compile(r"(?m)^[ \t]*القسم\s+\d+\s*[:：]"),
    "bn-BD": re.compile(r"(?m)^[ \t]*অধ্যায়\s+\d+\s*[:：]"),
    "en": re.compile(r"(?mi)^[ \t]*Section\s+\d+\s*[:：]"),
    "fa": re.compile(r"(?m)^[ \t]*بخش\s+\d+\s*[:：]"),
    "nl": re.compile(r"(?mi)^[ \t]*Sectie\s+\d+\s*[:：]"),
}


@dataclass(frozen=True)
class ReadingQuestion:
    question_id: str
    section_number: int
    question: str
    options: tuple[str, ...]
    correct_option: int


@dataclass(frozen=True)
class ReadingMaterial:
    topic_id: str
    language_code: str
    title: str
    sections: tuple[str, ...]
    questions: tuple[ReadingQuestion, ...]


def _language_code(language: str) -> str:
    normalized_language = language.strip().casefold()
    try:
        return LANGUAGE_CODES[normalized_language]
    except KeyError as error:
        supported_languages = ", ".join(
            ("Arabic", "Bangla", "Dutch", "English", "Persian")
        )
        raise ValueError(
            f"Unsupported participant language {language!r}. "
            f"Supported languages are: {supported_languages}."
        ) from error


def _split_sections(content: str, language_code: str) -> tuple[str, ...]:
    matches = list(SECTION_HEADER_PATTERNS[language_code].finditer(content))
    if not matches or content[:matches[0].start()].strip():
        raise ValueError(
            f"Reading content for language {language_code!r} must start with "
            "a recognized section heading."
        )

    section_texts = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        section = content[match.start():end].strip()
        if not section:
            raise ValueError(
                f"Reading section {index + 1} for language {language_code!r} is empty."
            )
        section_texts.append(section)
    return tuple(section_texts)


def load_reading_material(
    language: str,
    topic_id: str = DEFAULT_TOPIC_ID,
    data_directory: Union[Path, str] = DEFAULT_DATA_DIRECTORY,
) -> ReadingMaterial:
    """Load a topic's reading sections and questions for the participant language."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", topic_id):
        raise ValueError(f"Invalid reading topic ID: {topic_id!r}.")

    language_code = _language_code(language)
    path = Path(data_directory) / f"{topic_id}_{language_code}.json"
    raw_material = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_material, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    if raw_material.get("language") != language_code:
        raise ValueError(
            f"{path} declares language {raw_material.get('language')!r}; "
            f"expected {language_code!r}."
        )

    reading = raw_material.get("reading")
    if not isinstance(reading, dict):
        raise ValueError(f"{path} must contain a 'reading' object.")
    title = reading.get("title")
    content = reading.get("content")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"{path} must contain a non-empty reading title.")
    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"{path} must contain non-empty reading content.")
    sections = _split_sections(content, language_code)

    raw_questions = raw_material.get("questions")
    if not isinstance(raw_questions, list):
        raise ValueError(f"{path} must contain a 'questions' list.")
    expected_question_count = len(sections) * QUESTIONS_PER_SECTION
    if len(raw_questions) != expected_question_count:
        raise ValueError(
            f"{path} has {len(raw_questions)} questions for {len(sections)} sections; "
            f"expected {expected_question_count}."
        )

    questions = []
    for index, raw_question in enumerate(raw_questions):
        if not isinstance(raw_question, dict):
            raise ValueError(f"Question {index + 1} in {path} must be a JSON object.")
        question_id = raw_question.get("id")
        question_text = raw_question.get("question")
        options = raw_question.get("options")
        correct_option = raw_question.get("correct_option")
        if not isinstance(question_id, str) or not question_id.strip():
            raise ValueError(f"Question {index + 1} in {path} has no ID.")
        if not isinstance(question_text, str) or not question_text.strip():
            raise ValueError(f"Question {question_id!r} in {path} has no text.")
        if (
            not isinstance(options, list)
            or len(options) < 2
            or not all(isinstance(option, str) and option.strip() for option in options)
        ):
            raise ValueError(
                f"Question {question_id!r} in {path} must have at least two "
                "non-empty answer options."
            )
        if (
            not isinstance(correct_option, int)
            or isinstance(correct_option, bool)
            or correct_option not in range(1, len(options) + 1)
        ):
            raise ValueError(
                f"Question {question_id!r} in {path} has an invalid correct_option."
            )
        questions.append(
            ReadingQuestion(
                question_id=question_id,
                section_number=index // QUESTIONS_PER_SECTION + 1,
                question=question_text,
                options=tuple(options),
                correct_option=correct_option,
            )
        )

    return ReadingMaterial(
        topic_id=str(raw_material.get("topic_id", topic_id)),
        language_code=language_code,
        title=title.strip(),
        sections=sections,
        questions=tuple(questions),
    )


def questions_for_sections(
    material: ReadingMaterial,
    sections_read: int,
) -> tuple[ReadingQuestion, ...]:
    """Return the first question for each section the participant read."""
    if (
        not isinstance(sections_read, int)
        or isinstance(sections_read, bool)
        or sections_read not in range(1, len(material.sections) + 1)
    ):
        raise ValueError(
            f"sections_read must be between 1 and {len(material.sections)}."
        )
    question_count = sections_read * QUESTIONS_TO_PRESENT_PER_SECTION
    return material.questions[::QUESTIONS_PER_SECTION][:question_count]
