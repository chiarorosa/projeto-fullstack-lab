import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import { Webhook } from 'lucide-react';
import { useCanvasStore } from '../../store/canvasStore';
import type { WebhookData } from '../../store/canvasStore';

const WebhookNode = memo(({ id, data, selected }: NodeProps) => {
  const webhookData = data as WebhookData;
  const { selectNode, edges } = useCanvasStore();
  const triggerId = (webhookData.webhookId || '').trim();
  const connectedAgentCount = edges.filter((edge) => edge.source === id).length;

  return (
    <div className={`webhook-node ${selected ? 'selected' : ''}`} onClick={() => selectNode(id)}>
      <div className="node-header webhook-header">
        <div className="node-icon">
          <Webhook size={16} />
        </div>
        <span className="node-type-label">Webhook</span>
      </div>

      <div className="node-body">
        <div className="node-title">{webhookData.label || 'Webhook Trigger'}</div>
        <div className={`node-status-badge ${triggerId ? 'ready' : 'blocked'}`}>
          {triggerId ? 'Configured' : 'Missing trigger id'}
        </div>
        <div className="node-subtitle">Method: POST</div>
        <div className="node-subtitle" title={triggerId || 'No trigger id configured'}>
          Trigger: {triggerId ? `${triggerId.slice(0, 20)}${triggerId.length > 20 ? '...' : ''}` : 'not set'}
        </div>
        <div className="node-subtitle">Connected agents: {connectedAgentCount}</div>
      </div>

      <Handle type="source" position={Position.Bottom} id="webhook-out" className="handle-webhook" />
    </div>
  );
});

WebhookNode.displayName = 'WebhookNode';
export default WebhookNode;
