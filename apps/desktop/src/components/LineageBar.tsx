import type { Id } from '@vh/core';
import { familyIdOf, lineIdsOfFamily } from '@vh/core';
import { useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import { Icon } from './Icon.tsx';

interface LineageBarProps {
  entryId: Id;
  onSelect: (id: Id) => void;
}

/**
 * LLM 等族谱条：产品族 › 选型档位 · 当前版本
 * 版本不单独成条目，只展示 currentVersion。
 */
export function LineageBar({ entryId, onSelect }: LineageBarProps) {
  const { bundle } = useContent();
  const entry = bundle.entries.get(entryId);
  const cat = bundle.categories.find((c) => c.id === entry?.category);

  const lineage = useMemo(() => {
    if (!entry) return null;
    const isFamily = entry.category === 'llm-family';
    const isLine = entry.category === 'llm-line';
    if (!isFamily && !isLine) return null;

    if (isFamily) {
      const lines = lineIdsOfFamily(bundle.edges, entry.id)
        .map((id) => bundle.entries.get(id))
        .filter(Boolean);
      return { kind: 'family' as const, family: entry, lines };
    }

    const famId = familyIdOf(bundle.edges, entry.id);
    const family = famId ? bundle.entries.get(famId) : undefined;
    const siblings = famId
      ? lineIdsOfFamily(bundle.edges, famId).filter((id) => id !== entry.id)
      : [];
    return {
      kind: 'line' as const,
      family,
      line: entry,
      siblings,
      version: entry.currentVersion,
    };
  }, [bundle.edges, bundle.entries, entry]);

  if (!lineage || !entry) return null;

  return (
    <div className="vh-lineage" style={{ marginTop: 12 }}>
      <div
        className="flex flex-wrap items-center gap-2"
        style={{ fontSize: 13, color: 'var(--ink-2)' }}
      >
        <span className="vh-tag" data-tone="seal">
          {lineage.kind === 'family' ? '产品族' : '选型档位'}
        </span>
        {lineage.kind === 'line' && lineage.family && (
          <>
            <button
              type="button"
              className="vh-link"
              onClick={() => onSelect(lineage.family!.id)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--pigment-primary)',
                cursor: 'pointer',
                padding: 0,
                fontFamily: 'var(--font-body)',
              }}
            >
              {lineage.family.name}
            </button>
            <span style={{ opacity: 0.5 }}>›</span>
            <span style={{ fontWeight: 600, color: 'var(--ink-1)' }}>{entry.name}</span>
          </>
        )}
        {lineage.kind === 'family' && (
          <span style={{ fontWeight: 600, color: 'var(--ink-1)' }}>{entry.name}</span>
        )}
        {lineage.kind === 'line' && lineage.version && (
          <span
            className="vh-tag"
            title="当前版本（非独立条目）"
            style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}
          >
            <Icon name="GitBranch" size={12} /> 版本 {lineage.version}
          </span>
        )}
      </div>

      {lineage.kind === 'family' && lineage.lines.length > 0 && (
        <div className="flex flex-wrap gap-2" style={{ marginTop: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--ink-3)' }}>下属档位</span>
          {lineage.lines.map((line) =>
            line ? (
              <button
                key={line.id}
                type="button"
                className="vh-tag"
                onClick={() => onSelect(line.id)}
                style={{ cursor: 'pointer' }}
              >
                {line.name}
                {line.currentVersion ? ` · ${line.currentVersion}` : ''}
              </button>
            ) : null,
          )}
        </div>
      )}

      {lineage.kind === 'line' && lineage.siblings.length > 0 && (
        <div className="flex flex-wrap gap-2" style={{ marginTop: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--ink-3)' }}>同族其他档位</span>
          {lineage.siblings.map((sid) => {
            const s = bundle.entries.get(sid);
            if (!s) return null;
            return (
              <button
                key={sid}
                type="button"
                className="vh-tag"
                onClick={() => onSelect(sid)}
                style={{ cursor: 'pointer' }}
              >
                {s.name}
              </button>
            );
          })}
        </div>
      )}

      {(cat?.id === 'llm-family' || cat?.id === 'llm-line') && (
        <p style={{ margin: '8px 0 0', fontSize: 12, color: 'var(--ink-3)' }}>
          上下层：产品族 › 选型档位 › 版本（写在档位上，不建条目）。Arena / 价格对比挂在档位层。
        </p>
      )}
    </div>
  );
}
