import type { Id } from '@vh/core';
import { useMemo, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { Icon } from './Icon.tsx';
import { RelationPanel } from './RelationPanel.tsx';

interface MobileRelationsViewProps {
  focusId: Id | null;
  onFocus: (id: Id | null) => void;
  onOpenInKnowledge: (id: Id) => void;
}

/** 窄屏图谱降级：关联分组列表，不渲染 Cytoscape。 */
export function MobileRelationsView({
  focusId,
  onFocus,
  onOpenInKnowledge,
}: MobileRelationsViewProps) {
  const { bundle, index } = useContent();
  const [query, setQuery] = useState('');
  const entry = focusId ? bundle.entries.get(focusId) : undefined;

  const suggestions = useMemo(() => {
    if (!query.trim()) return [];
    return index
      .query(query, {})
      .slice(0, 12)
      .map((r) => r.id);
  }, [index, query]);

  return (
    <div className="vh-mobile-relations flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      <header className="vh-mobile-relations-head">
        <div className="vh-display" style={{ fontSize: 18, color: 'var(--ink-1)' }}>
          关联速查
        </div>
        <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--ink-3)' }}>
          窄屏不渲染全图，按关系分组浏览邻域。
        </p>
      </header>

      <div className="vh-mobile-relations-search">
        <Icon name="MagnifyingGlass" size={16} color="var(--ink-3)" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索并设为焦点…"
          aria-label="搜索焦点条目"
        />
      </div>

      {query.trim() && suggestions.length > 0 && (
        <ul className="vh-mobile-relations-suggest">
          {suggestions.map((id) => {
            const e = bundle.entries.get(id);
            if (!e) return null;
            return (
              <li key={id}>
                <button
                  type="button"
                  onClick={() => {
                    onFocus(id);
                    setQuery('');
                  }}
                >
                  <span>{e.name}</span>
                  <span className="vh-text-caption" style={{ color: 'var(--ink-3)' }}>
                    {e.oneLiner}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}

      <div className="vh-mobile-relations-body">
        {entry ? (
          <>
            <div className="vh-mobile-relations-focus">
              <div>
                <div className="vh-display" style={{ fontSize: 16 }}>
                  {entry.name}
                </div>
                <div className="vh-text-caption" style={{ color: 'var(--ink-3)', marginTop: 2 }}>
                  {entry.oneLiner}
                </div>
              </div>
              <button
                type="button"
                className="vh-btn"
                onClick={() => onOpenInKnowledge(entry.id)}
              >
                打开详情
              </button>
            </div>
            <RelationPanel id={entry.id} onSelect={(id) => onFocus(id)} />
          </>
        ) : (
          <div style={{ padding: 24, color: 'var(--ink-3)', fontSize: 14, textAlign: 'center' }}>
            搜索并选择一个条目作为焦点，查看其关联分组。
          </div>
        )}
      </div>
    </div>
  );
}
