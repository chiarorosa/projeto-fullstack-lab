import { create } from 'zustand';
import type {
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
} from '@xyflow/react';
import {
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';
import { FLOW_THEME } from '../theme/tokens';

export type NodeType = 'taskNode' | 'webhookNode' | 'agentNode' | 'llmNode';

export interface TaskData {
  label: string;
  taskInput: string;
  taskInputs: string[];
  [key: string]: unknown;
}

export interface WebhookData {
  label: string;
  webhookId: string;
  method: 'POST';
  testPresets?: WebhookTestPreset[];
  [key: string]: unknown;
}

export interface WebhookHeader {
  key: string;
  value: string;
}

export interface WebhookTestPreset {
  id: string;
  name: string;
  headers: WebhookHeader[];
  body: string;
}

export interface WebhookTestResponseState {
  status: number;
  ok: boolean;
  latencyMs: number;
  responseHeaders: Record<string, string>;
  responseBody: unknown;
  rawBody: string;
  executionId?: string;
  correlationId?: string;
  triggerId?: string;
  acceptedAt?: string;
  message?: string;
  testOrigin?: string;
}

export interface WebhookTestState {
  isOpen: boolean;
  nodeId: string | null;
  endpoint: string;
  webhookId: string;
  method: 'POST';
  headers: WebhookHeader[];
  body: string;
  loading: boolean;
  error: string | null;
  response: WebhookTestResponseState | null;
}

const EMPTY_WEBHOOK_TEST_STATE: WebhookTestState = {
  isOpen: false,
  nodeId: null,
  endpoint: '',
  webhookId: '',
  method: 'POST',
  headers: [{ key: 'Content-Type', value: 'application/json' }],
  body: '{\n  "task": "Analyze this webhook event and return the best result for the configured agents.",\n  "metadata": {\n    "event_type": "lead.created",\n    "source": "in-app-webhook-console"\n  }\n}',
  loading: false,
  error: null,
  response: null,
};

export interface AgentData {
  label: string;
  role: string;
  goal: string;
  backstory: string;
  connectedLlm?: string;
  executable?: boolean;
  executionReason?: string;
  [key: string]: unknown;
}

export interface LLMData {
  label: string;
  provider: 'openai' | 'anthropic' | 'google' | 'local' | 'openrouter' | 'opencode';
  model: string;
  apiKey?: string;
  credentialRef?: string;
  apiKeyMasked?: boolean;
  baseUrl?: string;
  connectedAgents?: string[];
  [key: string]: unknown;
}

export type AppNode = Node<TaskData | WebhookData | AgentData | LLMData, NodeType>;

interface CanvasStore {
  nodes: AppNode[];
  edges: Edge[];
  selectedNodeId: string | null;
  webhookTest: WebhookTestState;

  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  setNodes: (nodes: AppNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  addNode: (node: AppNode) => void;
  updateNodeData: (id: string, data: Partial<TaskData | WebhookData | AgentData | LLMData>) => void;
  selectNode: (id: string | null) => void;
  openWebhookTester: (payload: {
    nodeId: string;
    endpoint: string;
    webhookId: string;
    body?: string;
    headers?: WebhookHeader[];
  }) => void;
  closeWebhookTester: () => void;
  updateWebhookTestRequest: (patch: Partial<Pick<WebhookTestState, 'headers' | 'body'>>) => void;
  syncWebhookTestTarget: (patch: Partial<Pick<WebhookTestState, 'endpoint' | 'webhookId'>>) => void;
  setWebhookTestLoading: (loading: boolean) => void;
  setWebhookTestError: (error: string | null) => void;
  setWebhookTestResponse: (response: WebhookTestResponseState | null) => void;
  clearCanvas: () => void;
  loadGraph: (nodes: AppNode[], edges: Edge[]) => void;
}

export const useCanvasStore = create<CanvasStore>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  webhookTest: { ...EMPTY_WEBHOOK_TEST_STATE },

  onNodesChange: (changes) =>
    set((state) => ({ nodes: applyNodeChanges(changes, state.nodes) as AppNode[] })),

  onEdgesChange: (changes) =>
    set((state) => ({ edges: applyEdgeChanges(changes, state.edges) })),

  onConnect: (connection) =>
    set((state) => ({
      edges: addEdge({ ...connection, animated: true, style: { stroke: FLOW_THEME.edgeStroke } }, state.edges),
    })),

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),

  updateNodeData: (id, data) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, ...data } } : n
      ),
    })),

  selectNode: (id) => set({ selectedNodeId: id }),

  openWebhookTester: ({ nodeId, endpoint, webhookId, body, headers }) =>
    set((state) => ({
      selectedNodeId: nodeId,
      webhookTest: {
        ...state.webhookTest,
        isOpen: true,
        nodeId,
        endpoint,
        webhookId,
        method: 'POST',
        headers:
          headers && headers.length > 0
            ? headers
            : [{ key: 'Content-Type', value: 'application/json' }],
        body: body ?? state.webhookTest.body,
        loading: false,
        error: null,
      },
    })),

  closeWebhookTester: () =>
    set((state) => ({
      webhookTest: {
        ...state.webhookTest,
        isOpen: false,
        loading: false,
      },
    })),

  updateWebhookTestRequest: (patch) =>
    set((state) => ({
      webhookTest: {
        ...state.webhookTest,
        ...patch,
        error: null,
      },
    })),

  syncWebhookTestTarget: (patch) =>
    set((state) => ({
      webhookTest: {
        ...state.webhookTest,
        ...patch,
      },
    })),

  setWebhookTestLoading: (loading) =>
    set((state) => ({
      webhookTest: {
        ...state.webhookTest,
        loading,
      },
    })),

  setWebhookTestError: (error) =>
    set((state) => ({
      webhookTest: {
        ...state.webhookTest,
        error,
      },
    })),

  setWebhookTestResponse: (response) =>
    set((state) => ({
      webhookTest: {
        ...state.webhookTest,
        response,
      },
    })),

  clearCanvas: () =>
    set({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      webhookTest: { ...EMPTY_WEBHOOK_TEST_STATE },
    }),

  loadGraph: (nodes, edges) =>
    set((state) => ({
      nodes,
      edges,
      selectedNodeId: null,
      webhookTest: {
        ...state.webhookTest,
        nodeId: null,
        endpoint: '',
        webhookId: '',
        response: null,
        error: null,
        loading: false,
      },
    })),
}));
