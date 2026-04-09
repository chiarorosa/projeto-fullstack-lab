import React, { useCallback, useRef } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  useReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useCanvasStore } from '../store/canvasStore';
import TaskNode from './nodes/TaskNode';
import AgentNode from './nodes/AgentNode';
import LLMNode from './nodes/LLMNode';
import type { AppNode } from '../store/canvasStore';

const nodeTypes = {
  taskNode: TaskNode,
  agentNode: AgentNode,
  llmNode: LLMNode,
};

let idCounter = 100;

const Canvas: React.FC = () => {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode, selectNode } =
    useCanvasStore();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData('application/reactflow-type');
      const label = event.dataTransfer.getData('application/reactflow-label');
      const metaStr = event.dataTransfer.getData('application/reactflow-meta');
      if (!type) return;

      const meta = metaStr ? JSON.parse(metaStr) : {};
      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      const id = `node-${idCounter++}`;

      let nodeData: any = {};
      if (type === 'taskNode') {
        nodeData = { label, taskInput: meta.taskInput || '', taskInputs: meta.taskInputs || [] };
      } else if (type === 'agentNode') {
        nodeData = { label, role: label, goal: '', backstory: '' };
      } else if (type === 'llmNode') {
        nodeData = {
          label,
          provider: meta.provider || 'openrouter',
          model: meta.model || 'google/gemma-4-31b-it:free',
          credentialRef: undefined,
          apiKeyMasked: false,
        };
      }

      const newNode: AppNode = {
        id,
        type: type as any,
        position,
        data: nodeData,
      };
      addNode(newNode);
    },
    [screenToFlowPosition, addNode]
  );

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: any) => {
      selectNode(node.id);
    },
    [selectNode]
  );

  const onPaneClick = useCallback(() => {
    selectNode(null);
  }, [selectNode]);

  const enrichedNodes = React.useMemo(() => {
    const agentIncomingLlm = new Map<string, string>();
    const llmConnectedAgents = new Map<string, string[]>();

    for (const edge of edges) {
      const sourceNode = nodes.find((n) => n.id === edge.source);
      const targetNode = nodes.find((n) => n.id === edge.target);
      if (!sourceNode || !targetNode) continue;

      if (sourceNode.type === 'llmNode' && targetNode.type === 'agentNode') {
        agentIncomingLlm.set(targetNode.id, sourceNode.id);
        const list = llmConnectedAgents.get(sourceNode.id) || [];
        llmConnectedAgents.set(sourceNode.id, [...list, targetNode.id]);
      }

    }

    return nodes.map((node) => {
      if (node.type === 'agentNode') {
        const connectedLlm = agentIncomingLlm.get(node.id);
        return {
          ...node,
          data: {
            ...node.data,
            connectedLlm,
            executable: Boolean(connectedLlm),
            executionReason: connectedLlm ? 'Ready' : 'Missing LLM connection',
          },
        };
      }

      if (node.type === 'llmNode') {
        return {
          ...node,
          data: {
            ...node.data,
            connectedAgents: llmConnectedAgents.get(node.id) || [],
          },
        };
      }

      return node;
    });
  }, [nodes, edges]);

  return (
    <div ref={reactFlowWrapper} className="canvas-wrapper">
      <ReactFlow
        nodes={enrichedNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        defaultEdgeOptions={{
          animated: true,
          style: { stroke: '#7c3aed', strokeWidth: 2 },
        }}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="rgba(255,255,255,0.06)"
        />
        <Controls className="rf-controls" />
        <MiniMap
          nodeColor={(n) => {
            if (n.type === 'taskNode') return '#14b8a6';
            if (n.type === 'agentNode') return '#7c3aed';
            if (n.type === 'llmNode') return '#10a37f';
            return '#06b6d4';
          }}
          maskColor="rgba(0,0,0,0.6)"
          className="rf-minimap"
        />
      </ReactFlow>
    </div>
  );
};

export default Canvas;
