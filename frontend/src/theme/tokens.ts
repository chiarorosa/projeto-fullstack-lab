export const NODE_TYPE_COLORS = {
  task: '#238636',
  webhook: '#d29922',
  agent: '#1f6feb',
  llm: '#2ea043',
  tool: '#8b949e',
} as const;

export const PROVIDER_COLORS: Record<string, string> = {
  openai: '#58a6ff',
  anthropic: '#d29922',
  google: '#1f6feb',
  local: '#a371f7',
  openrouter: '#238636',
  opencode: '#238636',
};

export const FLOW_THEME = {
  edgeStroke: NODE_TYPE_COLORS.agent,
  backgroundDots: '#30363d',
  minimapMask: 'rgba(13, 17, 23, 0.62)',
} as const;
