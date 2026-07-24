import { navSections, type SectionId } from '../lib/sections.ts';
import { Icon } from './Icon.tsx';

interface RailProps {
  active: SectionId;
  onSelect: (id: SectionId) => void;
  includeCredentials?: boolean;
}

export function Rail({ active, onSelect, includeCredentials = true }: RailProps) {
  const sections = navSections(includeCredentials);
  return (
    <nav
      className="vh-shell-rail flex flex-col gap-1 overflow-y-auto"
      style={{
        width: 88,
        padding: '12px 8px',
        flexShrink: 0,
      }}
      aria-label="主导航"
    >
      {sections.map((s) => {
        const on = s.id === active;
        return (
          <button
            key={s.id}
            type="button"
            title={s.ready ? s.label : `${s.label}（开发中）`}
            aria-label={s.label}
            aria-current={on ? 'page' : undefined}
            onClick={() => onSelect(s.id)}
            className="vh-rail-item flex flex-col items-center justify-center gap-1"
            data-active={on ? 'true' : 'false'}
            style={{
              width: '100%',
              minHeight: 56,
              padding: '8px 4px',
              opacity: s.ready ? 1 : 0.55,
            }}
          >
            <Icon name={s.icon} size={22} weight={on ? 'fill' : 'regular'} />
            <span
              className="vh-rail-label"
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: 13,
                lineHeight: 1.2,
                letterSpacing: '0.02em',
                color: 'inherit',
              }}
            >
              {s.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
