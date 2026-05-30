"""FastAPI routes for GovPrepAI."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, File, UploadFile

from app.agents.runners import (
    run_mock_test_agent,
    run_study_plan_agent,
    run_syllabus_navigator,
)
from app.core.exam_types import resolve_exam_type
from app.schemas import (
    ExamTypeRequest,
    GovPrepRequest,
    MockTestRequest,
    StudyPlanRequest,
    UploadNotesResponse,
)
from app.services.rag import NotesRagService
from app.stategraph.pipeline import GovPrepPipeline


class GovPrepApi:
    """Registers HTTP endpoints around the workflow pipeline and services."""

    def __init__(
        self,
        pipeline: GovPrepPipeline | None = None,
        rag_service: NotesRagService | None = None,
    ) -> None:
        self.router = APIRouter()
        self.pipeline = pipeline or GovPrepPipeline()
        self.rag_service = rag_service or NotesRagService()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route("/", self.health_check, methods=["GET"])
        self.router.add_api_route(
            "/api/upload-notes",
            self.upload_notes,
            methods=["POST"],
            response_model=UploadNotesResponse,
        )
        self.router.add_api_route("/api/prepare", self.prepare, methods=["POST"])
        self.router.add_api_route("/api/syllabus", self.syllabus, methods=["POST"])
        self.router.add_api_route("/api/mock-test", self.mock_test, methods=["POST"])
        self.router.add_api_route("/api/study-plan", self.study_plan, methods=["POST"])

    async def health_check(self) -> dict[str, str]:
        return {"status": "ok", "service": "GovPrepAI"}

    async def upload_notes(
        self,
        file: UploadFile = File(...),
        user_id: str = "default",
    ) -> UploadNotesResponse:
        pdf_bytes = await file.read()
        chunk_count = await asyncio.to_thread(
            self.rag_service.ingest_notes,
            pdf_bytes,
            user_id,
        )
        return UploadNotesResponse(user_id=user_id, chunk_count=chunk_count)

    async def prepare(self, request: GovPrepRequest) -> dict:
        exam_type, exam_type_overridden = resolve_exam_type(request.exam_type, request.goal)
        notes_context = await asyncio.to_thread(
            self.rag_service.retrieve_notes_context,
            request.goal,
            request.user_id,
            6,
        )
        goal = request.goal
        if notes_context:
            goal = f"{request.goal}\n\nRelevant uploaded notes context:\n{notes_context}"

        result = await self.pipeline.run(
            goal=goal,
            exam_type=exam_type,
            user_id=request.user_id,
        )
        response = dict(result)
        response["requested_exam_type"] = request.exam_type
        response["resolved_exam_type"] = exam_type
        response["exam_type_overridden"] = exam_type_overridden
        return response

    async def syllabus(self, request: ExamTypeRequest) -> dict[str, str]:
        result = await run_syllabus_navigator(
            "Find the latest official syllabus, all topics, topic weightage, and priority ranking.",
            request.exam_type,
        )
        return {"exam_type": request.exam_type, "result": result}

    async def mock_test(self, request: MockTestRequest) -> dict[str, str]:
        instruction = f"Create a mock test focused on topic: {request.topic}"
        result = await run_mock_test_agent(instruction, request.exam_type)
        return {"exam_type": request.exam_type, "topic": request.topic, "result": result}

    async def study_plan(self, request: StudyPlanRequest) -> dict[str, str]:
        weak_topics = ", ".join(request.weak_topics) if request.weak_topics else "not provided"
        instruction = (
            f"Create a study plan up to target date {request.target_date}. "
            f"Weak topics: {weak_topics}. Include 10-month, 8-month, and 6-month options."
        )
        result = await run_study_plan_agent(instruction, request.exam_type)
        return {
            "exam_type": request.exam_type,
            "target_date": request.target_date,
            "result": result,
        }
