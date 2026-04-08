import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

export interface GraphData {
  nodes: any[];
  edges: any[];
}

export interface Team {
  id: number;
  name: string;
  description?: string;
  graph_json: GraphData;
  created_at: string;
  updated_at: string;
}

export interface TeamRun {
  id: number;
  team_id: number;
  execution_id: string;
  task_index: number;
  task_input: string;
  final_output?: string | null;
  status: 'completed' | 'failed' | string;
  error_message?: string | null;
  selected_agent_id?: string | null;
  selected_agent?: string | null;
  selected_provider?: string | null;
  selected_model?: string | null;
  routing_reason?: string | null;
  decision_json?: {
    scores?: { agent_id?: string; agent?: string; score?: number; reason?: string }[];
  } | null;
  routing_json?: {
    activated_agents?: { id?: string; agent?: string }[];
    skipped_agents?: { id?: string; agent?: string; reason?: string }[];
  } | null;
  created_at: string;
}

export interface TeamRunsGrouped {
  executions: {
    execution_id: string;
    created_at: string;
    tasks: TeamRun[];
  }[];
}

export type ProviderType = 'openai' | 'anthropic' | 'google' | 'local' | 'openrouter' | 'opencode';

export interface ProviderTestRequest {
  provider: ProviderType;
  api_key?: string;
  model?: string;
  base_url?: string;
}

export interface ProviderTestResponse {
  ok: boolean;
  message: string;
}

export interface ExecutePayload {
  task_input?: string;
  task_inputs?: string[];
}

export const teamsApi = {
  list: () => api.get<Team[]>('/api/teams/'),
  get: (id: number) => api.get<Team>(`/api/teams/${id}`),
  create: (data: { name: string; description?: string; graph_json: GraphData }) =>
    api.post<Team>('/api/teams/', data),
  update: (id: number, data: Partial<{ name: string; description: string; graph_json: GraphData }>) =>
    api.put<Team>(`/api/teams/${id}`, data),
  delete: (id: number) => api.delete(`/api/teams/${id}`),
  listRuns: (teamId: number, limit = 50) =>
    api.get<TeamRun[]>(`/api/teams/${teamId}/runs?limit=${limit}`),
  listRunsByExecution: (teamId: number, limit = 20) =>
    api.get<TeamRunsGrouped>(`/api/teams/${teamId}/runs/by-execution?limit=${limit}`),
  executeStream: (teamId: number, taskInput: string): EventSource => {
    // We hijack SSE via fetch manually so we can POST
    return new EventSource(
      `http://localhost:8000/api/teams/${teamId}/execute?task_input=${encodeURIComponent(taskInput)}`
    );
  },
};

export const llmApi = {
  testProvider: (data: ProviderTestRequest) =>
    api.post<ProviderTestResponse>('/api/llm/test-provider', data),
};

export async function executeTeamStream(
  teamId: number,
  payload: ExecutePayload,
  onEvent: (event: any) => void,
  onDone: () => void,
  onError?: (err: any) => void
) {
  try {
    const response = await fetch(`http://localhost:8000/api/teams/${teamId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const parsed = JSON.parse(line.slice(6));
            onEvent(parsed);
          } catch {
            // skip non-json lines
          }
        }
      }
    }
    onDone();
  } catch (err) {
    onError?.(err);
  }
}

export default api;
