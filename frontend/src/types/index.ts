export type AgentRun = {
  run_id: string;
  workflow_id: string;
  agent_name: string;
  status: string;
  final_response?: string | null;
  trace_id?: string | null;
  created_at: string;
};

export type ApprovalTask = {
  id: string;
  run_id: string;
  status: string;
  reason: string;
  proposed_response: string;
  reviewed_response?: string | null;
  reviewer_notes?: string | null;
  created_at: string;
};
