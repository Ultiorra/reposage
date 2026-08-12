from pydantic import BaseModel


class IngestUrlRequest(BaseModel):
    repo_url: str


class IngestResponse(BaseModel):
    index_id: str
    file_count: int


class AskRequest(BaseModel):
    index_id: str
    question: str


class AskResponse(BaseModel):
    answer: str
