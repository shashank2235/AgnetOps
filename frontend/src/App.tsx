import { useEffect, useState } from "react";
import api from "./api/client";
import { RunPanel } from "./components/RunPanel";
import { AgentRun, ApprovalTask } from "./types";

export function App() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [approvals, setApprovals] = useState<ApprovalTask[]>([]);

  async function refreshApprovals() {
    const response = await api.get<ApprovalTask[]>("/approvals");
    setApprovals(response.data);
  }

  useEffect(() => {
    refreshApprovals();
  }, []);

  async function approve(id: string, approved: boolean) {
    const endpoint = approved ? `/approvals/${id}/approve` : `/approvals/${id}/reject`;
    await api.post(endpoint, { reviewer_notes: approved ? "Reviewed and approved" : "Rejected" });
    await refreshApprovals();
  }

  return (
    <main>
      <header>
        <h1>AgentOps Runtime</h1>
        <p>Disaster recovery, guardrails, and human approval for enterprise AI agents.</p>
      </header>

      <RunPanel
        onCreated={(run) => {
          setRuns((prev) => [run, ...prev]);
          refreshApprovals();
        }}
      />

      <section className="grid">
        <article className="card">
          <h2>Agent Runs</h2>
          {runs.length === 0 ? <p>No runs yet</p> : null}
          {runs.map((run) => (
            <div key={run.run_id} className="row">
              <strong>{run.run_id.slice(0, 8)}</strong>
              <span>{run.status}</span>
              <span>{run.trace_id?.slice(0, 10)}</span>
            </div>
          ))}
        </article>

        <article className="card">
          <h2>Approval Queue</h2>
          {approvals.length === 0 ? <p>No pending tasks</p> : null}
          {approvals.map((task) => (
            <div key={task.id} className="approval">
              <p><strong>{task.status.toUpperCase()}</strong> - {task.reason}</p>
              <small>{task.proposed_response}</small>
              <div className="actions">
                <button onClick={() => approve(task.id, true)}>Approve</button>
                <button className="secondary" onClick={() => approve(task.id, false)}>Reject</button>
              </div>
            </div>
          ))}
        </article>
      </section>
    </main>
  );
}
