"""Supported exam-type helpers."""

from __future__ import annotations

from typing import Literal


ExamType = Literal["SSC", "Banking", "GATE CS/IT", "GATE DA", "RRB"]
SUPPORTED_EXAMS: tuple[ExamType, ...] = ("SSC", "Banking", "GATE CS/IT", "GATE DA", "RRB")


def normalize_exam_type(value: object) -> ExamType:
    """Normalize common UI/user exam labels to the canonical supported values."""

    if not isinstance(value, str):
        raise ValueError("exam_type must be a string")

    normalized = " ".join(value.strip().split()).lower()
    compact = (
        normalized.replace("/", " ")
        .replace("-", " ")
        .replace("_", " ")
        .replace("&", " and ")
    )
    compact = " ".join(compact.split())

    aliases: dict[str, ExamType] = {
        "ssc": "SSC",
        "banking": "Banking",
        "bank": "Banking",
        "gate cs it": "GATE CS/IT",
        "gate cs": "GATE CS/IT",
        "gate cse": "GATE CS/IT",
        "gate it": "GATE CS/IT",
        "gate computer science": "GATE CS/IT",
        "gate information technology": "GATE CS/IT",
        "gate da": "GATE DA",
        "gate data science": "GATE DA",
        "gate ai": "GATE DA",
        "gate artificial intelligence": "GATE DA",
        "rrb": "RRB",
        "railway": "RRB",
        "railways": "RRB",
    }
    if compact in aliases:
        return aliases[compact]

    for exam_type in SUPPORTED_EXAMS:
        if value.strip() == exam_type:
            return exam_type

    supported = ", ".join(SUPPORTED_EXAMS)
    raise ValueError(f"Unsupported exam_type {value!r}. Supported values: {supported}")


def infer_exam_type(text: str) -> ExamType | None:
    """Infer a supported exam type from user text when it is explicitly mentioned."""

    normalized = text.lower()
    if "ssc" in normalized or "cgl" in normalized or "chsl" in normalized:
        return "SSC"
    if any(keyword in normalized for keyword in ("banking", "ibps", "sbi", "rbi")):
        return "Banking"
    if "gate" in normalized and any(
        keyword in normalized
        for keyword in (" da", "data science", "artificial intelligence", "ai")
    ):
        return "GATE DA"
    if "gate" in normalized and any(
        keyword in normalized
        for keyword in ("cs", "cse", "computer science", "it", "information technology")
    ):
        return "GATE CS/IT"
    if "rrb" in normalized or "railway" in normalized or "railways" in normalized:
        return "RRB"
    return None


def resolve_exam_type(requested_exam: ExamType, text: str) -> tuple[ExamType, bool]:
    """Use explicit user text over a conflicting selected exam value."""

    inferred_exam = infer_exam_type(text)
    if inferred_exam is not None and inferred_exam != requested_exam:
        return inferred_exam, True
    return requested_exam, False
