"""API request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.core.exam_types import ExamType, normalize_exam_type


class ExamTypeModel(BaseModel):
    """Base model that accepts common exam aliases but stores canonical labels."""

    exam_type: ExamType

    @field_validator("exam_type", mode="before")
    @classmethod
    def normalize_exam_type(cls, value: object) -> ExamType:
        return normalize_exam_type(value)


class GovPrepRequest(ExamTypeModel):
    """Full plan-and-execute request body."""

    goal: str = Field(..., min_length=3)
    user_id: str = "default"


class ExamTypeRequest(ExamTypeModel):
    """Request body for exam-only direct endpoints."""


class MockTestRequest(ExamTypeModel):
    """Request body for direct mock generation."""

    topic: str = Field(..., min_length=1)


class StudyPlanRequest(ExamTypeModel):
    """Request body for direct study-plan generation."""

    target_date: str = Field(..., min_length=4)
    weak_topics: list[str] = Field(default_factory=list)


class UploadNotesResponse(BaseModel):
    """Response returned after user notes are indexed."""

    user_id: str
    chunk_count: int
