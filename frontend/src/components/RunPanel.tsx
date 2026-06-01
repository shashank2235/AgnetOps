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
    <section className="card panel-card composer-card">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Workflow Launch</span>
          <h2>Run Medical Agent</h2>
        </div>
        <span className="soft-pill">LangGraph workflow</span>
      </div>

      <p className="composer-copy">
        Submit a medical policy question to simulate retrieval, knowledge graph enrichment,
        guardrails, approvals, and recovery-aware orchestration.
      </p>

      <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={5} />

      <div className="composer-actions">
        <button onClick={submit} disabled={loading}>{loading ? "Running..." : "Start Run"}</button>
        <span className="helper-text">High-risk prompts will route into human approval automatically.</span>
      </div>
    </section>
  );
}
