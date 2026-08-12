import io
import subprocess
import tempfile
import zipfile
from pathlib import Path

from core.config import settings

CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".rb",
    ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala",
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".sql", ".sh",
}

IGNORE_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "venv", "__pycache__",
    ".venv", "target", "vendor", ".idea", ".vscode", "coverage",
}


def _collect_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        if path.stat().st_size > settings.max_file_bytes:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        files[str(path.relative_to(root))] = content
    return files


def ingest_github(repo_url: str) -> dict[str, str]:
    if not repo_url.startswith("https://github.com/"):
        raise ValueError("Only public https://github.com/ URLs are supported.")
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmp],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise ValueError(f"Clone failed: {result.stderr.strip()}")
        files = _collect_files(Path(tmp))
    if not files:
        raise ValueError("No readable source files found in the repository.")
    return files


def ingest_zip(file_bytes: bytes) -> dict[str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            zf.extractall(root)
        files = _collect_files(root)
    if not files:
        raise ValueError("No readable source files found in the archive.")
    return files
