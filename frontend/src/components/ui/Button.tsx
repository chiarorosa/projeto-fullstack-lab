import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'icon';

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
  }
>;

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  ghost: 'btn-ghost',
  icon: 'btn-icon',
};

function Button({ variant = 'ghost', className = '', type = 'button', children, ...props }: ButtonProps) {
  const variantClass = VARIANT_CLASS[variant];
  const mergedClassName = `${variantClass} ${className}`.trim();

  return (
    <button type={type} className={mergedClassName} {...props}>
      {children}
    </button>
  );
}

export default Button;
