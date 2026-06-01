import { useState } from "react";
import api from "../api/client";
import { AgentRun } from "../types";

type Props = {
  onCreated: (run: AgentRun) => void;
};

export function RunPanel({ onCreated }: Props) {
  const [query, setQuery] = useState("What does policy 101 say about cardiology review escalation?");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    try {
      const response = await api.post<AgentRun>("/agents/run", {
        workflow_id: "medical_document_review",
        agent_name: "Medical Document Review Agent",
        query
      });
      onCreated(response.data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Run Medical Agent</h2>
      <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={4} />
      <button onClick={submit} disabled={loading}>{loading ? "Running..." : "Start Run"}</button>
    </section>
  );
}
