import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import { Bot } from 'lucide-react';
import { useCanvasStore } from '../../store/canvasStore';
import type { AgentData } from '../../store/canvasStore';

const AgentNode = memo(({ id, data, selected }: NodeProps) => {
  const agentData = data as AgentData;
  const selectNode = useCanvasStore((s) => s.selectNode);
  const isExecutable = Boolean(agentData.connectedLlm);

  return (
    <div
      className={`agent-node ${selected ? 'selected' : ''}`}
      onClick={() => selectNode(id)}
    >
      {/* Incoming connection (from another agent or trigger) */}
      <Handle type="target" position={Position.Top} className="handle-top" />

      <div className="node-header agent-header">
        <div className="node-icon">
          <Bot size={16} />
        </div>
        <span className="node-type-label">Agent</span>
      </div>

      <div className="node-body">
        <div className="node-title">{agentData.role || 'Unnamed Agent'}</div>
        <div className={`node-status-badge ${isExecutable ? 'ready' : 'blocked'}`}>
          {isExecutable ? 'Ready' : 'Not executable'}
        </div>
        {agentData.goal && (
          <div className="node-subtitle" title={agentData.goal}>
            {agentData.goal.length > 50 ? agentData.goal.slice(0, 50) + '…' : agentData.goal}
          </div>
        )}
      </div>

      {/* LLM connection point (left side) */}
      <Handle
        type="target"
        position={Position.Left}
        id="llm-in"
        className="handle-left handle-llm-in"
      />
      {/* Output to next agent */}
      <Handle type="source" position={Position.Bottom} className="handle-bottom" />
    </div>
  );
});

AgentNode.displayName = 'AgentNode';
export default AgentNode;
