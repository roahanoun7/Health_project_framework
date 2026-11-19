"""Schedule-driven page order for one participant session."""

ACTIVITY_LABELS = {
    "no_break": "No break",
    "walking_break": "Walking",
    "doomscrolling_break": "Doomscrolling",
}


def normalize_activity(activity: str) -> str:
    normalized = activity.strip().casefold().replace(" ", "_")
    if normalized in ACTIVITY_LABELS:
        return normalized
    activities = {
        "no_break": "no_break",
        "walking": "walking_break",
        "doomscrolling": "doomscrolling_break",
    }
    try:
        return activities[normalized]
    except KeyError as error:
        raise ValueError(f"Unsupported scheduled activity: {activity!r}") from error


def build_session_flow(activity: str) -> tuple[str, ...]:
    condition = normalize_activity(activity)
    if condition == "no_break":
        return (
            "study_1",
            "d2_pre",
            "pasat_pre",
            "comprehension",
            "post_survey",
            "results",
        )

    return (
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
    )
