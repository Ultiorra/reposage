"use client";

import { useState } from "react";
import { ask, ingestUrl, ingestZip } from "../lib/api";

interface Turn {
  role: "user" | "agent";
  text: string;
}

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [indexId, setIndexId] = useState("");
  const [fileCount, setFileCount] = useState(0);
  const [ingesting, setIngesting] = useState(false);
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState("");

  async function handleIngestUrl() {
    if (!repoUrl.trim()) return;
    setError("");
    setIngesting(true);
    try {
      const res = await ingestUrl(repoUrl.trim());
      setIndexId(res.index_id);
      setFileCount(res.file_count);
      setTurns([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setIngesting(false);
    }
  }

  async function handleIngestZip(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setIngesting(true);
    try {
      const res = await ingestZip(file);
      setIndexId(res.index_id);
      setFileCount(res.file_count);
      setTurns([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setIngesting(false);
    }
  }

  async function handleAsk() {
    if (!question.trim() || !indexId) return;
    const q = question.trim();
    setQuestion("");
    setTurns((t) => [...t, { role: "user", text: q }]);
    setThinking(true);
    setError("");
    try {
      const answer = await ask(indexId, q);
      setTurns((t) => [...t, { role: "agent", text: answer }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setThinking(false);
    }
  }

  return (
    <main className="shell">
      <header className="masthead">
        <span className="prompt">~/reposage $</span>
        <h1>Ask questions about any codebase.</h1>
        <p>
          Point the agent at a public repo or a zip. It indexes the source, then
          reasons over it with semantic search and direct file reads.
        </p>
      </header>

      <section className="ingest">
        <div className="ingest-row">
          <input
            className="repo-input"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
          />
          <button className="load" onClick={handleIngestUrl} disabled={ingesting}>
            {ingesting ? "Indexing…" : "Index repo"}
          </button>
        </div>
        <label className="zip">
          or upload a .zip
          <input type="file" accept=".zip" onChange={handleIngestZip} />
        </label>
      </section>

      {indexId && (
        <p className="indexed">
          Indexed <strong>{fileCount}</strong> files · ready for questions
        </p>
      )}

      {indexId && (
        <section className="chat">
          {turns.map((t, i) => (
            <div key={i} className={`turn ${t.role}`}>
              <span className="who">{t.role === "user" ? "you" : "agent"}</span>
              <div className="bubble">{t.text}</div>
            </div>
          ))}
          {thinking && <div className="turn agent"><span className="who">agent</span><div className="bubble pulse">searching the code…</div></div>}

          <div className="ask-row">
            <input
              className="ask-input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
              placeholder="Where is authentication handled?"
            />
            <button className="send" onClick={handleAsk} disabled={thinking}>
              Ask
            </button>
          </div>
        </section>
      )}

      {error && <p className="error">{error}</p>}
    </main>
  );
}
