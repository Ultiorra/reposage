const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface IngestResult {
  index_id: string;
  file_count: number;
}

export async function ingestUrl(repoUrl: string): Promise<IngestResult> {
  const res = await fetch(`${API_URL}/api/ingest/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Ingestion failed");
  return res.json();
}

export async function ingestZip(file: File): Promise<IngestResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/ingest/zip`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail || "Ingestion failed");
  return res.json();
}

export async function ask(indexId: string, question: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index_id: indexId, question }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
  return (await res.json()).answer;
}
