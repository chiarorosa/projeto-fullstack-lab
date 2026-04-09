import React from 'react';
import { Braces, Play, Plus, Trash2, Save, FolderOpen, X, AlertCircle, CheckCircle2 } from 'lucide-react';
import { triggerWebhookTest } from '../api/client';
import { useCanvasStore } from '../store/canvasStore';
import {
  normalizeWebhookHeaders,
  parseWebhookJsonBody,
  webhookHeadersToRecord,
} from './webhookTestUtils';
import type {
  WebhookData,
  WebhookHeader,
  WebhookTestPreset,
  WebhookTestResponseState,
} from '../store/canvasStore';

const DEFAULT_BODY =
  '{\n  "task": "Analyze this webhook event and return the best result for the configured agents.",\n  "metadata": {\n    "event_type": "lead.created",\n    "source": "in-app-webhook-console"\n  }\n}';

function buildEndpointFromWebhookId(webhookId: string): string {
  const apiBaseUrl = (
    (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || 'http://localhost:8000'
  ).replace(/\/$/, '');
  return webhookId ? `${apiBaseUrl}/api/webhooks/${webhookId}` : '';
}

function prettyJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value ?? '');
  }
}

const WebhookTestConsole: React.FC = () => {
  const {
    nodes,
    selectedNodeId,
    webhookTest,
    updateNodeData,
    openWebhookTester,
    closeWebhookTester,
    updateWebhookTestRequest,
    syncWebhookTestTarget,
    setWebhookTestLoading,
    setWebhookTestError,
    setWebhookTestResponse,
  } = useCanvasStore();

  const selectedNode = React.useMemo(
    () => nodes.find((node) => node.id === (webhookTest.nodeId || selectedNodeId)),
    [nodes, webhookTest.nodeId, selectedNodeId]
  );

  const selectedWebhookNode =
    selectedNode && selectedNode.type === 'webhookNode' ? selectedNode : null;
  const webhookData = (selectedWebhookNode?.data || null) as WebhookData | null;
  const webhookId = (webhookData?.webhookId || '').trim();
  const endpoint = webhookId ? buildEndpointFromWebhookId(webhookId) : '';

  React.useEffect(() => {
    if (!selectedWebhookNode || !webhookId) return;
    if (!webhookTest.isOpen) return;
    if (webhookTest.webhookId === webhookId && webhookTest.endpoint === endpoint) return;
    syncWebhookTestTarget({ webhookId, endpoint });
  }, [
    selectedWebhookNode,
    webhookId,
    endpoint,
    webhookTest.isOpen,
    webhookTest.webhookId,
    webhookTest.endpoint,
    syncWebhookTestTarget,
  ]);

  React.useEffect(() => {
    if (!selectedWebhookNode || !webhookTest.isOpen) return;
    if (webhookTest.body.trim() === '') {
      updateWebhookTestRequest({ body: DEFAULT_BODY });
    }
  }, [selectedWebhookNode, webhookTest.isOpen, webhookTest.body, updateWebhookTestRequest]);

  const currentHeaders = webhookTest.headers;
  const currentBody = webhookTest.body;
  const currentResponse = webhookTest.response;
  const requestError = webhookTest.error;
  const isLoading = webhookTest.loading;
  const presets = webhookData?.testPresets || [];

  const ensureOpened = () => {
    if (!selectedWebhookNode || !webhookData) return;
    openWebhookTester({
      nodeId: selectedWebhookNode.id,
      endpoint,
      webhookId,
      body: currentBody || DEFAULT_BODY,
      headers: currentHeaders,
    });
  };

  const handleSend = async () => {
    if (!selectedWebhookNode || !webhookId) {
      setWebhookTestError('Select a Webhook Node with a configured Trigger ID.');
      return;
    }

    const parsedBody = parseWebhookJsonBody(currentBody);
    if (!parsedBody.ok) {
      setWebhookTestError(`Invalid JSON body: ${parsedBody.error}`);
      return;
    }

    const headerRecord = webhookHeadersToRecord(currentHeaders);

    setWebhookTestLoading(true);
    setWebhookTestError(null);
    setWebhookTestResponse(null);

    try {
      const correlationId = `test-${Date.now().toString(36)}`;
      const response = await triggerWebhookTest({
        webhookId,
        body: JSON.stringify(parsedBody.value),
        headers: headerRecord,
        correlationId,
      });

      const mapped: WebhookTestResponseState = {
        status: response.status,
        ok: response.ok,
        latencyMs: response.latencyMs,
        responseHeaders: response.responseHeaders,
        responseBody: response.responseBody,
        rawBody: response.rawBody,
        executionId: response.executionId,
        correlationId: response.correlationId || correlationId,
        triggerId: response.triggerId,
        acceptedAt: response.acceptedAt,
        message: response.message,
        testOrigin: 'in-app-webhook-console',
      };

      setWebhookTestResponse(mapped);

      if (!response.ok) {
        const display =
          typeof response.responseBody === 'object' && response.responseBody !== null
            ? prettyJson(response.responseBody)
            : response.rawBody || `HTTP ${response.status}`;
        setWebhookTestError(`Request failed (${response.status}): ${display}`);
      }
    } catch (error) {
      setWebhookTestError((error as Error).message || 'Failed to execute webhook request.');
    } finally {
      setWebhookTestLoading(false);
    }
  };

  const handleHeaderChange = (index: number, patch: Partial<WebhookHeader>) => {
    const nextHeaders = [...currentHeaders];
    nextHeaders[index] = { ...nextHeaders[index], ...patch };
    updateWebhookTestRequest({ headers: nextHeaders });
  };

  const addHeader = () => {
    updateWebhookTestRequest({ headers: [...currentHeaders, { key: '', value: '' }] });
  };

  const removeHeader = (index: number) => {
    const nextHeaders = currentHeaders.filter((_, idx) => idx !== index);
    updateWebhookTestRequest({
      headers: nextHeaders.length > 0 ? nextHeaders : [{ key: 'Content-Type', value: 'application/json' }],
    });
  };

  const savePreset = () => {
    if (!selectedWebhookNode || !webhookData) return;
    const presetName = window.prompt('Preset name:', `Preset ${new Date().toLocaleTimeString()}`)?.trim();
    if (!presetName) return;

    const presets = webhookData.testPresets || [];
    const nextPreset: WebhookTestPreset = {
      id: `preset_${Date.now().toString(36)}`,
      name: presetName,
      headers: normalizeWebhookHeaders(currentHeaders),
      body: currentBody,
    };

    updateNodeData(selectedWebhookNode.id, {
      testPresets: [...presets, nextPreset],
    });
  };

  const loadPreset = (presetId: string) => {
    if (!webhookData) return;
    const preset = (webhookData.testPresets || []).find((item) => item.id === presetId);
    if (!preset) return;
    updateWebhookTestRequest({ headers: preset.headers, body: preset.body });
  };

  const deletePreset = (presetId: string) => {
    if (!selectedWebhookNode || !webhookData) return;
    updateNodeData(selectedWebhookNode.id, {
      testPresets: (webhookData.testPresets || []).filter((item) => item.id !== presetId),
    });
  };

  if (!selectedWebhookNode) return null;

  return (
    <aside className={`webhook-console ${webhookTest.isOpen ? 'open' : 'closed'}`}>
      <div className="webhook-console-header">
        <div className="webhook-console-title">
          <Braces size={15} />
          <span>Webhook Test Console</span>
        </div>
        <div className="webhook-console-actions">
          {!webhookTest.isOpen ? (
            <button className="btn-ghost webhook-console-toggle" type="button" onClick={ensureOpened}>
              Open
            </button>
          ) : (
            <button className="btn-ghost webhook-console-toggle" type="button" onClick={closeWebhookTester}>
              <X size={14} />
            </button>
          )}
        </div>
      </div>

      {webhookTest.isOpen && (
        <div className="webhook-console-body">
          <div className="webhook-console-meta">
            <span>Endpoint</span>
            <code>{endpoint || 'Configure Trigger ID in Webhook Node'}</code>
          </div>

          <div className="webhook-console-hint">
            Expected payload: send JSON with at least <code>task</code> (or <code>task_input</code>) as text.
            Optional fields (e.g. <code>metadata</code>) can carry extra context for your flow.
          </div>

          <div className="webhook-console-section">
            <div className="webhook-console-section-title">
              Headers
              <button className="btn-ghost webhook-inline-btn" type="button" onClick={addHeader}>
                <Plus size={12} />
              </button>
            </div>
            <div className="webhook-headers-list">
              {currentHeaders.map((header, idx) => (
                <div key={`header-${idx}`} className="webhook-header-row">
                  <input
                    className="field-input"
                    value={header.key}
                    placeholder="Header"
                    onChange={(event) => handleHeaderChange(idx, { key: event.target.value })}
                  />
                  <input
                    className="field-input"
                    value={header.value}
                    placeholder="Value"
                    onChange={(event) => handleHeaderChange(idx, { value: event.target.value })}
                  />
                  <button
                    className="btn-ghost webhook-inline-btn"
                    type="button"
                    onClick={() => removeHeader(idx)}
                    title="Remove header"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="webhook-console-section">
            <div className="webhook-console-section-title">JSON Body</div>
            <textarea
              className="field-textarea webhook-json-body"
              value={currentBody}
              onChange={(event) => updateWebhookTestRequest({ body: event.target.value })}
              spellCheck={false}
              rows={10}
              placeholder={DEFAULT_BODY}
            />
          </div>

          <div className="webhook-console-presets">
            <div className="webhook-console-section-title">
              Presets
              <button className="btn-ghost webhook-inline-btn" type="button" onClick={savePreset}>
                <Save size={12} />
              </button>
            </div>
            {presets.length === 0 && (
              <div className="webhook-empty">No presets yet.</div>
            )}
            {presets.map((preset) => (
              <div key={preset.id} className="webhook-preset-row">
                <button
                  className="btn-ghost webhook-preset-load"
                  type="button"
                  onClick={() => loadPreset(preset.id)}
                >
                  <FolderOpen size={12} />
                  {preset.name}
                </button>
                <button
                  className="btn-ghost webhook-inline-btn"
                  type="button"
                  onClick={() => deletePreset(preset.id)}
                  title="Delete preset"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
          </div>

          <div className="webhook-console-run">
            <button
              className="btn-primary webhook-send-btn"
              type="button"
              onClick={handleSend}
              disabled={isLoading || !webhookId}
            >
              <Play size={14} />
              {isLoading ? 'Sending...' : 'Send Test Request'}
            </button>
          </div>

          {requestError && (
            <div className="webhook-response error">
              <AlertCircle size={14} />
              <span>{requestError}</span>
            </div>
          )}

          {currentResponse && (
            <div className={`webhook-response ${currentResponse.ok ? 'success' : 'error'}`}>
              <div className="webhook-response-headline">
                {currentResponse.ok ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
                <strong>HTTP {currentResponse.status}</strong>
                <span>{Math.round(currentResponse.latencyMs)} ms</span>
              </div>
              <div className="webhook-response-meta">
                {currentResponse.executionId && <span>Execution: {currentResponse.executionId}</span>}
                {currentResponse.correlationId && <span>Correlation: {currentResponse.correlationId}</span>}
                {currentResponse.triggerId && <span>Trigger: {currentResponse.triggerId}</span>}
              </div>
              <details className="webhook-response-details" open>
                <summary>Response Body</summary>
                <pre>{prettyJson(currentResponse.responseBody)}</pre>
              </details>
              <details className="webhook-response-details">
                <summary>Response Headers</summary>
                <pre>{prettyJson(currentResponse.responseHeaders)}</pre>
              </details>
            </div>
          )}
        </div>
      )}
    </aside>
  );
};

export default WebhookTestConsole;
