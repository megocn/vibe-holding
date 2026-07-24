import type { ReactNode } from 'react';
import { BrandSeal } from './BrandSeal.tsx';
import { Icon } from './Icon.tsx';

interface EmptyStateProps {
  title: string;
  hint?: string;
  icon?: string;
  seal?: boolean;
  action?: ReactNode;
}

/** 空状态：Duotone / 印章 + 臻楷标题（设计规范 §10） */
export function EmptyState({ title, hint, icon = 'Compass', seal, action }: EmptyStateProps) {
  return (
    <div className="vh-empty">
      {seal ? <BrandSeal size={40} /> : <Icon name={icon} size={48} weight="duotone" />}
      <div className="vh-text-h2" style={{ color: 'var(--ink-2)', margin: 0 }}>
        {title}
      </div>
      {hint && (
        <p className="vh-text-sm" style={{ margin: 0, maxWidth: '28em', color: 'var(--ink-3)' }}>
          {hint}
        </p>
      )}
      {action}
    </div>
  );
}
