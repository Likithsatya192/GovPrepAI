"""Pipeline object that builds and runs the GovPrepAI LangGraph workflow."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.stategraph.nodes import GovPrepWorkflowNodes
from app.stategraph.schemas import ExamType, GovPrepState


class GovPrepPipeline:
    """Owns the plan-and-execute graph and exposes a single async run method."""

    def __init__(self, nodes: GovPrepWorkflowNodes | None = None) -> None:
        self.nodes = nodes or GovPrepWorkflowNodes()
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(GovPrepState)
        graph.add_node("planner", self.nodes.planner_node)
        graph.add_node("executor", self.nodes.executor_node)
        graph.add_node("replanner", self.nodes.replanner_node)
        graph.add_node("synthesizer", self.nodes.synthesizer_node)

        graph.set_entry_point("planner")
        graph.add_edge("planner", "executor")
        graph.add_conditional_edges(
            "executor",
            self.nodes.should_continue_executing,
            {
                "execute": "executor",
                "replan": "replanner",
                "synthesize": "synthesizer",
            },
        )
        graph.add_edge("replanner", "executor")
        graph.add_edge("synthesizer", END)
        return graph.compile()

    async def run(self, goal: str, exam_type: ExamType, user_id: str = "default") -> GovPrepState:
        initial_state: GovPrepState = {
            "user_goal": goal,
            "user_id": user_id,
            "exam_type": exam_type,
            "plan": [],
            "current_step_index": 0,
            "completed_results": [],
            "final_output": None,
            "replan_count": 0,
            "error": None,
        }
        return await self.graph.ainvoke(initial_state)

