import type { Entry, EntryRanking, Id } from '@vh/core';
import { formatRankingPrimary } from '@vh/core';
import { useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import { MATURITY_LABELS, PRICING_LABELS, REGION_LABELS } from '../lib/filters.ts';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';

const MAX_COMPARE = 4;

interface CompareViewProps {
  ids: Id[];
  onChange: (ids: Id[]) => void;
  onOpenEntry: (id: Id) => void;
}

type Dim =
  | { key: string; label: string; get: (e: Entry) => string; mono?: boolean }
  | { key: string; label: string; getList: (e: Entry) => string[] };

const BASE_DIMS: Dim[] = [
  { key: 'category', label: '分类', get: (e) => e.category },
  {
    key: 'grain',
    label: '粒度',
    get: (e) =>
      e.category === 'llm-family'
        ? '产品族'
        : e.category === 'llm-line'
          ? '选型档位'
          : '—',
  },
  {
    key: 'currentVersion',
    label: '当前版本',
    get: (e) => e.currentVersion ?? '—',
    mono: true,
  },
  { key: 'region', label: '地区', get: (e) => REGION_LABELS[e.region] ?? e.region },
  { key: 'maturity', label: '成熟度', get: (e) => MATURITY_LABELS[e.maturity] ?? e.maturity },
  {
    key: 'pricing',
    label: '定价模型',
    get: (e) => PRICING_LABELS[e.pricing.model] ?? e.pricing.model,
  },
  { key: 'priceNotes', label: '定价说明', get: (e) => e.pricing.notes ?? '—' },
  { key: 'vendor', label: '厂商', get: (e) => e.vendorId ?? '—' },
  {
    key: 'china',
    label: '国内可访问',
    get: (e) => (e.availability.chinaAccessible ? '是' : '否'),
  },
  {
    key: 'company',
    label: '需公司主体',
    get: (e) => (e.availability.needsCompany ? '是' : '否'),
  },
  { key: 'icp', label: '需备案', get: (e) => (e.availability.needsIcp ? '是' : '否') },
  { key: 'oneLiner', label: '选型一句话', get: (e) => e.oneLiner },
  { key: 'official', label: '官网', get: (e) => e.officialUrl, mono: true },
  { key: 'reviewed', label: '最近复核', get: (e) => e.lastReviewed, mono: true },
  { key: 'tags', label: '标签', getList: (e) => e.tags },
  { key: 'pitfalls', label: '坑点', getList: (e) => e.pitfalls },
];

function rankingLookup(e: Entry, systemId: string): EntryRanking | undefined {
  return e.rankings.find((r) => r.systemId === systemId);
}

export function CompareView({ ids, onChange, onOpenEntry }: CompareViewProps) {
  const { bundle } = useContent();
  const entries = ids.map((id) => bundle.entries.get(id)).filter((e): e is Entry => e != null);

  const dims = useMemo(() => {
    const systemIds = new Set<string>();
    for (const e of entries) {
      for (const r of e.rankings) systemIds.add(r.systemId);
      for (const s of bundle.rankingSystems.values()) {
        if (s.categories.includes(e.category)) systemIds.add(s.id);
      }
    }
    const rankingDims: Dim[] = [...systemIds]
      .map((sid) => bundle.rankingSystems.get(sid))
      .filter((s): s is NonNullable<typeof s> => s != null)
      .sort((a, b) => a.order - b.order || a.shortName.localeCompare(b.shortName))
      .map((sys) => ({
        key: `rank:${sys.id}`,
        label: `排行 · ${sys.shortName}`,
        get: (e: Entry) => {
          const r = rankingLookup(e, sys.id);
          if (!r) return '—';
          const primary = formatRankingPrimary(r, sys);
          return r.period ? `${primary}（${r.period}）` : primary;
        },
      }));
    return [...BASE_DIMS.slice(0, 5), ...rankingDims, ...BASE_DIMS.slice(5)];
  }, [bundle.rankingSystems, entries]);

  const grainWarn = useMemo(() => {
    const grains = new Set(
      entries
        .map((e) =>
          e.category === 'llm-family' || e.category === 'llm-line' ? e.category : null,
        )
        .filter(Boolean),
    );
    return grains.size > 1;
  }, [entries]);

  function remove(id: Id) {
    onChange(ids.filter((x) => x !== id));
  }

  function cellValue(dim: Dim, e: Entry): string {
    if ('getList' in dim) {
      const list = dim.getList(e);
      return list.length ? list.join(' · ') : '—';
    }
    const v = dim.get(e);
    if (dim.key === 'category') return bundle.categories.find((c) => c.id === v)?.name ?? v;
    if (dim.key === 'vendor' && v !== '—') return bundle.vendors.get(v)?.name ?? v;
    return v || '—';
  }

  function isDiff(dim: Dim): boolean {
    if (entries.length < 2) return false;
    const vals = entries.map((e) => cellValue(dim, e));
    return new Set(vals).size > 1;
  }

  return (
    <div className="flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      <header className="vh-page-header">
        <div style={{ flex: 1 }}>
          <div className="vh-page-kicker">并观 · 差异高亮</div>
          <h1>对比</h1>
        </div>
        <span className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)' }}>
          {entries.length}/{MAX_COMPARE}
        </span>
        {entries.length > 0 && (
          <button type="button" className="vh-btn" onClick={() => onChange([])}>
            清空
          </button>
        )}
      </header>

      {entries.length === 0 ? (
        <EmptyState
          icon="Columns"
          title="尚未点选对照"
          hint={`在知识库详情点「加入对比」，或列表勾选条目（最多 ${MAX_COMPARE} 个）。差异行会以赭石淡染标出。`}
        />
      ) : (
        <div className="overflow-auto" style={{ flex: 1, padding: 16 }}>
          {grainWarn && (
            <div
              className="vh-tag"
              data-tone="warning"
              style={{
                display: 'block',
                marginBottom: 12,
                padding: '8px 12px',
                whiteSpace: 'normal',
              }}
            >
              对比里混入了「产品族」与「选型档位」——粒度不同，排行与价格不宜直接横比。建议只对比同为档位的条目（如 Claude Opus ↔ Kimi 旗舰 ↔ Qwen-Max）。
            </div>
          )}
          <table className="vh-compare-table" style={{ minWidth: 200 + entries.length * 180 }}>
            <thead>
              <tr>
                <th
                  style={{
                    position: 'sticky',
                    left: 0,
                    background: 'var(--paper-1)',
                    zIndex: 1,
                    minWidth: 110,
                  }}
                >
                  维度
                </th>
                {entries.map((e) => (
                  <th key={e.id} style={{ minWidth: 180 }}>
                    <div className="flex items-start gap-2">
                      <button
                        type="button"
                        className="vh-link vh-display"
                        style={{
                          border: 'none',
                          background: 'transparent',
                          cursor: 'pointer',
                          padding: 0,
                          fontSize: 16,
                          textAlign: 'left',
                        }}
                        onClick={() => onOpenEntry(e.id)}
                      >
                        {e.name}
                      </button>
                      <button
                        type="button"
                        className="vh-btn"
                        title="移出对比"
                        aria-label="移出对比"
                        onClick={() => remove(e.id)}
                        style={{ padding: '2px 6px', marginLeft: 'auto' }}
                      >
                        <Icon name="X" size={12} />
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dims.map((dim) => {
                const diff = isDiff(dim);
                return (
                  <tr key={dim.key} data-diff={diff ? 'true' : 'false'}>
                    <td
                      style={{
                        position: 'sticky',
                        left: 0,
                        background: diff
                          ? 'color-mix(in oklch, var(--pigment-warning) 10%, var(--paper-1))'
                          : 'var(--paper-1)',
                        fontWeight: 500,
                        color: 'var(--ink-2)',
                        zIndex: 1,
                      }}
                    >
                      {dim.label}
                      {diff && (
                        <span className="vh-tag" data-tone="warning" style={{ marginLeft: 6 }}>
                          异
                        </span>
                      )}
                    </td>
                    {entries.map((e) => {
                      const text = cellValue(dim, e);
                      const mono = !('getList' in dim) && dim.mono;
                      return (
                        <td
                          key={e.id}
                          style={{
                            color: 'var(--ink-1)',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                          }}
                          className={mono ? 'vh-mono' : undefined}
                        >
                          {dim.key === 'official' && text !== '—' ? (
                            <a
                              className="vh-link vh-mono"
                              href={text}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {text}
                            </a>
                          ) : (
                            text
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export { MAX_COMPARE };
