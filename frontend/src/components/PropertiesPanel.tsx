import React from 'react';
import { X, Bot, Cpu, Loader2, ListTodo } from 'lucide-react';
import { useCanvasStore } from '../store/canvasStore';
import type { AgentData, LLMData, TaskData } from '../store/canvasStore';
import { llmApi } from '../api/client';

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
  { value: 'local', label: 'Local' },
  { value: 'openrouter', label: 'OpenRouter AI' },
] as const;

type ProviderValue = (typeof PROVIDERS)[number]['value'];

const LLM_OPTIONS = [
  { label: 'GPT-4o', provider: 'openai', model: 'gpt-4o' },
  { label: 'GPT-4o Mini', provider: 'openai', model: 'gpt-4o-mini' },
  { label: 'Claude 3.5 Sonnet', provider: 'anthropic', model: 'claude-3-5-sonnet' },
  { label: 'Claude 3 Haiku', provider: 'anthropic', model: 'claude-3-haiku' },
  { label: 'Gemini 1.5 Pro', provider: 'google', model: 'gemini-1.5-pro' },
  { label: 'Gemini 1.5 Flash', provider: 'google', model: 'gemini-1.5-flash' },
  { label: 'LLaMA 3.1 70B', provider: 'local', model: 'llama-3.1-70b' },
] as const;

type ProviderMetadata = {
  modelPlaceholder: string;
  envVar?: string;
  defaultBaseUrl: string;
  docsLabel: string;
  docsUrl: string;
  baseUrlHint?: string;
};

const PROVIDER_METADATA: Record<ProviderValue, ProviderMetadata> = {
  openai: {
    modelPlaceholder: 'e.g., gpt-4o, gpt-4o-mini',
    envVar: 'OPENAI_API_KEY',
    defaultBaseUrl: 'https://api.openai.com/v1',
    docsLabel: 'OpenAI model list',
    docsUrl: 'https://developers.openai.com/api/reference/resources/models/methods/list',
  },
  anthropic: {
    modelPlaceholder: 'e.g., claude-3-5-sonnet-latest, claude-3-5-haiku-latest',
    envVar: 'ANTHROPIC_API_KEY',
    defaultBaseUrl: 'https://api.anthropic.com',
    docsLabel: 'Anthropic model docs',
    docsUrl: 'https://docs.anthropic.com/en/docs/about-claude/models/all-models',
  },
  google: {
    modelPlaceholder: 'e.g., gemini-1.5-pro, gemini-1.5-flash',
    envVar: 'GOOGLE_API_KEY',
    defaultBaseUrl: 'https://generativelanguage.googleapis.com',
    docsLabel: 'Gemini model docs',
    docsUrl: 'https://ai.google.dev/gemini-api/docs/models',
  },
  openrouter: {
    modelPlaceholder: 'e.g., openai/gpt-4o-mini, anthropic/claude-3.5-sonnet',
    envVar: 'OPENROUTER_API_KEY',
    defaultBaseUrl: 'https://openrouter.ai/api/v1',
    docsLabel: 'OpenRouter model catalog',
    docsUrl: 'https://openrouter.ai/models',
  },
  local: {
    modelPlaceholder: 'e.g., llama3.1:8b, mistral:latest',
    defaultBaseUrl: 'http://localhost:11434/v1',
    docsLabel: 'Ollama model library',
    docsUrl: 'https://ollama.com/library',
    baseUrlHint: 'Ollama default: http://localhost:11434/v1 | LM Studio default: http://localhost:1234/v1',
  },
};

