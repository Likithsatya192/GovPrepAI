"""OOP agent runner implementation for GovPrepAI."""

from __future__ import annotations

import asyncio

from duckduckgo_search import DDGS
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.prompts import (
    ACCURACY_GROUNDING_RULES,
    CURRENT_AFFAIRS_PROMPT,
    MOCK_TEST_PROMPT,
    QUESTION_BANK_PROMPT,
    STUDY_PLAN_PROMPT,
    SYLLABUS_NAVIGATOR_PROMPT,
    WEAK_TOPIC_PROMPT,
)
from app.core.config import get_settings
from app.core.exam_knowledge import format_curated_exam_knowledge


class GovPrepAgentRunners:
    """Runs all specialized preparation agents with async LLM calls."""

    def _search_sync(self, query: str) -> list[dict[str, str]]:
        """Run a DuckDuckGo search and return normalized result dictionaries."""

        settings = get_settings()
        with DDGS() as ddgs:
            raw_results = ddgs.text(
                query,
                region=settings.search_region,
                safesearch="moderate",
                max_results=settings.search_max_results,
            )
            return [
                {
                    "title": str(item.get("title", "")).strip(),
                    "url": str(item.get("href", "")).strip(),
                    "snippet": str(item.get("body", "")).strip(),
                }
                for item in raw_results
                if item.get("href")
            ]

    async def safe_search(self, queries: list[str]) -> str:
        """Run searches without letting provider failures crash the app."""

        seen_urls: set[str] = set()
        evidence: list[dict[str, str]] = []
        try:
            for query in queries:
                results = await asyncio.to_thread(self._search_sync, query)
                for result in results:
                    url = result["url"]
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    evidence.append(result)
        except Exception:
            return "Search unavailable. Use general knowledge only with clear uncertainty."

        if not evidence:
            return "No search evidence found. Use general knowledge only with clear uncertainty."

        formatted_results = []
        for index, item in enumerate(evidence[:12], start=1):
            formatted_results.append(
                "\n".join(
                    [
                        f"[{index}] {item['title']}",
                        f"URL: {item['url']}",
                        f"Snippet: {item['snippet']}",
                    ]
                )
            )
        return "\n\n".join(formatted_results)

    async def safe_search_one(self, query: str) -> str:
        """Convenience wrapper for single-query searches."""

        return await self.safe_search([query])

    async def official_exam_search(self, exam_type: str, topic: str) -> str:
        """Search broadly, with official-source-biased queries first."""

        return await self.safe_search(
            [
                f"{exam_type} {topic} official notification syllabus pdf",
                f"{exam_type} {topic} site:gov.in",
                f"{exam_type} {topic} site:nic.in",
                f"{exam_type} {topic} latest exam pattern weightage",
            ]
        )

    async def call_agent(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured Groq LLM asynchronously."""

        response = await get_llm().ainvoke(
            [
                SystemMessage(content=f"{system_prompt}\n\n{ACCURACY_GROUNDING_RULES}"),
                HumanMessage(content=user_prompt),
            ]
        )
        return str(response.content)

    async def run_syllabus_navigator(self, instruction: str, exam_type: str) -> str:
        """Find and structure latest official syllabus, weights, and priorities."""

        search_result = await self.official_exam_search(
            exam_type,
            "latest official syllabus topic weightage",
        )
        curated_knowledge = format_curated_exam_knowledge(exam_type)
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Curated knowledge:
{curated_knowledge}

Search evidence:
{search_result}

Return a clear syllabus map with:
- subjects
- topics and subtopics
- expected weightage or marks distribution
- priority ranking
- source URLs for official or high-confidence claims
- official-source caveats where needed
"""
        return await self.call_agent(SYLLABUS_NAVIGATOR_PROMPT, prompt)

    async def run_question_bank_agent(self, instruction: str, exam_type: str) -> str:
        """Analyze previous-year patterns and generate practice questions."""

        search_result = await self.official_exam_search(
            exam_type,
            "previous year question paper pattern PYQ analysis",
        )
        curated_knowledge = format_curated_exam_knowledge(exam_type)
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Curated knowledge:
{curated_knowledge}

Search evidence:
{search_result}

Generate 10 practice questions with answers and brief explanations across high-weightage topics.
Match the discovered pattern, section style, and difficulty as closely as possible.
Mention which parts are based on source evidence and which are inferred practice design.
"""
        return await self.call_agent(QUESTION_BANK_PROMPT, prompt)

    async def run_current_affairs_agent(self, instruction: str, exam_type: str) -> str:
        """Curate exam-relevant current affairs."""

        search_result = await self.safe_search(
            [
                f"latest current affairs important for {exam_type} exam India",
                f"{exam_type} current affairs official notification India",
                "PIB latest current affairs India government exam",
            ]
        )
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Search evidence:
{search_result}

Filter for high-probability exam relevance only. Include concise explanations and probable sections.
Include source URLs. Do not claim a topic is confirmed for the exam unless evidence supports it.
"""
        return await self.call_agent(CURRENT_AFFAIRS_PROMPT, prompt)

    async def run_mock_test_agent(self, instruction: str, exam_type: str) -> str:
        """Generate a 20-question exam-style mock test."""

        curated_knowledge = format_curated_exam_knowledge(exam_type)
        prompt = f"""
Exam: {exam_type}
Instruction: {instruction}

Curated knowledge:
{curated_knowledge}

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

        curated_knowledge = format_curated_exam_knowledge(exam_type)
        prompt = f"""
Exam: {exam_type}
Instruction and prior context:
{instruction}

Curated knowledge:
{curated_knowledge}

Identify low-coverage or weak topics. Create focused revision notes, common traps, and mnemonics.
"""
        return await self.call_agent(WEAK_TOPIC_PROMPT, prompt)

    async def run_study_plan_agent(self, instruction: str, exam_type: str) -> str:
        """Create a day-wise timetable with revision and mock-test cycles."""

        curated_knowledge = format_curated_exam_knowledge(exam_type)
        prompt = f"""
Exam: {exam_type}
Instruction and planning context:
{instruction}

Curated knowledge:
{curated_knowledge}

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
