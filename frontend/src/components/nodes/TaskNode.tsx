import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import { ListTodo } from 'lucide-react';
import { useCanvasStore } from '../../store/canvasStore';
import type { TaskData } from '../../store/canvasStore';

const TaskNode = memo(({ id, data, selected }: NodeProps) => {
  const taskData = data as TaskData;
  const { selectNode, edges } = useCanvasStore();
  const singleTask = taskData.taskInput?.trim() || '';
  const batchCount = (taskData.taskInputs || []).filter((item) => item.trim()).length;
  const connectedAgentCount = edges.filter((edge) => edge.source === id).length;
  const previewText = singleTask || (batchCount > 0 ? `${batchCount} batch task(s) configured` : 'Configure tasks in properties');

  return (
    <div className={`task-node ${selected ? 'selected' : ''}`} onClick={() => selectNode(id)}>
      <div className="node-header task-header">
        <div className="node-icon">
          <ListTodo size={16} />
        </div>
        <span className="node-type-label">Task</span>
      </div>

      <div className="node-body">
        <div className="node-title">{taskData.label || 'Task Bootstrap'}</div>
        <div className="task-node-meta">
          <span className={`task-chip ${singleTask ? 'ready' : ''}`}>Single</span>
          <span className={`task-chip ${batchCount > 0 ? 'ready' : ''}`}>Batch {batchCount}</span>
        </div>
        <div className="node-subtitle" title={previewText}>
          {previewText.length > 60 ? `${previewText.slice(0, 60)}...` : previewText}
        </div>
        <div className="node-subtitle">Connected agents: {connectedAgentCount}</div>
      </div>

      <Handle type="source" position={Position.Bottom} id="task-out" className="handle-task" />
    </div>
  );
});

TaskNode.displayName = 'TaskNode';
export default TaskNode;
