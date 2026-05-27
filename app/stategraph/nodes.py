"""OOP LangGraph node implementation for GovPrepAI."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.prompts import (
    PLANNER_SYSTEM_PROMPT,
    REPLANNER_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)
from app.agents.runners import GovPrepAgentRunners
from app.stategraph.json_parser import LlmJsonParser
from app.stategraph.schemas import GovPrepState, Step


class GovPrepWorkflowNodes:
    """Planner, executor, replanner, synthesizer, and router for the state graph."""

    allowed_agents = {
        "syllabus_navigator",
        "question_bank_agent",
        "current_affairs_agent",
        "mock_test_agent",
        "weak_topic_agent",
        "study_plan_agent",
    }

    def __init__(
        self,
        agent_runners: GovPrepAgentRunners | None = None,
        json_parser: LlmJsonParser | None = None,
    ) -> None:
        self.agent_runners = agent_runners or GovPrepAgentRunners()
        self.json_parser = json_parser or LlmJsonParser()
        self.agent_registry: dict[str, Callable[[str, str], Awaitable[str]]] = {
            "syllabus_navigator": self.agent_runners.run_syllabus_navigator,
            "question_bank_agent": self.agent_runners.run_question_bank_agent,
            "current_affairs_agent": self.agent_runners.run_current_affairs_agent,
            "mock_test_agent": self.agent_runners.run_mock_test_agent,
            "weak_topic_agent": self.agent_runners.run_weak_topic_agent,
            "study_plan_agent": self.agent_runners.run_study_plan_agent,
        }

    def fallback_step(self, goal: str) -> Step:
        return {
            "step_id": 1,
            "agent": "syllabus_navigator",
            "instruction": f"Map the syllabus, topic weightage, and priorities for: {goal}",
            "status": "pending",
            "result": None,
        }

    def normalize_steps(
        self,
        raw_steps: list[dict],
        fallback_goal: str,
        max_steps: int = 4,
        allow_empty: bool = False,
    ) -> list[Step]:
        """Validate LLM planner/replanner steps and fill executor fields."""

        normalized: list[Step] = []
        for index, raw_step in enumerate(raw_steps[:max_steps], start=1):
            agent = str(raw_step.get("agent", "")).strip()
            instruction = str(raw_step.get("instruction", "")).strip()
            if agent not in self.allowed_agents or not instruction:
                continue

            raw_id = raw_step.get("step_id", index)
            try:
                step_id = int(raw_id)
            except (TypeError, ValueError):
                step_id = index

            normalized.append(
                {
                    "step_id": step_id,
                    "agent": agent,
                    "instruction": instruction,
                    "status": "pending",
                    "result": None,
                }
            )

        if normalized or allow_empty:
            return normalized
        return [self.fallback_step(fallback_goal)]

    async def planner_node(self, state: GovPrepState) -> GovPrepState:
        """Create the initial execution plan."""

        prompt = f"""
User goal: {state["user_goal"]}
Exam type: {state["exam_type"]}

