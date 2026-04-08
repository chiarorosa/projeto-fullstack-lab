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

export type NodeType = 'taskNode' | 'agentNode' | 'llmNode';

export interface TaskData {
  label: string;
  taskInput: string;
  taskInputs: string[];
  [key: string]: unknown;
}

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
  apiKey: string;
  baseUrl?: string;
  connectedAgents?: string[];
  [key: string]: unknown;
}

export type AppNode = Node<TaskData | AgentData | LLMData, NodeType>;

interface CanvasStore {
  nodes: AppNode[];
  edges: Edge[];
  selectedNodeId: string | null;

  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  setNodes: (nodes: AppNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  addNode: (node: AppNode) => void;
  updateNodeData: (id: string, data: Partial<TaskData | AgentData | LLMData>) => void;
  selectNode: (id: string | null) => void;
  clearCanvas: () => void;
  loadGraph: (nodes: AppNode[], edges: Edge[]) => void;
}

export const useCanvasStore = create<CanvasStore>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,

  onNodesChange: (changes) =>
    set((state) => ({ nodes: applyNodeChanges(changes, state.nodes) as AppNode[] })),

  onEdgesChange: (changes) =>
    set((state) => ({ edges: applyEdgeChanges(changes, state.edges) })),

  onConnect: (connection) =>
    set((state) => ({
      edges: addEdge({ ...connection, animated: true, style: { stroke: '#7c3aed' } }, state.edges),
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

  clearCanvas: () => set({ nodes: [], edges: [], selectedNodeId: null }),

  loadGraph: (nodes, edges) => set({ nodes, edges, selectedNodeId: null }),
}));
