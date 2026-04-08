import React from 'react';
import { Bot, Cpu, Globe, Calculator, FileText, Code2, ListTodo } from 'lucide-react';
import { useCanvasStore } from '../store/canvasStore';
import type { AppNode } from '../store/canvasStore';

const NODE_PALETTE = [
  {
    category: 'Input',
    items: [
      {
        type: 'taskNode',
        label: 'Task Node',
        icon: <ListTodo size={18} />,
        color: '#14b8a6',
        meta: { taskInput: '', taskInputs: [] },
      },
    ],
  },
  {
    category: 'Agents',
    items: [
      { type: 'agentNode', label: 'AI Agent', icon: <Bot size={18} />, color: '#7c3aed' },
    ],
  },
  {
    category: 'LLM',
    items: [
      { type: 'llmNode', label: 'LLM Node', icon: <Cpu size={18} />, color: '#10a37f', meta: { provider: 'openai', model: 'gpt-4o-mini' } },
    ],
  },
  {
    category: 'Tools',
    items: [
      { type: 'toolNode', label: 'Web Search', icon: <Globe size={18} />, color: '#06b6d4', meta: { toolType: 'web_search' } },
      { type: 'toolNode', label: 'Calculator', icon: <Calculator size={18} />, color: '#f59e0b', meta: { toolType: 'calculator' } },
      { type: 'toolNode', label: 'Document Reader', icon: <FileText size={18} />, color: '#84cc16', meta: { toolType: 'document' } },
      { type: 'toolNode', label: 'Code Executor', icon: <Code2 size={18} />, color: '#6366f1', meta: { toolType: 'code' } },
    ],
  },
];

let idCounter = 1;

const SidebarPalette: React.FC = () => {
  const addNode = useCanvasStore((s) => s.addNode);

  const handleDragStart = (e: React.DragEvent, item: any) => {
    e.dataTransfer.setData('application/reactflow-type', item.type);
    e.dataTransfer.setData('application/reactflow-meta', JSON.stringify(item.meta || {}));
    e.dataTransfer.setData('application/reactflow-label', item.label);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleClick = (item: any) => {
    const id = `node-${idCounter++}`;
    const meta = item.meta || {};
    let nodeData: any = {};

    if (item.type === 'taskNode') {
      nodeData = { label: item.label, taskInput: '', taskInputs: [] };
    } else if (item.type === 'agentNode') {
      nodeData = { label: item.label, role: 'New Agent', goal: '', backstory: '' };
    } else if (item.type === 'llmNode') {
      nodeData = {
        label: item.label,
        provider: meta.provider || 'openai',
        model: meta.model || 'gpt-4o-mini',
        apiKey: '',
      };
    } else if (item.type === 'toolNode') {
      nodeData = { label: item.label, name: item.label, toolType: meta.toolType || 'generic' };
    }

    const newNode: AppNode = {
      id,
      type: item.type as any,
      position: { x: 250 + Math.random() * 100, y: 150 + Math.random() * 100 },
      data: nodeData,
    };
    addNode(newNode);
  };

  return (
    <aside className="sidebar-palette">
      <div className="sidebar-header">
        <span className="sidebar-title">Node Palette</span>
        <span className="sidebar-hint">Drag or click to add</span>
      </div>

      {NODE_PALETTE.map((group) => (
        <div key={group.category} className="palette-group">
          <div className="palette-group-label">{group.category}</div>
          {group.items.map((item) => (
            <div
              key={`${item.type}-${item.label}`}
              className="palette-item"
              draggable
              onDragStart={(e) => handleDragStart(e, item)}
              onClick={() => handleClick(item)}
              style={{ '--item-color': item.color } as React.CSSProperties}
            >
              <span className="palette-item-icon" style={{ color: item.color }}>
                {item.icon}
              </span>
              <span className="palette-item-label">{item.label}</span>
            </div>
          ))}
        </div>
      ))}
    </aside>
  );
};

export default SidebarPalette;
