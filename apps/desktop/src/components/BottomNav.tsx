import { useEffect, useRef, useState } from 'react';
import { SECTIONS, type SectionId } from '../lib/sections.ts';
import { Icon } from './Icon.tsx';

const PRIMARY: SectionId[] = ['dashboard', 'knowledge', 'graph', 'recipes'];
const MORE: SectionId[] = ['intel', 'compare', 'settings'];

interface BottomNavProps {
  active: SectionId;
  onSelect: (id: SectionId) => void;
  /** 是否展示凭据（仅桌面 Tauri 宽屏） */
  includeCredentials?: boolean;
}

export function BottomNav({ active, onSelect, includeCredentials = false }: BottomNavProps) {
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  const moreIds = includeCredentials ? [...MORE, 'credentials' as SectionId] : MORE;
  const moreActive = moreIds.includes(active) || active === 'kitchen';

  useEffect(() => {
    if (!moreOpen) return;
    function onDoc(e: MouseEvent) {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) {
        setMoreOpen(false);
      }
    }
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [moreOpen]);

  function pick(id: SectionId) {
    setMoreOpen(false);
    onSelect(id);
  }

  return (
    <nav className="vh-bottom-nav" aria-label="主导航">
      {PRIMARY.map((id) => {
        const s = SECTIONS.find((x) => x.id === id)!;
        const on = active === id;
        return (
          <button
            key={id}
            type="button"
            className="vh-bottom-nav-item"
            data-active={on ? 'true' : 'false'}
            aria-current={on ? 'page' : undefined}
            onClick={() => pick(id)}
          >
            <Icon name={s.icon} size={22} weight={on ? 'fill' : 'regular'} />
            <span>{s.label}</span>
          </button>
        );
      })}
      <div className="vh-bottom-nav-more" ref={moreRef}>
        {moreOpen && (
          <div className="vh-bottom-nav-sheet" role="menu">
            {moreIds.map((id) => {
              const s = SECTIONS.find((x) => x.id === id)!;
              const on = active === id || (id === 'settings' && active === 'kitchen');
              return (
                <button
                  key={id}
                  type="button"
                  role="menuitem"
                  className="vh-bottom-nav-sheet-item"
                  data-active={on ? 'true' : 'false'}
                  onClick={() => pick(id)}
                >
                  <Icon name={s.icon} size={20} weight={on ? 'fill' : 'regular'} />
                  <span>{s.label}</span>
                </button>
              );
            })}
          </div>
        )}
        <button
          type="button"
          className="vh-bottom-nav-item"
          data-active={moreActive ? 'true' : 'false'}
          aria-expanded={moreOpen}
          aria-haspopup="menu"
          onClick={() => setMoreOpen((o) => !o)}
        >
          <Icon name="DotsThreeOutline" size={22} weight={moreActive ? 'fill' : 'regular'} />
          <span>更多</span>
        </button>
      </div>
    </nav>
  );
}
