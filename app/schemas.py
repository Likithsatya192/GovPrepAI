"""API request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ExamType = Literal["SSC", "Banking", "GATE CS/IT", "GATE DA", "RRB"]


class GovPrepRequest(BaseModel):
    """Full plan-and-execute request body."""

    goal: str = Field(..., min_length=3)
    exam_type: ExamType
    user_id: str = "default"


class ExamTypeRequest(BaseModel):
    """Request body for exam-only direct endpoints."""

    exam_type: ExamType


class MockTestRequest(BaseModel):
    """Request body for direct mock generation."""

    exam_type: ExamType
    topic: str = Field(..., min_length=1)


class StudyPlanRequest(BaseModel):
    """Request body for direct study-plan generation."""

    exam_type: ExamType
    target_date: str = Field(..., min_length=4)
    weak_topics: list[str] = Field(default_factory=list)


class UploadNotesResponse(BaseModel):
    """Response returned after user notes are indexed."""

    user_id: str
    chunk_count: int
