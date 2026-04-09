import type { HTMLAttributes, PropsWithChildren } from 'react';

type CardProps = PropsWithChildren<HTMLAttributes<HTMLDivElement>>;

function Card({ className = '', children, ...props }: CardProps) {
  const mergedClassName = `ui-card ${className}`.trim();
  return (
    <div className={mergedClassName} {...props}>
      {children}
    </div>
  );
}

export default Card;
