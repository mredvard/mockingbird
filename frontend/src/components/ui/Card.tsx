import { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  elevated?: boolean;
}

export function Card({ children, elevated = false, className = '', ...props }: CardProps) {
  const baseStyles = 'bg-white rounded-lg border border-gray-200';
  const elevationStyles = elevated ? 'shadow-lg' : 'shadow-sm';

  return (
    <div className={`${baseStyles} ${elevationStyles} ${className}`} {...props}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return <div className={`px-6 py-4 border-b border-gray-200 ${className}`}>{children}</div>;
}

interface CardBodyProps {
  children: ReactNode;
  className?: string;
}

export function CardBody({ children, className = '' }: CardBodyProps) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
}

interface CardFooterProps {
  children: ReactNode;
  className?: string;
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return <div className={`px-6 py-4 border-t border-gray-200 ${className}`}>{children}</div>;
}
