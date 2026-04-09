type ProgressBarProps = {
  value: number;
  label?: string;
};

function ProgressBar({ value, label }: ProgressBarProps) {
  const normalized = Math.max(0, Math.min(100, value));

  return (
    <div className="progress-wrap" aria-label={label || 'Progress'}>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
}

export default ProgressBar;