const PropertiesPanel: React.FC = () => {
  const { nodes, edges, selectedNodeId, updateNodeData, selectNode } = useCanvasStore();

  if (!selectedNodeId) return null;

  const node = nodes.find((n) => n.id === selectedNodeId);
  if (!node) return null;

  const connectedLlmId = node.type === 'agentNode'
    ? edges.find((edge) => {
        if (edge.target !== node.id) return false;
        const sourceNode = nodes.find((candidate) => candidate.id === edge.source);
        return sourceNode?.type === 'llmNode';
      })?.source
    : undefined;

  return (
    <aside className="properties-panel">
      <div className="panel-header">
        <div className="panel-title-row">
          {node.type === 'agentNode' && <Bot size={16} className="panel-icon agent-icon" />}
          {node.type === 'taskNode' && <ListTodo size={16} className="panel-icon task-icon" />}
          {node.type === 'llmNode' && <Cpu size={16} className="panel-icon llm-icon" />}
          <span className="panel-title">
            {node.type === 'agentNode' && 'Agent Properties'}
            {node.type === 'taskNode' && 'Task Properties'}
            {node.type === 'llmNode' && 'LLM Properties'}
          </span>
        </div>
        <button className="panel-close" onClick={() => selectNode(null)}>
          <X size={16} />
        </button>
      </div>

      <div className="panel-body">
        {node.type === 'agentNode' && (
          <AgentForm
            id={node.id}
            data={node.data as AgentData}
            onChange={updateNodeData}
            connectedLlmId={connectedLlmId}
          />
        )}
        {node.type === 'taskNode' && (
          <TaskForm id={node.id} data={node.data as TaskData} onChange={updateNodeData} />
        )}
        {node.type === 'llmNode' && (
          <LLMForm id={node.id} data={node.data as LLMData} onChange={updateNodeData} />
        )}
      </div>
    </aside>
  );
};

const AgentForm: React.FC<{
  id: string;
  data: AgentData;
  onChange: any;
  connectedLlmId?: string;
}> = ({ id, data, onChange, connectedLlmId }) => (
  <div className="form-fields">
    <label className="field-label">Role (System Prompt Title)
      <input
        className="field-input"
        value={data.role || ''}
        onChange={(e) => onChange(id, { role: e.target.value })}
        placeholder="e.g., Research Specialist"
      />
    </label>
    <label className="field-label">Goal
      <textarea
        className="field-textarea"
        value={data.goal || ''}
        onChange={(e) => onChange(id, { goal: e.target.value })}
        placeholder="What this agent is trying to accomplish..."
        rows={3}
      />
    </label>
    <label className="field-label">Backstory
      <textarea
        className="field-textarea"
        value={data.backstory || ''}
        onChange={(e) => onChange(id, { backstory: e.target.value })}
        placeholder="Context about this agent's expertise..."
        rows={4}
      />
    </label>
    <div className={`field-hint ${connectedLlmId ? 'hint-success' : 'hint-warning'}`}>
      {connectedLlmId
        ? `LLM connected: ${connectedLlmId}`
        : 'No LLM connected. This agent will not execute.'}
    </div>
  </div>
);

const TaskForm: React.FC<{ id: string; data: TaskData; onChange: any }> = ({ id, data, onChange }) => {
  const taskInputsText = (data.taskInputs || []).join('\n');

  const handleBatchChange = (value: string) => {
    const parsed = value.split('\n');
    onChange(id, { taskInputs: parsed });
  };

  return (
    <div className="form-fields">
      <label className="field-label">Task Bootstrap Label
        <input
          className="field-input"
          value={data.label || ''}
          onChange={(e) => onChange(id, { label: e.target.value })}
          placeholder="e.g., Primary Task Input"
        />
      </label>

      <label className="field-label">Single Task
        <textarea
          className="field-textarea"
          rows={3}
          value={data.taskInput || ''}
          onChange={(e) => onChange(id, { taskInput: e.target.value })}
          placeholder="One task for quick execution..."
        />
      </label>

      <label className="field-label">Batch Tasks (one per line)
        <textarea
          className="field-textarea"
          rows={6}
          value={taskInputsText}
          onChange={(e) => handleBatchChange(e.target.value)}
          placeholder="Task 1&#10;Task 2&#10;Task 3"
        />
      </label>

      <div className="field-hint">
        O Task Node funciona como bootstrap da execução. Se houver tarefas em lote, elas terão prioridade sobre o campo de tarefa única.
      </div>
    </div>
  );
};

