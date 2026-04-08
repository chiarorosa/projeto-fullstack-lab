import { useState } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { Layers, Play, Trash2, FolderOpen, Zap } from 'lucide-react';

import Canvas from './components/Canvas';
import SidebarPalette from './components/SidebarPalette';
import PropertiesPanel from './components/PropertiesPanel';
import ExecutionLogs from './components/ExecutionLogs';
import TeamManager from './components/TeamManager';
import { useCanvasStore } from './store/canvasStore';
import { teamsApi, executeTeamStream } from './api/client';
import type { LogEvent } from './components/ExecutionLogs';
import type { TaskData } from './store/canvasStore';

function App() {
  const { nodes, edges, clearCanvas } = useCanvasStore();
  const [showManager, setShowManager] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTeamId, setCurrentTeamId] = useState<number | null>(null);

  const taskNode = nodes.find((n) => n.type === 'taskNode');
  const taskData = taskNode?.data as TaskData | undefined;
  const singleTask = taskData?.taskInput?.trim() || '';
  const batchTasks = (taskData?.taskInputs || []).map((item) => item.trim()).filter(Boolean);
  const hasTasks = Boolean(singleTask) || batchTasks.length > 0;
  const hasTaskNode = Boolean(taskNode);
  const hasExecutableAgents = nodes.some((node) => {
    if (node.type !== 'agentNode') return false;
    return edges.some((edge) => edge.source !== node.id && edge.target === node.id && nodes.find((n) => n.id === edge.source)?.type === 'llmNode');
  });

  const handleSaveAndRun = async () => {
    if (!hasTaskNode) {
      setLogs((prev) => [...prev, { type: 'error', message: 'Add a Task Node before running the team.' }]);
      setShowLogs(true);
      setIsRunning(false);
      return;
    }

    if (!hasTasks) {
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
      } else {
        await teamsApi.update(teamId, { graph_json: { nodes, edges } });
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
          setLogs((prev) => [...prev, { type: 'error', message: String(err) }]);
          setIsRunning(false);
        }
      );
    } catch (err) {
      setLogs((prev) => [...prev, { type: 'error', message: String(err) }]);
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
            disabled={agentCount === 0 || !hasTaskNode || !hasExecutableAgents}
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

        <PropertiesPanel />
      </div>

      {showManager && <TeamManager onClose={() => setShowManager(false)} />}
    </div>
  );
}

export default App;
