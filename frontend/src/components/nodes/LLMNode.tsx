import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import { Cpu } from 'lucide-react';
import { useCanvasStore } from '../../store/canvasStore';
import type { LLMData } from '../../store/canvasStore';

const MODEL_LABELS: Record<string, string> = {
  'gpt-4o': 'GPT-4o',
  'gpt-4o-mini': 'GPT-4o Mini',
  'gpt-4-turbo': 'GPT-4 Turbo',
  'claude-3-5-sonnet': 'Claude 3.5 Sonnet',
  'claude-3-haiku': 'Claude 3 Haiku',
  'gemini-1.5-pro': 'Gemini 1.5 Pro',
  'gemini-1.5-flash': 'Gemini 1.5 Flash',
  'llama-3.1-70b': 'LLaMA 3.1 70B',
  'mistral-large': 'Mistral Large',
};

const PROVIDER_LABELS: Record<string, string> = {
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  google: 'Google',
  local: 'Local',
  openrouter: 'OpenRouter AI',
  opencode: 'OpenRouter AI',
};

const LLMNode = memo(({ id, data, selected }: NodeProps) => {
  const llmData = data as LLMData;
  const selectNode = useCanvasStore((s) => s.selectNode);
  const providerClass = `provider-${llmData.provider || 'openai'}`;
  const connectedAgentCount = (llmData.connectedAgents || []).length;

  return (
    <div
      className={`llm-node ${providerClass} ${selected ? 'selected' : ''}`}
      onClick={() => selectNode(id)}
    >
      <div className="node-header llm-header">
        <div className="node-icon">
          <Cpu size={16} />
        </div>
        <span className="node-type-label">LLM</span>
      </div>

      <div className="node-body">
        <div className="node-title">
          {MODEL_LABELS[llmData.model] || llmData.model || 'Select Model'}
        </div>
        <div className="node-subtitle">{PROVIDER_LABELS[llmData.provider] || llmData.provider || 'OpenAI'}</div>
        <div className="node-subtitle">Connected agents: {connectedAgentCount}</div>
        {!['local'].includes(llmData.provider || '') && (
          <div className="node-subtitle">
            Credential: {llmData.credentialRef ? 'stored' : 'not stored'}
          </div>
        )}
      </div>

      {/* Connects to Agent's left handle */}
      <Handle type="source" position={Position.Right} className="handle-right" />
    </div>
  );
});

LLMNode.displayName = 'LLMNode';
export default LLMNode;
