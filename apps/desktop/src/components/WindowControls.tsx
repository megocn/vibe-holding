import { winClose, winMinimize, winToggleMaximize } from '../lib/platform.ts';
import { Icon } from './Icon.tsx';

export function WindowControls() {
  return (
    <div className="flex items-center gap-1" style={{ marginLeft: 4 }}>
      <Ctrl name="Minus" title="最小化" onClick={winMinimize} />
      <Ctrl name="Square" title="最大化" onClick={winToggleMaximize} />
      <Ctrl name="X" title="关闭" onClick={winClose} danger />
    </div>
  );
}

function Ctrl({
  name,
  title,
  onClick,
  danger,
}: {
  name: string;
  title: string;
  onClick: () => void;
  danger?: boolean;
}) {
  return (
    <button
      type="button"
      title={title}
      onClick={onClick}
      className="flex items-center justify-center"
      style={{
        width: 26,
        height: 26,
        border: 'none',
        borderRadius: 'var(--radius-sm)',
        background: 'transparent',
        color: 'var(--ink-2)',
        cursor: 'pointer',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = danger ? 'var(--pigment-danger)' : 'var(--paper-2)';
        e.currentTarget.style.color = danger ? 'var(--paper-0)' : 'var(--ink-1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'transparent';
        e.currentTarget.style.color = 'var(--ink-2)';
      }}
    >
      <Icon name={name} size={14} />
    </button>
  );
}
