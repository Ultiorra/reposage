from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-5"
    embedding_model: str = "all-MiniLM-L6-v2"
    cors_origins: str = "http://localhost:3000"
    max_file_bytes: int = 200_000
    chunk_size: int = 1200
    chunk_overlap: int = 150
    top_k: int = 6

    class Config:
        env_file = ".env"


settings = Settings()
