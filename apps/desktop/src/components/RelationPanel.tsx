import type { Edge, Id } from '@vh/core';
import { useMemo } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import { relMeta } from '../lib/relations.ts';
import { useUserData } from '../lib/userdata.tsx';
import { Icon } from './Icon.tsx';

interface RelationPanelProps {
  id: Id;
  onSelect: (id: Id) => void;
  onEditEdge?: (edgeId: Id) => void;
  onAddEdge?: (fromId: Id) => void;
}

export function RelationPanel({ id, onSelect, onEditEdge, onAddEdge }: RelationPanelProps) {
  const { bundle, graph, isEntry, resolveName } = useContent();
  const { isEdgeOverridden } = useContentEditor();
  const { data } = useUserData();
  const groups = graph.related(id);
  const keys = Object.keys(groups).sort();

  const edgesHere = bundle.edges.filter((e) => e.from === id || e.to === id);

  const personalNeighbors = useMemo(() => {
    const out: { id: Id; weight: number; note?: string }[] = [];
    for (const e of data.personalEdges) {
      if (e.from === id) out.push({ id: e.to, weight: e.weight, note: e.note });
      else if (e.to === id) out.push({ id: e.from, weight: e.weight, note: e.note });
    }
    return out.sort((a, b) => b.weight - a.weight);
  }, [data.personalEdges, id]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        {onAddEdge && (
          <button
            type="button"
            className="vh-btn flex items-center gap-1.5"
            onClick={() => onAddEdge(id)}
          >
            <Icon name="Plus" size={14} /> 添加关系
          </button>
        )}
        <span style={{ fontSize: 12, color: 'var(--ink-3)' }}>{edgesHere.length} 条边</span>
      </div>

      {keys.length === 0 && edgesHere.length === 0 && personalNeighbors.length === 0 && (
        <div style={{ color: 'var(--ink-3)', fontSize: 14 }}>暂无关联。</div>
      )}

      {personalNeighbors.length > 0 && (
        <div>
          <div
            className="flex items-center gap-2"
            style={{ color: 'var(--pigment-primary)', fontSize: 13, marginBottom: 6 }}
          >
            <Icon name="User" size={16} />
            <span>个人共现（私有）</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {personalNeighbors.map((n) => {
              const clickable = isEntry(n.id);
              return (
                <button
                  key={n.id}
                  type="button"
                  className="vh-tag"
                  title={n.note}
                  onClick={clickable ? () => onSelect(n.id) : undefined}
                  style={{
                    cursor: clickable ? 'pointer' : 'default',
                    color: 'var(--pigment-primary)',
                    background: 'var(--paper-1)',
                    borderColor: 'var(--pigment-primary)',
                  }}
                >
                  {resolveName(n.id)} · {n.weight.toFixed(2)}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {keys.map((key) => {
        const meta = relMeta(key);
        const targets = groups[key] ?? [];
        return (
          <div key={key}>
            <div
              className="flex items-center gap-2"
              style={{ color: 'var(--ink-2)', fontSize: 13, marginBottom: 6 }}
            >
              <Icon name={meta.icon} size={16} />
              <span>{meta.label}</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {targets.map((tid) => {
                const clickable = isEntry(tid);
                const edge = findEdge(edgesHere, id, tid, key);
                return (
                  <span key={tid} className="flex items-center gap-1">
                    <button
                      type="button"
                      className="vh-tag"
                      onClick={clickable ? () => onSelect(tid) : undefined}
                      style={{
                        cursor: clickable ? 'pointer' : 'default',
                        color: clickable ? 'var(--pigment-primary)' : 'var(--ink-2)',
                        background: 'var(--paper-1)',
                      }}
                    >
                      {resolveName(tid)}
                    </button>
                    {edge && onEditEdge && (
                      <button
                        type="button"
                        className="vh-btn"
                        title="编辑边"
                        onClick={() => onEditEdge(edge.id)}
                        style={{ padding: '2px 6px' }}
                      >
                        <Icon
                          name="PencilSimple"
                          size={12}
                          color={isEdgeOverridden(edge.id) ? 'var(--pigment-warning)' : undefined}
                        />
                      </button>
                    )}
                  </span>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** 在当前条目视角下，找连接 other 且「有效类型」匹配的边。 */
function findEdge(edges: Edge[], self: Id, other: Id, effectiveType: string): Edge | undefined {
  return edges.find((e) => {
    if (!((e.from === self && e.to === other) || (e.from === other && e.to === self))) return false;
    if (e.from === self) return e.type === effectiveType;
    return true;
  });
}
