import axios from 'axios';

const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();
const API_BASE_URL = (rawApiBaseUrl && rawApiBaseUrl.length > 0
  ? rawApiBaseUrl
  : 'http://localhost:8000').replace(/\/$/, '');
const API_BEARER_TOKEN = (import.meta.env.VITE_API_BEARER_TOKEN as string | undefined)?.trim();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  if (API_BEARER_TOKEN) {
    config.headers = config.headers || {};
    if (!config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${API_BEARER_TOKEN}`;
    }
  }
  return config;
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
  source?: 'task' | 'webhook' | string;
  trigger_id?: string | null;
  trigger_timestamp?: string | null;
  correlation_id?: string | null;
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
  credential_ref?: string;
  model?: string;
  base_url?: string;
  team_id?: number;
  node_id?: string;
}

export interface ProviderTestResponse {
  ok: boolean;
  message: string;
  credential_ref?: string;
}

export interface ExecutePayload {
  task_input?: string;
  task_inputs?: string[];
}

export interface WebhookTestRequest {
  webhookId: string;
  body: string;
  headers?: Record<string, string>;
  correlationId?: string;
}

export interface WebhookTestResponse {
  ok: boolean;
  status: number;
  latencyMs: number;
  responseHeaders: Record<string, string>;
  responseBody: unknown;
  rawBody: string;
  executionId?: string;
  correlationId?: string;
  triggerId?: string;
  acceptedAt?: string;
  message?: string;
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
    return new EventSource(`${API_BASE_URL}/api/teams/${teamId}/execute?task_input=${encodeURIComponent(taskInput)}`);
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
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (API_BEARER_TOKEN) {
      headers.Authorization = `Bearer ${API_BEARER_TOKEN}`;
    }

    const response = await fetch(`${API_BASE_URL}/api/teams/${teamId}/execute`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let backendDetail = '';
      try {
        const payload = await response.json();
        const detail =
          (typeof payload?.detail === 'string' && payload.detail) ||
          (typeof payload?.message === 'string' && payload.message) ||
          '';
        backendDetail = detail ? `: ${detail}` : '';
      } catch {
        backendDetail = '';
      }
      throw new Error(`HTTP ${response.status}${backendDetail}`);
    }

    if (!response.body) {
      throw new Error('Execution stream unavailable: empty response body.');
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

function parseJsonIfPossible(text: string): unknown {
  const trimmed = text.trim();
  if (!trimmed) return null;
  try {
    return JSON.parse(trimmed);
  } catch {
    return trimmed;
  }
}

export async function triggerWebhookTest(
  payload: WebhookTestRequest
): Promise<WebhookTestResponse> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'x-test-origin': 'in-app-webhook-console',
    ...(payload.headers || {}),
  };

  if (!headers['Content-Type'] && !headers['content-type']) {
    headers['Content-Type'] = 'application/json';
  }

  if (API_BEARER_TOKEN) {
    headers.Authorization = `Bearer ${API_BEARER_TOKEN}`;
  }

  if (payload.correlationId) {
    headers['x-correlation-id'] = payload.correlationId;
  }

  const startedAt = performance.now();
  const response = await fetch(`${API_BASE_URL}/api/webhooks/${payload.webhookId}`, {
    method: 'POST',
    headers,
    body: payload.body,
  });
  const latencyMs = Math.max(0, performance.now() - startedAt);

  const rawBody = await response.text();
  const parsedBody = parseJsonIfPossible(rawBody);
  const responseHeaders: Record<string, string> = {};
  response.headers.forEach((value, key) => {
    responseHeaders[key] = value;
  });

  let executionId: string | undefined;
  let correlationId: string | undefined;
  let triggerId: string | undefined;
  let acceptedAt: string | undefined;
  let message: string | undefined;

  if (parsedBody && typeof parsedBody === 'object') {
    const bodyObj = parsedBody as Record<string, unknown>;
    executionId = typeof bodyObj.execution_id === 'string' ? bodyObj.execution_id : undefined;
    correlationId = typeof bodyObj.correlation_id === 'string' ? bodyObj.correlation_id : undefined;
    triggerId = typeof bodyObj.trigger_id === 'string' ? bodyObj.trigger_id : undefined;
    acceptedAt = typeof bodyObj.accepted_at === 'string' ? bodyObj.accepted_at : undefined;
    message = typeof bodyObj.message === 'string' ? bodyObj.message : undefined;
  }

  return {
    ok: response.ok,
    status: response.status,
    latencyMs,
    responseHeaders,
    responseBody: parsedBody,
    rawBody,
    executionId,
    correlationId,
    triggerId,
    acceptedAt,
    message,
  };
}

export default api;