const LLMForm: React.FC<{ id: string; data: LLMData; onChange: any }> = ({ id, data, onChange }) => {
  const providerValue: ProviderValue = data.provider === 'opencode' ? 'openrouter' : (data.provider || 'openai');
  const isLocalProvider = providerValue === 'local';
  const providerMeta = PROVIDER_METADATA[providerValue];
  const modelSuggestions = LLM_OPTIONS.filter((option) => option.provider === providerValue);
  const datalistId = `model-suggestions-${id}`;
  const [testState, setTestState] = React.useState<{
    status: 'idle' | 'loading' | 'success' | 'error';
    message: string;
  }>({ status: 'idle', message: '' });

  const clearTestState = () => {
    if (testState.status !== 'idle') {
      setTestState({ status: 'idle', message: '' });
    }
  };

  const handleDataChange = (patch: Partial<LLMData>) => {
    onChange(id, patch);
    clearTestState();
  };

  const handleTestProvider = async () => {
    setTestState({ status: 'loading', message: 'Testing provider configuration...' });
    try {
      const response = await llmApi.testProvider({
        provider: providerValue,
        api_key: data.apiKey?.trim() || undefined,
        model: data.model?.trim() || undefined,
        base_url: data.baseUrl?.trim() || undefined,
      });

      setTestState({
        status: response.data.ok ? 'success' : 'error',
        message: response.data.message,
      });
    } catch (error: any) {
      const message = error?.response?.data?.message || error?.message || 'Provider test request failed.';
      setTestState({ status: 'error', message });
    }
  };
  
  return (
    <div className="form-fields">
      <label className="field-label">Provider
        <select
          className="field-select"
          value={providerValue}
          onChange={(e) => handleDataChange({ provider: e.target.value as LLMData['provider'] })}
        >
          {PROVIDERS.map((prov) => (
            <option key={prov.value} value={prov.value}>
              {prov.label}
            </option>
          ))}
        </select>
      </label>
      
      <label className="field-label">Model
        <input
          className="field-input"
          value={data.model || ''}
          onChange={(e) => handleDataChange({ model: e.target.value })}
          placeholder={providerMeta.modelPlaceholder}
          list={datalistId}
        />
        <datalist id={datalistId}>
          {modelSuggestions.map((option) => (
            <option key={option.model} value={option.model} label={option.label} />
          ))}
        </datalist>
      </label>

      <div className="provider-meta">
        <div className="field-hint">
          Default API URL: {providerMeta.defaultBaseUrl}
        </div>
        <div className="field-hint">
          Model reference: <a className="field-link" href={providerMeta.docsUrl} target="_blank" rel="noreferrer">{providerMeta.docsLabel}</a>
        </div>
      </div>
      
      {!isLocalProvider && (
        <label className="field-label">API Key
          <input
            className="field-input"
            type="password"
            value={data.apiKey || ''}
            onChange={(e) => handleDataChange({ apiKey: e.target.value })}
            placeholder="Leave blank to use environment variable"
          />
          {providerMeta.envVar && (
            <div className="field-hint">
              Environment variable: {providerMeta.envVar}
            </div>
          )}
        </label>
      )}
      
      {isLocalProvider && (
        <label className="field-label">Base URL
          <input
            className="field-input"
            value={data.baseUrl || ''}
            onChange={(e) => handleDataChange({ baseUrl: e.target.value })}
            placeholder={providerMeta.defaultBaseUrl}
          />
          {providerMeta.baseUrlHint && <div className="field-hint">{providerMeta.baseUrlHint}</div>}
        </label>
      )}

      <div className="provider-test-row">
        <button
          className="btn-ghost provider-test-btn"
          onClick={handleTestProvider}
          disabled={testState.status === 'loading'}
          type="button"
        >
          {testState.status === 'loading' && <Loader2 size={14} className="spin" />}
          {testState.status === 'loading' ? 'Testing...' : 'Test Provider'}
        </button>
      </div>

      {testState.status !== 'idle' && (
        <div className={`provider-test-feedback ${testState.status}`}>
          {testState.message}
        </div>
      )}
    </div>
  );
};

export default PropertiesPanel;