Plan for syllabus, roadmap, resources, weightage, practice, and doubt-resolution needs.
"""
        try:
            response = await get_llm().ainvoke(
                [SystemMessage(content=PLANNER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
            )
            raw_steps = self.json_parser.parse_array(str(response.content))
            plan = self.normalize_steps(raw_steps, state["user_goal"], max_steps=4)
            error = None
        except Exception as exc:
            plan = [self.fallback_step(state["user_goal"])]
            error = f"Planner fallback used: {exc}"

        return {
            **state,
            "plan": plan,
            "current_step_index": 0,
            "completed_results": [],
            "final_output": None,
            "error": error,
        }

    def prior_context(self, completed_results: list[dict]) -> str:
        """Build compact prior-step context for the executor."""

        context_blocks = []
        for item in completed_results:
            result = str(item.get("result", ""))[:400]
            context_blocks.append(f"Step {item.get('step_id')} ({item.get('agent')}): {result}")
        return "\n\n".join(context_blocks) if context_blocks else "No prior results yet."

    async def executor_node(self, state: GovPrepState) -> GovPrepState:
        """Run the current plan step through the correct agent runner."""

        current_index = state["current_step_index"]
        plan = list(state["plan"])
        if current_index >= len(plan):
            return state

        step = dict(plan[current_index])
        agent_name = step["agent"]
        runner = self.agent_registry.get(agent_name)
        instruction = (
            f"{step['instruction']}\n\n"
            f"Prior execution context for this user:\n{self.prior_context(state['completed_results'])}"
        )

        if runner is None:
            result = f"Unknown agent: {agent_name}"
            step["status"] = "failed"
            step["result"] = result
            error = result
        else:
            try:
                result = await runner(instruction, state["exam_type"])
                step["status"] = "done"
                step["result"] = result
                error = None
            except Exception as exc:
                result = f"{type(exc).__name__}: {exc}"
                step["status"] = "failed"
                step["result"] = result
                error = result

        plan[current_index] = step
        completed_results = [
            *state["completed_results"],
            {
                "step_id": step["step_id"],
                "agent": agent_name,
                "instruction": step["instruction"],
                "status": step["status"],
                "result": result,
            },
        ]
        return {
            **state,
            "plan": plan,
            "completed_results": completed_results,
            "current_step_index": current_index + 1,
            "error": error,
        }

    async def replanner_node(self, state: GovPrepState) -> GovPrepState:
        """Run one bounded replanning cycle after early execution feedback."""

        current_index = state["current_step_index"]
        completed_summary = json.dumps(state["completed_results"], ensure_ascii=False, indent=2)
        remaining_steps = state["plan"][current_index:]
        prompt = f"""
Original user goal: {state["user_goal"]}
Exam type: {state["exam_type"]}

Completed results:
{completed_summary}

Remaining steps:
{json.dumps(remaining_steps, ensure_ascii=False, indent=2)}

Return the revised remaining steps only. Keep useful steps, remove redundant ones, and modify
instructions when the completed results show a better direction.
"""
        try:
            response = await get_llm().ainvoke(
                [SystemMessage(content=REPLANNER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
            )
            raw_steps = self.json_parser.parse_array(str(response.content))
            revised_remaining = self.normalize_steps(
                raw_steps,
                state["user_goal"],
                max_steps=max(1, len(remaining_steps)),
                allow_empty=True,
            )
            plan = [*state["plan"][:current_index], *revised_remaining]
            error = None
        except Exception as exc:
            plan = state["plan"]
            error = f"Replanner kept original remaining steps: {exc}"

        return {
            **state,
            "plan": plan,
            "replan_count": state["replan_count"] + 1,
            "error": error,
        }

    async def synthesizer_node(self, state: GovPrepState) -> GovPrepState:
        """Synthesize all agent results into the final markdown plan."""

        structured_summary = json.dumps(
            {
                "user_goal": state["user_goal"],
                "exam_type": state["exam_type"],
                "completed_results": state["completed_results"],
            },
            ensure_ascii=False,
            indent=2,
        )
        prompt = f"""
Original user goal: {state["user_goal"]}
Exam type: {state["exam_type"]}

Structured execution summary:
{structured_summary}

Produce the final answer in markdown. Include exactly 5 next steps for today.
"""
        try:
            response = await get_llm().ainvoke(
                [SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
            )
            final_output = str(response.content)
            error = None
        except Exception as exc:
            final_output = (
                "# GovPrepAI Study Action Plan\n\n"
                "The final LLM synthesis could not run. Review the completed agent results below.\n\n"
                f"```json\n{structured_summary}\n```\n\n"
                "## Next Steps Today\n"
                "1. Verify the official syllabus for your target exam.\n"
                "2. Mark high-weightage topics from the completed results.\n"
                "3. Solve one previous-year set from the highest-weightage subject.\n"
                "4. Revise weak topics noted by the agents.\n"
                "5. Schedule the next mock test and review slot."
            )
            error = f"Synthesizer fallback used: {exc}"

        return {**state, "final_output": final_output, "error": error}

    def should_continue_executing(self, state: GovPrepState) -> str:
        """Route executor output to execute, replan, or synthesize."""

        if state["current_step_index"] >= len(state["plan"]):
            return "synthesize"

        completed_done_count = sum(
            1 for result in state["completed_results"] if result.get("status") == "done"
        )
        has_remaining = state["current_step_index"] < len(state["plan"])
        if completed_done_count >= 2 and state["replan_count"] == 0 and has_remaining:
            return "replan"

        return "execute"

