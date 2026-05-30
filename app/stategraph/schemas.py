"""Plan-and-execute state schemas."""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from app.core.exam_types import ExamType
StepStatus = Literal["pending", "done", "failed"]


class Step(TypedDict):
    """Single executable planner step."""

    step_id: int
    agent: str
    instruction: str
    status: StepStatus
    result: str | None


class GovPrepState(TypedDict):
    """State shared by planner, executor, replanner, and synthesizer."""

    user_goal: str
    user_id: str
    exam_type: ExamType
    plan: list[Step]
    current_step_index: int
    completed_results: list[dict]
    final_output: str | None
    replan_count: int
    error: str | None
    notes_context: NotRequired[str]
