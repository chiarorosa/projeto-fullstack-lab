import React from 'react';
import { X, Bot, Cpu, Loader2, ListTodo, Webhook, RefreshCw, Copy, Terminal } from 'lucide-react';
import { useCanvasStore } from '../store/canvasStore';
import type { AgentData, LLMData, TaskData, WebhookData } from '../store/canvasStore';
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
  { label: 'Gemma 4 31B (Free)', provider: 'openrouter', model: 'google/gemma-4-31b-it:free' },
  { label: 'GPT-4o Mini (OpenRouter)', provider: 'openrouter', model: 'openai/gpt-4o-mini' },
  { label: 'Claude 3.5 Sonnet (OpenRouter)', provider: 'openrouter', model: 'anthropic/claude-3.5-sonnet' },
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

const API_BASE_URL = ((import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || 'http://localhost:8000').replace(/\/$/, '');

function generateWebhookId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return `wh_${crypto.randomUUID().replace(/-/g, '').slice(0, 20)}`;
  }
  return `wh_${Math.random().toString(36).slice(2, 14)}`;
}

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

const PropertiesPanel: React.FC<{ teamId?: number | null }> = ({ teamId }) => {
  const { nodes, edges, selectedNodeId, updateNodeData, selectNode, openWebhookTester } = useCanvasStore();

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
          {node.type === 'webhookNode' && <Webhook size={16} className="panel-icon webhook-icon" />}
          {node.type === 'llmNode' && <Cpu size={16} className="panel-icon llm-icon" />}
          <span className="panel-title">
            {node.type === 'agentNode' && 'Agent Properties'}
            {node.type === 'taskNode' && 'Task Properties'}
            {node.type === 'webhookNode' && 'Webhook Properties'}
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
        {node.type === 'webhookNode' && (
          <WebhookForm id={node.id} data={node.data as WebhookData} onChange={updateNodeData} onOpenTester={openWebhookTester} />
        )}
        {node.type === 'llmNode' && (
          <LLMForm id={node.id} data={node.data as LLMData} onChange={updateNodeData} teamId={teamId} />
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

const WebhookForm: React.FC<{
  id: string;
  data: WebhookData;
  onChange: any;
  onOpenTester: (payload: { nodeId: string; endpoint: string; webhookId: string; body?: string }) => void;
}> = ({ id, data, onChange, onOpenTester }) => {
  const webhookId = (data.webhookId || '').trim();
  const endpoint = webhookId ? `${API_BASE_URL}/api/webhooks/${webhookId}` : '';
  const [copied, setCopied] = React.useState(false);

  const regenerate = () => {
    onChange(id, { webhookId: generateWebhookId(), method: 'POST' });
    setCopied(false);
  };

  const copyEndpoint = async () => {
    if (!endpoint) return;
    try {
      await navigator.clipboard.writeText(endpoint);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  const openTester = () => {
    if (!webhookId || !endpoint) return;
    onOpenTester({
      nodeId: id,
      endpoint,
      webhookId,
      body: data.testPresets?.[0]?.body || '{\n  "task": ""\n}',
    });
  };

  return (
    <div className="form-fields">
      <label className="field-label">Webhook Label
        <input
          className="field-input"
          value={data.label || ''}
          onChange={(e) => onChange(id, { label: e.target.value })}
          placeholder="e.g., Incoming CRM Events"
        />
      </label>

      <label className="field-label">Method
        <input className="field-input" value="POST" disabled />
      </label>

      <label className="field-label">Trigger ID
        <div className="inline-action-row">
          <input
            className="field-input"
            value={data.webhookId || ''}
            onChange={(e) => onChange(id, { webhookId: e.target.value, method: 'POST' })}
            placeholder="wh_..."
          />
          <button className="btn-ghost inline-icon-btn" type="button" onClick={regenerate} title="Regenerate trigger id">
            <RefreshCw size={14} />
          </button>
        </div>
      </label>

      <label className="field-label">Trigger Endpoint
        <div className="inline-action-row">
          <input className="field-input" value={endpoint} placeholder="Generate a trigger id to enable endpoint" readOnly />
          <button className="btn-ghost inline-icon-btn" type="button" onClick={copyEndpoint} disabled={!endpoint} title="Copy endpoint">
            <Copy size={14} />
          </button>
          <button
            className="btn-ghost inline-icon-btn"
            type="button"
            onClick={openTester}
            disabled={!endpoint}
            title="Open webhook test console"
          >
            <Terminal size={14} />
          </button>
        </div>
      </label>

      <div className={`field-hint ${webhookId ? 'hint-success' : 'hint-warning'}`}>
        {webhookId
          ? copied
            ? 'Endpoint copied.'
            : 'Ready. Send JSON payload with task/task_input or task_inputs to trigger execution.'
          : 'Set a trigger id to activate this webhook.'}
      </div>
    </div>
  );
};

const LLMForm: React.FC<{ id: string; data: LLMData; onChange: any; teamId?: number | null }> = ({ id, data, onChange, teamId }) => {
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
        credential_ref: data.credentialRef?.trim() || undefined,
        model: data.model?.trim() || undefined,
        base_url: data.baseUrl?.trim() || undefined,
        team_id: teamId ?? undefined,
        node_id: id,
      });

      const returnedCredentialRef = response.data.credential_ref?.trim();
      if (response.data.ok && returnedCredentialRef) {
        onChange(id, { credentialRef: returnedCredentialRef, apiKey: '' });
      }

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
            onChange={(e) => handleDataChange({ apiKey: e.target.value, apiKeyMasked: false })}
            placeholder={data.credentialRef ? 'Stored securely on backend' : 'Stored securely when team is saved'}
          />
          {providerMeta.envVar && (
            <div className="field-hint">
              Environment variable: {providerMeta.envVar}
            </div>
          )}
          {data.credentialRef && (
            <div className="field-hint hint-success">
              Credential reference saved: {data.credentialRef}
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
