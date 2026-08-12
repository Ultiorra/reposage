from langchain.agents import create_agent
from langchain_core.tools import tool

from core.config import settings
from services.indexer import get_index


def build_agent(index_id: str):
    @tool
    def semantic_search(query: str) -> str:
        """Search the repository for code relevant to a natural-language query.
        Returns the most relevant snippets with their file paths."""
        index = get_index(index_id)
        if index is None:
            return "Repository index not found."
        results = index.search(query, settings.top_k)
        blocks = [
            f"[{r['path']}] (score {r['score']:.2f})\n{r['snippet']}"
            for r in results
        ]
        return "\n\n---\n\n".join(blocks)

    @tool
    def read_file(path: str) -> str:
        """Read the full content of a specific file by its exact relative path."""
        index = get_index(index_id)
        if index is None:
            return "Repository index not found."
        content = index.read_file(path)
        return content if content else f"File not found: {path}"

    @tool
    def list_files() -> str:
        """List every file path available in the repository."""
        index = get_index(index_id)
        if index is None:
            return "Repository index not found."
        return "\n".join(index.list_files())

    system_prompt = (
        "You are a senior engineer who knows this codebase intimately. "
        "Use semantic_search to locate relevant code, read_file to inspect a file "
        "in full, and list_files to see the structure. Always ground your answers "
        "in the actual code you retrieve, cite file paths, and say so explicitly "
        "when something is not present in the repository."
    )

    return create_agent(
        f"anthropic:{settings.llm_model}",
        tools=[semantic_search, read_file, list_files],
        system_prompt=system_prompt,
    )


def ask_agent(index_id: str, question: str) -> str:
    agent = build_agent(index_id)
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content
