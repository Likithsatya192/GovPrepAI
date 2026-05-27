"""Backward-compatible exports for the standalone agent runner functions."""

from app.agents.runners import (
    GovPrepAgentRunners,
    run_current_affairs_agent,
    run_mock_test_agent,
    run_question_bank_agent,
    run_study_plan_agent,
    run_syllabus_navigator,
    run_weak_topic_agent,
)

__all__ = [
    "GovPrepAgentRunners",
    "run_syllabus_navigator",
    "run_question_bank_agent",
    "run_current_affairs_agent",
    "run_mock_test_agent",
    "run_weak_topic_agent",
    "run_study_plan_agent",
]

