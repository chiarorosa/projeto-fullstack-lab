import type { ReactNode } from 'react';

type FeatureListItemProps = {
  title: string;
  description?: ReactNode;
  status?: string;
  link?: ReactNode;
};

function FeatureListItem({ title, description, status, link }: FeatureListItemProps) {
  return (
    <div className="feature-item">
      <div className="feature-content">
        <div className="feature-title">{title}</div>
        {description ? <div className="feature-description">{description}</div> : null}
      </div>
      <div className="feature-meta">
        {status ? <span className="feature-status">{status}</span> : null}
        {link ? <div className="feature-link">{link}</div> : null}
      </div>
    </div>
  );
}

export default FeatureListItem;
