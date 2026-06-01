import { useEffect, useState } from "react";
import api from "./api/client";
import { RunPanel } from "./components/RunPanel";
import { AgentRun, ApprovalTask } from "./types";

function formatStatus(status: string) {
  return status.split("_").join(" ");
}

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

  const activeRuns = runs.filter((run) => run.status !== "completed").length;
  const approvalCount = approvals.filter((task) => task.status === "pending").length;
  const latestRun = runs[0];

  return (
    <main className="app-shell">
      <section className="hero card hero-card">
        <div className="hero-copy">
          <span className="eyebrow">Enterprise Agent Reliability</span>
          <h1>AgentOps Runtime Command Center</h1>
          <p>
            Monitor guarded agent execution, approval bottlenecks, and recovery posture from a
            single operational dashboard.
          </p>
        </div>

        <div className="hero-panel">
          <p className="hero-panel-label">Latest Trace</p>
          <strong>{latestRun?.trace_id?.slice(0, 16) ?? "No trace yet"}</strong>
          <span>{latestRun ? `Run ${latestRun.run_id.slice(0, 8)}` : "Start a workflow to begin"}</span>
        </div>
      </section>

      <section className="stats-grid">
        <article className="stat-card card">
          <span className="stat-label">Total Runs</span>
          <strong>{runs.length}</strong>
          <small>Executed from this session</small>
        </article>
        <article className="stat-card card">
          <span className="stat-label">Active Runs</span>
          <strong>{activeRuns}</strong>
          <small>Awaiting completion or review</small>
        </article>
        <article className="stat-card card">
          <span className="stat-label">Pending Approvals</span>
          <strong>{approvalCount}</strong>
          <small>Human-in-the-loop queue depth</small>
        </article>
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-main">
          <RunPanel
            onCreated={(run) => {
              setRuns((prev) => [run, ...prev]);
              refreshApprovals();
            }}
          />

          <article className="card panel-card">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Execution Feed</span>
                <h2>Agent Runs</h2>
              </div>
              <span className="soft-pill">{runs.length} tracked</span>
            </div>

            {runs.length === 0 ? <p className="empty-state">No runs yet. Start the medical workflow to populate operational telemetry.</p> : null}

            <div className="run-list">
              {runs.map((run) => (
                <div key={run.run_id} className="run-item">
                  <div>
                    <strong>{run.agent_name}</strong>
                    <p>{run.run_id.slice(0, 8)} · {run.workflow_id}</p>
                  </div>
                  <div className="run-meta">
                    <span className={`status-pill status-${run.status}`}>{formatStatus(run.status)}</span>
                    <span className="trace-chip">{run.trace_id?.slice(0, 10) ?? "no-trace"}</span>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </div>

        <aside className="dashboard-side">
          <article className="card panel-card approval-card">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Human Review</span>
                <h2>Approval Queue</h2>
              </div>
              <span className="soft-pill warning-pill">{approvals.length} items</span>
            </div>

            {approvals.length === 0 ? <p className="empty-state">No pending tasks. Guardrail routing is currently clear.</p> : null}

            {approvals.map((task) => (
              <div key={task.id} className="approval-item">
                <div className="approval-topline">
                  <span className={`status-pill status-${task.status}`}>{formatStatus(task.status)}</span>
                  <span className="trace-chip">{task.run_id.slice(0, 8)}</span>
                </div>
                <p className="approval-reason">{task.reason}</p>
                <small>{task.proposed_response}</small>
                <div className="actions">
                  <button onClick={() => approve(task.id, true)}>Approve</button>
                  <button className="secondary" onClick={() => approve(task.id, false)}>Reject</button>
                </div>
              </div>
            ))}
          </article>

          <article className="card panel-card operational-card">
            <span className="eyebrow">Operational Focus</span>
            <h2>Recovery Ready</h2>
            <ul className="signal-list">
              <li>Checkpoint-aware execution with replay and rollback paths</li>
              <li>Approval escalation for high-risk medical guidance</li>
              <li>Trace-aware architecture designed for incident review</li>
            </ul>
          </article>
        </aside>
      </section>
    </main>
  );
}
