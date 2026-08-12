from fastapi import APIRouter, File, HTTPException, UploadFile

from agent.graph import ask_agent
from models_schemas import (
    AskRequest,
    AskResponse,
    IngestResponse,
    IngestUrlRequest,
)
from services.indexer import create_index, get_index
from services.ingestion import ingest_github, ingest_zip

router = APIRouter(prefix="/api", tags=["repo"])


@router.post("/ingest/url", response_model=IngestResponse)
def ingest_url(payload: IngestUrlRequest):
    try:
        files = ingest_github(payload.repo_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc
    index_id = create_index(files)
    return IngestResponse(index_id=index_id, file_count=len(files))


@router.post("/ingest/zip", response_model=IngestResponse)
async def ingest_upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="A .zip file is required.")
    try:
        files = ingest_zip(await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    index_id = create_index(files)
    return IngestResponse(index_id=index_id, file_count=len(files))


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    if get_index(payload.index_id) is None:
        raise HTTPException(status_code=404, detail="Index not found. Ingest a repo first.")
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="A question is required.")
    try:
        answer = ask_agent(payload.index_id, payload.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc
    return AskResponse(answer=answer)
