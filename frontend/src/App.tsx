import { useState } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { Layers, Play, Trash2, FolderOpen, Zap } from 'lucide-react';

import Canvas from './components/Canvas';
import SidebarPalette from './components/SidebarPalette';
import PropertiesPanel from './components/PropertiesPanel';
import ExecutionLogs from './components/ExecutionLogs';
import TeamManager from './components/TeamManager';
import WebhookTestConsole from './components/WebhookTestConsole';
import { useCanvasStore } from './store/canvasStore';
import { teamsApi, executeTeamStream } from './api/client';
import type { LogEvent } from './components/ExecutionLogs';
import type { AppNode, TaskData, WebhookData } from './store/canvasStore';
import type { Edge } from '@xyflow/react';
import axios from 'axios';

function normalizeUiErrorMessage(message: string): string {
  const text = (message || '').trim();
  const lower = text.toLowerCase();

  if (lower.includes('openrouter key is valid') && lower.includes('429')) {
    return text;
  }

  if (lower.includes('api key missing') || lower.includes('api key is required')) {
    return text;
  }

  return text;
}

function App() {
  const { nodes, edges, clearCanvas, loadGraph } = useCanvasStore();
  const [showManager, setShowManager] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTeamId, setCurrentTeamId] = useState<number | null>(null);

  const taskNode = nodes.find((n) => n.type === 'taskNode');
  const webhookNodes = nodes.filter((n) => n.type === 'webhookNode');
  const taskData = taskNode?.data as TaskData | undefined;
  const singleTask = taskData?.taskInput?.trim() || '';
  const batchTasks = (taskData?.taskInputs || []).map((item) => item.trim()).filter(Boolean);
  const hasTasks = Boolean(singleTask) || batchTasks.length > 0;
  const hasTaskNode = Boolean(taskNode);
  const hasWebhookBootstrap = webhookNodes.some((node) => {
    const data = node.data as WebhookData;
    return Boolean((data.webhookId || '').trim());
  });
  const hasSupportedBootstrap = (hasTaskNode && hasTasks) || hasWebhookBootstrap;
  const hasExecutableAgents = nodes.some((node) => {
    if (node.type !== 'agentNode') return false;
    return edges.some((edge) => edge.source !== node.id && edge.target === node.id && nodes.find((n) => n.id === edge.source)?.type === 'llmNode');
  });

  const handleSaveAndRun = async () => {
    if (!hasTaskNode && !hasWebhookBootstrap) {
      setLogs((prev) => [...prev, { type: 'error', message: 'Add a Task Node with tasks or configure a Webhook Node before running.' }]);
      setShowLogs(true);
      setIsRunning(false);
      return;
    }

    if (hasTaskNode && !hasTasks && !hasWebhookBootstrap) {
      setLogs((prev) => [...prev, { type: 'error', message: 'Task Node has no task input. Add single or batch tasks.' }]);
      setShowLogs(true);
      setIsRunning(false);
      return;
    }

    if (!hasExecutableAgents) {
      setLogs((prev) => [
        ...prev,
        {
          type: 'error',
          message:
            'No executable agents found. Connect at least one LLM Node to an Agent Node.',
        },
      ]);
      setShowLogs(true);
      setIsRunning(false);
      return;
    }

    setShowLogs(true);
    setLogs([]);
    setIsRunning(true);

    try {
      let teamId = currentTeamId;
      if (!teamId) {
        const res = await teamsApi.create({
          name: 'Current Session',
          graph_json: { nodes, edges },
        });
        teamId = res.data.id;
        setCurrentTeamId(teamId);
        loadGraph(res.data.graph_json.nodes as AppNode[], res.data.graph_json.edges as Edge[]);
      } else {
        try {
          const res = await teamsApi.update(teamId, { graph_json: { nodes, edges } });
          loadGraph(res.data.graph_json.nodes as AppNode[], res.data.graph_json.edges as Edge[]);
        } catch (error) {
          const status = axios.isAxiosError(error) ? error.response?.status : undefined;
          if (status === 404) {
            const recreate = await teamsApi.create({
              name: 'Current Session',
              graph_json: { nodes, edges },
            });
            teamId = recreate.data.id;
            setCurrentTeamId(teamId);
            loadGraph(recreate.data.graph_json.nodes as AppNode[], recreate.data.graph_json.edges as Edge[]);
          } else {
            throw error;
          }
        }
      }

      if (!hasTasks && hasWebhookBootstrap) {
        setLogs((prev) => [
          ...prev,
          {
            type: 'done',
            final_output:
              'Team salvo com sucesso. Este fluxo esta configurado para bootstrap por Webhook Node; use o Webhook Test Console para disparar execucoes.',
          },
        ]);
        setIsRunning(false);
        return;
      }

      await executeTeamStream(
        teamId,
        {
          task_input: singleTask,
          task_inputs: batchTasks,
        },
        (event: LogEvent) => setLogs((prev) => [...prev, event]),
        () => setIsRunning(false),
        (err) => {
          const normalized = normalizeUiErrorMessage(String(err));
          setLogs((prev) => [...prev, { type: 'error', message: normalized }]);
          setIsRunning(false);
        }
      );
    } catch (err) {
      const normalized = normalizeUiErrorMessage(String(err));
      setLogs((prev) => [...prev, { type: 'error', message: normalized }]);
      setIsRunning(false);
    }
  };

  const agentCount = nodes.filter((n) => n.type === 'agentNode').length;

  return (
    <div className="app-root">
      <header className="topbar">
        <div className="topbar-brand">
          <Zap size={20} className="brand-icon" />
          <span className="brand-name">AgentForge</span>
          <span className="brand-tagline">Visual Multi-Agent Builder</span>
        </div>

        <nav className="topbar-actions">
          <div className="agent-counter">
            <Layers size={14} />
            <span>{agentCount} agent{agentCount !== 1 ? 's' : ''}</span>
          </div>

          <button className="btn-ghost" onClick={() => setShowManager(true)}>
            <FolderOpen size={16} />
            Teams
          </button>

          <button className="btn-ghost" onClick={clearCanvas}>
            <Trash2 size={16} />
            Clear
          </button>

          <button
            className="btn-primary run-btn"
            onClick={handleSaveAndRun}
            disabled={agentCount === 0 || !hasSupportedBootstrap || !hasExecutableAgents}
          >
            <Play size={16} />
            Run Team
          </button>
        </nav>
      </header>

      <div className="main-layout">
        <SidebarPalette />

        <main className="canvas-area">
          <ReactFlowProvider>
            <Canvas />
          </ReactFlowProvider>

          {showLogs && (
            <div className="logs-container">
              <ExecutionLogs
                logs={logs}
                isRunning={isRunning}
                onClose={() => setShowLogs(false)}
              />
            </div>
          )}
        </main>

        <PropertiesPanel teamId={currentTeamId} />
      </div>

      <WebhookTestConsole />

      {showManager && (
        <TeamManager
          onClose={() => setShowManager(false)}
          onTeamLoaded={(teamId) => setCurrentTeamId(teamId)}
        />
      )}
    </div>
  );
}

export default App;
