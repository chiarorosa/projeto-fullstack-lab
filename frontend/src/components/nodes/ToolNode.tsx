import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import { Wrench, Globe, Calculator, Search, FileText, Code2 } from 'lucide-react';
import { useCanvasStore } from '../../store/canvasStore';
import type { ToolData } from '../../store/canvasStore';

const TOOL_ICONS: Record<string, React.ReactNode> = {
  web_search: <Globe size={14} />,
  calculator: <Calculator size={14} />,
  search: <Search size={14} />,
  document: <FileText size={14} />,
  code: <Code2 size={14} />,
};

const ToolNode = memo(({ id, data, selected }: NodeProps) => {
  const toolData = data as ToolData;
  const selectNode = useCanvasStore((s) => s.selectNode);
  const icon = TOOL_ICONS[toolData.toolType] || <Wrench size={14} />;

  return (
    <div
      className={`tool-node ${selected ? 'selected' : ''}`}
      onClick={() => selectNode(id)}
    >
      <div className="node-header tool-header">
        <div className="node-icon tool-icon">{icon}</div>
        <span className="node-type-label">Tool</span>
      </div>

      <div className="node-body">
        <div className="node-title">{toolData.name || 'Unnamed Tool'}</div>
        <div className="node-subtitle">{toolData.toolType || 'generic'}</div>
      </div>

      {/* Connects to Agent's right handle */}
      <Handle type="source" position={Position.Left} className="handle-left" />
    </div>
  );
});

ToolNode.displayName = 'ToolNode';
export default ToolNode;
