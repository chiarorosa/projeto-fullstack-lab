import React from 'react';
import { Bot, Cpu, ListTodo, Webhook } from 'lucide-react';
import { useCanvasStore } from '../store/canvasStore';
import type { AppNode } from '../store/canvasStore';
import { NODE_TYPE_COLORS } from '../theme/tokens';

type PaletteNodeType = 'taskNode' | 'webhookNode' | 'agentNode' | 'llmNode';

type PaletteItem = {
  type: PaletteNodeType;
  label: string;
  icon: React.ReactNode;
  color: string;
  meta?: Record<string, unknown>;
};

type PaletteGroup = {
  category: string;
  items: PaletteItem[];
};

const NODE_PALETTE: PaletteGroup[] = [
  {
    category: 'Input',
    items: [
      {
        type: 'taskNode',
        label: 'Task Node',
        icon: <ListTodo size={18} />,
        color: NODE_TYPE_COLORS.task,
        meta: { taskInput: '', taskInputs: [] },
      },
      {
        type: 'webhookNode',
        label: 'Webhook Node',
        icon: <Webhook size={18} />,
        color: NODE_TYPE_COLORS.webhook,
        meta: { webhookId: '', method: 'POST' },
      },
    ],
  },
  {
    category: 'Agents',
    items: [
      { type: 'agentNode', label: 'AI Agent', icon: <Bot size={18} />, color: NODE_TYPE_COLORS.agent },
    ],
  },
  {
    category: 'LLM',
    items: [
      {
        type: 'llmNode',
        label: 'LLM Node',
        icon: <Cpu size={18} />,
        color: NODE_TYPE_COLORS.llm,
        meta: { provider: 'openrouter', model: 'google/gemma-4-31b-it:free' },
      },
    ],
  },
];

let idCounter = 1;

const SidebarPalette: React.FC = () => {
  const addNode = useCanvasStore((s) => s.addNode);
  const [activeItemKey, setActiveItemKey] = React.useState<string>('');

  const toProviderValue = (value: unknown): 'openai' | 'anthropic' | 'google' | 'local' | 'openrouter' | 'opencode' => {
    if (value === 'openai' || value === 'anthropic' || value === 'google' || value === 'local' || value === 'openrouter' || value === 'opencode') {
      return value;
    }
    return 'openrouter';
  };

  const handleDragStart = (e: React.DragEvent, item: PaletteItem) => {
    setActiveItemKey(`${item.type}-${item.label}`);
    e.dataTransfer.setData('application/reactflow-type', item.type);
    e.dataTransfer.setData('application/reactflow-meta', JSON.stringify(item.meta || {}));
    e.dataTransfer.setData('application/reactflow-label', item.label);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleClick = (item: PaletteItem) => {
    setActiveItemKey(`${item.type}-${item.label}`);
    const id = `node-${idCounter++}`;
    const meta = item.meta || {};
    let nodeData: AppNode['data'];

    if (item.type === 'taskNode') {
      nodeData = { label: item.label, taskInput: '', taskInputs: [] };
    } else if (item.type === 'webhookNode') {
      nodeData = { label: item.label, webhookId: '', method: 'POST' };
    } else if (item.type === 'agentNode') {
      nodeData = { label: item.label, role: 'New Agent', goal: '', backstory: '' };
    } else if (item.type === 'llmNode') {
      const provider = toProviderValue(meta.provider);
      const model = typeof meta.model === 'string' ? meta.model : 'google/gemma-4-31b-it:free';
      nodeData = {
        label: item.label,
        provider,
        model,
        credentialRef: undefined,
        apiKeyMasked: false,
      };
    } else {
      return;
    }

    const newNode: AppNode = {
      id,
      type: item.type,
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
          {group.items.map((item) => {
            const itemKey = `${item.type}-${item.label}`;
            const typeClass = `palette-item-${item.type}`;
            const iconClass = `palette-item-icon-${item.type}`;
            const isActive = activeItemKey === itemKey;

            return (
              <div
                key={itemKey}
                className={`palette-item ${typeClass}${isActive ? ' active' : ''}`}
                draggable
                onDragStart={(e) => handleDragStart(e, item)}
                onClick={() => handleClick(item)}
              >
                <span className={`palette-item-icon ${iconClass}`}>
                  {item.icon}
                </span>
                <span className="palette-item-label">{item.label}</span>
              </div>
            );
          })}
        </div>
      ))}
    </aside>
  );
};

export default SidebarPalette;
