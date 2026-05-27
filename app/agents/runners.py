"""OOP agent runner implementation for GovPrepAI."""

from __future__ import annotations

import asyncio

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.prompts import (
    CURRENT_AFFAIRS_PROMPT,
    MOCK_TEST_PROMPT,
    QUESTION_BANK_PROMPT,
    STUDY_PLAN_PROMPT,
    SYLLABUS_NAVIGATOR_PROMPT,
    WEAK_TOPIC_PROMPT,
)


class GovPrepAgentRunners:
    """Runs all specialized preparation agents with async LLM calls."""

    async def safe_search(self, query: str) -> str:
        """Run DuckDuckGo search without letting search failures crash the app."""

        try:
            search = DuckDuckGoSearchRun()
            return await asyncio.to_thread(search.run, query)
        except Exception:
            return "Search unavailable"

    async def call_agent(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured Groq LLM asynchronously."""

        response = await get_llm().ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        return str(response.content)

    async def run_syllabus_navigator(self, instruction: str, exam_type: str) -> str:
        """Find and structure latest official syllabus, weights, and priorities."""

        search_result = await self.safe_search(
            f"{exam_type} latest official syllabus topic weightage"
        )
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Search evidence:
{search_result}

Return a clear syllabus map with:
- subjects
- topics and subtopics
- expected weightage or marks distribution
- priority ranking
- official-source caveats where needed
"""
        return await self.call_agent(SYLLABUS_NAVIGATOR_PROMPT, prompt)

    async def run_question_bank_agent(self, instruction: str, exam_type: str) -> str:
        """Analyze previous-year patterns and generate practice questions."""

        search_result = await self.safe_search(
            f"{exam_type} previous year question pattern PYQ analysis"
        )
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Search evidence:
{search_result}

Generate 10 practice questions with answers and brief explanations across high-weightage topics.
Match the discovered pattern, section style, and difficulty as closely as possible.
"""
        return await self.call_agent(QUESTION_BANK_PROMPT, prompt)

    async def run_current_affairs_agent(self, instruction: str, exam_type: str) -> str:
        """Curate exam-relevant current affairs."""

        search_result = await self.safe_search(
            f"latest current affairs important for {exam_type} exam"
        )
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Search evidence:
{search_result}

Filter for high-probability exam relevance only. Include concise explanations and probable sections.
"""
        return await self.call_agent(CURRENT_AFFAIRS_PROMPT, prompt)

    async def run_mock_test_agent(self, instruction: str, exam_type: str) -> str:
        """Generate a 20-question exam-style mock test."""

        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Create a 20-question mock test spanning all major subjects. For each question include:
- question
- four options
- correct answer
- explanation
- topic tag
"""
        return await self.call_agent(MOCK_TEST_PROMPT, prompt)

    async def run_weak_topic_agent(self, instruction: str, exam_type: str) -> str:
        """Identify weak topics and generate targeted revision material."""

        prompt = f"""
Exam: {exam_type}
Instruction and prior context:
{instruction}

Identify low-coverage or weak topics, then create focused revision notes, common traps, and mnemonics.
"""
        return await self.call_agent(WEAK_TOPIC_PROMPT, prompt)

    async def run_study_plan_agent(self, instruction: str, exam_type: str) -> str:
        """Create a day-wise timetable with revision and mock-test cycles."""

        prompt = f"""
Exam: {exam_type}
Instruction and planning context:
{instruction}

Create a realistic timetable. Include daily hours, subject rotation, revision cycles, PYQ practice,
mock-test schedule, and 10-month, 8-month, and 6-month roadmap options when relevant.
"""
        return await self.call_agent(STUDY_PLAN_PROMPT, prompt)


_default_runners = GovPrepAgentRunners()


async def run_syllabus_navigator(instruction: str, exam_type: str) -> str:
    return await _default_runners.run_syllabus_navigator(instruction, exam_type)


async def run_question_bank_agent(instruction: str, exam_type: str) -> str:
    return await _default_runners.run_question_bank_agent(instruction, exam_type)


async def run_current_affairs_agent(instruction: str, exam_type: str) -> str:
    return await _default_runners.run_current_affairs_agent(instruction, exam_type)


async def run_mock_test_agent(instruction: str, exam_type: str) -> str:
    return await _default_runners.run_mock_test_agent(instruction, exam_type)


async def run_weak_topic_agent(instruction: str, exam_type: str) -> str:
    return await _default_runners.run_weak_topic_agent(instruction, exam_type)


async def run_study_plan_agent(instruction: str, exam_type: str) -> str:
    return await _default_runners.run_study_plan_agent(instruction, exam_type)

