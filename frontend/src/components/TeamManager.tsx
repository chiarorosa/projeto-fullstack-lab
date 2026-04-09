import React, { useState, useEffect } from 'react';
import { Save, FolderOpen, Trash2, X } from 'lucide-react';
import { teamsApi } from '../api/client';
import type { Team, TeamRun, TeamRunsGrouped } from '../api/client';
import { useCanvasStore } from '../store/canvasStore';
import type { AppNode } from '../store/canvasStore';
import type { Edge } from '@xyflow/react';

interface TeamManagerProps {
  onClose: () => void;
  onTeamLoaded?: (teamId: number) => void;
}

const TeamManager: React.FC<TeamManagerProps> = ({ onClose, onTeamLoaded }) => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(false);
  const [saveName, setSaveName] = useState('');
  const [saveDesc, setSaveDesc] = useState('');
  const [saving, setSaving] = useState(false);
  const [selectedRunTeam, setSelectedRunTeam] = useState<Team | null>(null);
  const [runHistory, setRunHistory] = useState<TeamRun[]>([]);
  const [groupedRuns, setGroupedRuns] = useState<TeamRunsGrouped['executions']>([]);
  const [runsLoading, setRunsLoading] = useState(false);
  const [showArtifactsTab, setShowArtifactsTab] = useState(false);
  const [selectedExecutionId, setSelectedExecutionId] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'failed'>('all');

  const { nodes, edges, loadGraph } = useCanvasStore();

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    setLoading(true);
    try {
      const res = await teamsApi.list();
      setTeams(res.data);
    } catch {
      console.error('Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!saveName.trim()) return;
    setSaving(true);
    try {
      await teamsApi.create({
        name: saveName.trim(),
        description: saveDesc.trim() || undefined,
        graph_json: { nodes, edges },
      });
      setSaveName('');
      setSaveDesc('');
      await fetchTeams();
    } catch {
      console.error('Failed to save team');
    } finally {
      setSaving(false);
    }
  };

  const handleLoad = (team: Team) => {
    loadGraph(team.graph_json.nodes as AppNode[], team.graph_json.edges as Edge[]);
    onTeamLoaded?.(team.id);
    onClose();
  };

  const handleDelete = async (id: number) => {
    await teamsApi.delete(id);
    setTeams((prev) => prev.filter((t) => t.id !== id));
    if (selectedRunTeam?.id === id) {
      setSelectedRunTeam(null);
      setRunHistory([]);
      setGroupedRuns([]);
    }
  };

  const handleViewRuns = async (team: Team) => {
    setSelectedRunTeam(team);
    setRunsLoading(true);
    try {
      const res = await teamsApi.listRuns(team.id, 100);
      setRunHistory(res.data);
      const groupedRes = await teamsApi.listRunsByExecution(team.id, 50);
      setGroupedRuns(groupedRes.data.executions);
      setShowArtifactsTab(true);
    } catch {
      setRunHistory([]);
      setGroupedRuns([]);
    } finally {
      setRunsLoading(false);
    }
  };

  const visibleRuns = runHistory.filter((run) => {
    const executionMatch = selectedExecutionId === 'all' || run.execution_id === selectedExecutionId;
    const statusMatch = statusFilter === 'all' || run.status === statusFilter;
    return executionMatch && statusMatch;
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Team Manager</span>
          <button className="modal-close" onClick={onClose}><X size={18} /></button>
        </div>

        <div className="modal-body">
          {/* Save current graph */}
          <div className="modal-section">
            <h3 className="section-title"><Save size={14} /> Save Current Team</h3>
            <input
              className="field-input"
              placeholder="Team name..."
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
            />
            <input
              className="field-input"
              placeholder="Description (optional)"
              value={saveDesc}
              onChange={(e) => setSaveDesc(e.target.value)}
              style={{ marginTop: 8 }}
            />
            <button
              className="btn-primary"
              onClick={handleSave}
              disabled={!saveName.trim() || saving}
              style={{ marginTop: 10 }}
            >
              {saving ? 'Saving…' : 'Save Team'}
            </button>
          </div>

          {/* Load saved teams */}
          <div className="modal-section">
            <h3 className="section-title"><FolderOpen size={14} /> Saved Teams</h3>
            {loading && <div className="loading-text">Loading…</div>}
            {!loading && teams.length === 0 && (
              <div className="empty-state">No saved teams yet.</div>
            )}
            {teams.map((team) => (
              <div key={team.id} className="team-card">
                <div className="team-card-info">
                  <div className="team-card-name">{team.name}</div>
                  {team.description && (
                    <div className="team-card-desc">{team.description}</div>
                  )}
                  <div className="team-card-meta">
                    {team.graph_json.nodes?.length || 0} nodes · {team.graph_json.edges?.length || 0} edges
                  </div>
                </div>
                <div className="team-card-actions">
                  <button
                    className="btn-icon btn-view"
                    onClick={() => handleViewRuns(team)}
                    title="Runs"
                  >
                    Runs
                  </button>
                  <button className="btn-icon btn-load" onClick={() => handleLoad(team)} title="Load">
                    <FolderOpen size={14} />
                  </button>
                  <button
                    className="btn-icon btn-delete"
                    onClick={() => handleDelete(team.id)}
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {selectedRunTeam && showArtifactsTab && (
            <div className="modal-section">
              <h3 className="section-title">Artifacts: {selectedRunTeam.name}</h3>
              <div className="artifacts-filters">
                <label className="field-label">Execution
                  <select
                    className="field-select"
                    value={selectedExecutionId}
                    onChange={(e) => setSelectedExecutionId(e.target.value)}
                  >
                    <option value="all">All executions</option>
                    {groupedRuns.map((execution) => (
                      <option key={execution.execution_id} value={execution.execution_id}>
                        {execution.execution_id.slice(0, 8)}... ({execution.tasks.length} tasks)
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field-label">Status
                  <select
                    className="field-select"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value as 'all' | 'completed' | 'failed')}
                  >
                    <option value="all">All</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                  </select>
                </label>
              </div>
              {runsLoading && <div className="loading-text">Loading runs…</div>}
              {!runsLoading && visibleRuns.length === 0 && (
                <div className="empty-state">No persisted runs yet for this team.</div>
              )}
              {!runsLoading && visibleRuns.map((run) => (
                <div key={run.id} className="run-card">
                  <div className="run-card-meta">
                    <span>#{run.task_index + 1}</span>
                    <span className={`run-status ${run.status}`}>{run.status}</span>
                    <span title={run.execution_id}>Exec: {run.execution_id.slice(0, 8)}...</span>
                    <span>{new Date(run.created_at).toLocaleString()}</span>
                  </div>
                  {(run.source || run.trigger_id || run.correlation_id) && (
                    <div className="run-card-label">
                      Source: {run.source || 'task'}
                      {run.trigger_id ? ` · Trigger: ${run.trigger_id}` : ''}
                      {run.correlation_id ? ` · Correlation: ${run.correlation_id}` : ''}
                    </div>
                  )}
                  {(run.selected_agent || run.selected_provider || run.selected_model) && (
                    <div className="run-card-label">
                      Selected: {run.selected_agent || 'N/A'} · {run.selected_provider || 'provider?'} / {run.selected_model || 'model?'}
                    </div>
                  )}
                  {run.routing_reason && <div className="run-card-text">Routing: {run.routing_reason}</div>}
                  {run.decision_json?.scores?.length ? (
                    <div className="run-scores">
                      {run.decision_json.scores.map((score, idx) => (
                        <div key={`${run.id}-score-${idx}`} className="run-score-item">
                          <strong>{score.agent || 'Agent'}</strong>: {score.score ?? 0} - {score.reason || ''}
                        </div>
                      ))}
                    </div>
                  ) : null}
                  <div className="run-card-label">Input</div>
                  <div className="run-card-text">{run.task_input}</div>
                  {run.final_output && (
                    <>
                      <div className="run-card-label">Output</div>
                      <div className="run-card-text">{run.final_output}</div>
                    </>
                  )}
                  {run.error_message && (
                    <div className="run-card-error">Error: {run.error_message}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamManager;
