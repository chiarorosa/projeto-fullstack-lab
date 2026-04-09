import React, { useRef, useEffect } from 'react';
import { Bot, CheckCircle2, Loader2, AlertCircle, Terminal } from 'lucide-react';

export interface LogEvent {
  type:
    | 'graph_connectivity'
    | 'routing_decision'
    | 'task_start'
    | 'task_done'
    | 'task_error'
    | 'agent_start'
    | 'agent_output'
    | 'done'
    | 'error';
  agent?: string;
  llm?: string;
  output?: string;
  final_output?: string;
  index?: number;
  task_index?: number;
  task_input?: string;
  routing?: {
    activated_agents?: { id?: string; agent?: string }[];
    skipped_agents?: { id?: string; agent?: string; reason?: string }[];
  };
  bootstrap?: {
    source?: string;
    trigger_id?: string;
    timestamp?: string;
    correlation_id?: string;
    test_origin?: string;
  };
  fallback_used?: boolean;
  reason?: string;
  selected_agent?: string;
  selected_llm?: { provider?: string; model?: string };
  scores?: { agent?: string; score?: number; reason?: string }[];
  agents?: {
    agent?: string;
    llm_connected?: boolean;
    eligible?: boolean;
    reason?: string;
  }[];
  message?: string;
}

interface ExecutionLogsProps {
  logs: LogEvent[];
  isRunning: boolean;
  onClose?: () => void;
}

function normalizeExecutionError(message: string): string {
  const text = (message || '').trim();
  const lower = text.toLowerCase();

  if (lower.includes('openrouter key is valid') && lower.includes('429')) {
    return text;
  }

  if (lower.includes('rate/usage limit reached') || (lower.includes('openrouter') && lower.includes('429'))) {
    const marker = 'upstream detail:';
    const markerIdx = lower.indexOf(marker);
    const detail = markerIdx >= 0 ? text.slice(markerIdx + marker.length).trim() : text;
    return `OpenRouter key is valid, but model execution failed (429): ${detail}`;
  }

  if (lower.includes('model access failed even though api key is valid')) {
    return 'OpenRouter key is valid, but model access is currently blocked for this account/model.';
  }

  return text;
}

const ExecutionLogs: React.FC<ExecutionLogsProps> = ({ logs, isRunning, onClose }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const isDone = logs.some((l) => l.type === 'done');

  return (
    <div className="execution-logs-panel">
      <div className="logs-header">
        <div className="logs-title-row">
          <Terminal size={16} />
          <span>Execution Logs</span>
          {isRunning && <Loader2 size={14} className="spin" />}
          {isDone && <CheckCircle2 size={14} className="done-icon" />}
        </div>
        {onClose && (
          <button className="logs-close" onClick={onClose}>×</button>
        )}
      </div>

      <div className="logs-body">
        {logs.length === 0 && !isRunning && (
          <div className="logs-empty">No execution yet. Run a team to see logs here.</div>
        )}

        {logs.map((log, idx) => (
          <div key={idx} className={`log-entry log-${log.type}`}>
            {log.type === 'agent_start' && (
              <div className="log-agent-start">
                <div className="log-agent-badge">
                  <Bot size={12} />
                  <span>{log.agent}</span>
                </div>
                {typeof log.task_index === 'number' && <span className="log-task-badge">task #{log.task_index + 1}</span>}
                <span className="log-llm-badge">{log.llm}</span>
              </div>
            )}

            {log.type === 'task_start' && (
              <div className="log-task-start">
                <div>
                  <strong>Task #{(log.task_index ?? 0) + 1} started</strong>
                  <p className="log-final">{log.task_input}</p>
                  {log.bootstrap?.source && (
                    <p className="log-final">
                      Source: {log.bootstrap.source}
                      {log.bootstrap.trigger_id ? ` (${log.bootstrap.trigger_id})` : ''}
                    </p>
                  )}
                  {log.bootstrap?.correlation_id && (
                    <p className="log-final">Correlation: {log.bootstrap.correlation_id}</p>
                  )}
                  {log.bootstrap?.test_origin && (
                    <p className="log-final">Origin: {log.bootstrap.test_origin}</p>
                  )}
                </div>
                <div className="log-routing-summary">
                  <span>Activated: {log.routing?.activated_agents?.length || 0}</span>
                  <span>Skipped: {log.routing?.skipped_agents?.length || 0}</span>
                </div>
              </div>
            )}

            {log.type === 'graph_connectivity' && (
              <div className="log-task-start">
                <div>
                  <strong>Graph connectivity</strong>
                  <p className="log-final">
                    {(log.agents || []).map((agent) => `${agent.agent}: ${agent.eligible ? 'Ready' : 'Not executable'}`).join(' | ')}
                  </p>
                </div>
              </div>
            )}

            {log.type === 'routing_decision' && (
              <div className="log-task-start">
                <div>
                  <strong>Routing decision for task #{(log.task_index ?? 0) + 1}</strong>
                  <p className="log-final">
                    Selected: {log.selected_agent} ({log.selected_llm?.provider}/{log.selected_llm?.model})
                  </p>
                  <p className="log-final">Reason: {log.reason}</p>
                  {log.fallback_used && <p className="log-final">Fallback routing used</p>}
                </div>
              </div>
            )}

            {log.type === 'task_done' && (
              <div className="log-task-done">
                <CheckCircle2 size={14} />
                <div>
                  <strong>Task #{(log.task_index ?? 0) + 1} complete</strong>
                  <p className="log-final">{log.final_output}</p>
                </div>
              </div>
            )}

            {log.type === 'task_error' && (
              <div className="log-error">
                <AlertCircle size={14} />
                <span>
                  Task #{(log.task_index ?? 0) + 1}:{' '}
                  {normalizeExecutionError(log.message || 'Task failed.')}
                </span>
              </div>
            )}

            {log.type === 'agent_output' && (
              <div className="log-output">
                <span className="log-output-label">{log.agent} →</span>
                <p className="log-output-text">{log.output}</p>
              </div>
            )}

            {log.type === 'done' && (
              <div className="log-done">
                <CheckCircle2 size={14} />
                <div>
                  <strong>Execution Complete</strong>
                  <p className="log-final">{log.final_output}</p>
                </div>
              </div>
            )}

            {log.type === 'error' && (
              <div className="log-error">
                <AlertCircle size={14} />
                <span>{normalizeExecutionError(log.message || 'An unknown error occurred.')}</span>
              </div>
            )}
          </div>
        ))}

        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default ExecutionLogs;
