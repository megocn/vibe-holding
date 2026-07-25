import type { Entry, Id, PricingModel } from '@vh/core';
import {
  computeProminence,
  entryRankingForSystem,
  formatRankingPrimary,
  leavesOfSection,
  primaryRankingSystem,
  sectionIdOf,
  sortIdsByPrimaryRanking,
} from '@vh/core';
import { CATEGORY_ICONS, CATEGORY_LAYERS, layerOfCategory } from '@vh/ui';
import { useCallback, useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import { formatReviewedRelative, isStale } from '../lib/intel.ts';
import { buildLlmFamilyTree, isLlmSectionNav } from '../lib/llm-tree.ts';
import { useUserData } from '../lib/userdata.tsx';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';
import type { KbNav } from './Sidebar.tsx';

interface EntryListProps {
  ids: Id[];
  selectedId: Id | null;
  onSelect: (id: Id) => void;
  compareIds?: Id[];
  onToggleCompare?: (id: Id) => void;
  /** 当前导航；「全部」时按卷分组列表 */
  nav?: KbNav;
}

export function EntryList({
  ids,
  selectedId,
  onSelect,
  compareIds = [],
  onToggleCompare,
  nav = { kind: 'all' },
}: EntryListProps) {
  const { bundle, categories } = useContent();
  const { isFavorite, getRating } = useUserData();
  const catName = useMemo(() => new Map(categories.map((c) => [c.id, c])), [categories]);

  // 外部客观流行度 → 同类突出度分（无权威榜时兜底排序用）
  const prominence = useMemo(
    () => computeProminence(bundle.entries.values(), bundle.popularity),
    [bundle.entries, bundle.popularity],
  );

  const sortGroup = useCallback(
    (groupIds: Id[]) =>
      sortIdsByPrimaryRanking(
        groupIds,
        (id) => {
          const e = bundle.entries.get(id);
          if (!e) return undefined;
          return {
            category: e.category,
            name: e.name,
            rankings: e.rankings,
            maturity: e.maturity,
          };
        },
        bundle.rankingSystems.values(),
        { prominenceOf: (id) => prominence.get(id) },
      ),
    [bundle.entries, bundle.rankingSystems, prominence],
  );

  const primaryLabel = useMemo(() => {
    if (nav.kind === 'family') return '按榜单综合分排序（旗舰聚合）';
    if (nav.kind !== 'category') return null;
    if (isLlmSectionNav(nav.categoryId, categories)) return '按榜单综合分排序（旗舰聚合）';
    const sys = primaryRankingSystem(bundle.rankingSystems.values(), nav.categoryId);
    const catEntries = [...bundle.entries.values()].filter((e) => e.category === nav.categoryId);
    // 仅当类内确有主榜快照时宣称「按权威榜」；否则诚实标流行度兜底
    const hasPrimarySnap =
      !!sys &&
      catEntries.some((e) => entryRankingForSystem(e.rankings, sys.id) != null);
    if (hasPrimarySnap && sys) return `按 ${sys.shortName} 排序`;
    const hasSignal = catEntries.some((e) => prominence.has(e.id));
    return hasSignal ? '按流行度排序（GitHub/域名等外部信号）' : null;
  }, [nav, bundle.rankingSystems, bundle.entries, categories, prominence]);

  const groups = useMemo(() => {
    type ListGroup = {
      key: string;
      label: string | null;
      code?: string;
      subtitle?: string;
      isLayer?: boolean;
      /** LLM 族头：可点开族详情 */
      familyId?: Id;
      ids: Id[];
    };
    const entrySection = (entryCategory: Id) => sectionIdOf(categories, entryCategory);

    const llmTreeGroups = (familyFilter?: Id): ListGroup[] => {
      const tree = buildLlmFamilyTree(bundle);
      const out: ListGroup[] = [];
      for (const n of tree) {
        if (familyFilter && n.familyId !== familyFilter) continue;
        const scope = [n.familyId, ...n.lineIds].filter((id) => ids.includes(id));
        // 列表里族头单独展示，ids 只放档位（上下层更清晰）
        const lineOnly = n.lineIds.filter((id) => ids.includes(id));
        if (scope.length === 0) continue;
        out.push({
          key: `fam:${n.familyId}`,
          label: n.familyName,
          subtitle: '产品族',
          familyId: n.familyId,
          ids: sortGroup(lineOnly.length > 0 ? lineOnly : scope),
        });
      }
      return out;
    };

    if (nav.kind === 'family') {
      return llmTreeGroups(nav.familyId);
    }

    if (nav.kind === 'category') {
      const cat = catName.get(nav.categoryId);
      if (isLlmSectionNav(nav.categoryId, categories)) {
        return llmTreeGroups();
      }
      if (cat?.kind === 'section') {
        const leaves = leavesOfSection(categories, nav.categoryId);
        return leaves
          .map(
            (leaf): ListGroup => ({
              key: leaf.id,
              label: leaf.name,
              ids: sortGroup(ids.filter((id) => bundle.entries.get(id)?.category === leaf.id)),
            }),
          )
          .filter((g) => g.ids.length > 0);
      }
      return [{ key: nav.categoryId, label: null, ids: sortGroup(ids) } satisfies ListGroup];
    }
    if (nav.kind === 'layer') {
      const layer = CATEGORY_LAYERS.find((l) => l.id === nav.layerId);
      if (!layer) return [{ key: 'all', label: null, ids: sortGroup(ids) } satisfies ListGroup];
      return layer.categories.flatMap((cid): ListGroup[] => {
        if (cid === 'llm') return llmTreeGroups();
        return [
          {
            key: cid,
            label: catName.get(cid)?.name ?? cid,
            code: catName.get(cid)?.code,
            ids: sortGroup(
              ids.filter((id) => {
                const e = bundle.entries.get(id);
                return e != null && entrySection(e.category) === cid;
              }),
            ),
          },
        ].filter((g) => g.ids.length > 0);
      });
    }
    return CATEGORY_LAYERS.flatMap((layer): ListGroup[] => {
      const layerIds = ids.filter((id) => {
        const e = bundle.entries.get(id);
        return e && layer.categories.includes(entrySection(e.category));
      });
      if (layerIds.length === 0) return [];
      return [
        {
          key: `layer:${layer.id}`,
          label: layer.label,
          subtitle: layer.subtitle,
          isLayer: true,
          ids: [],
        },
        ...layer.categories.flatMap((cid): ListGroup[] => {
          if (cid === 'llm') {
            // 全部视图下 LLM 也按族›档
            const out: ListGroup[] = [];
            for (const n of buildLlmFamilyTree(bundle)) {
              const lineOnly = n.lineIds.filter((id) => layerIds.includes(id));
              if (lineOnly.length === 0 && !layerIds.includes(n.familyId)) continue;
              out.push({
                key: `fam:${n.familyId}`,
                label: n.familyName,
                subtitle: `${catName.get('llm')?.code ?? 'B'} · 产品族`,
                familyId: n.familyId,
                ids: sortGroup(lineOnly),
              });
            }
            return out;
          }
          return [
            {
              key: cid,
              label: catName.get(cid)?.name ?? cid,
              code: catName.get(cid)?.code,
              ids: sortGroup(
                layerIds.filter((id) => {
                  const e = bundle.entries.get(id);
                  return e != null && entrySection(e.category) === cid;
                }),
              ),
            },
          ].filter((g) => g.ids.length > 0);
        }),
      ];
    });
  }, [ids, nav, bundle, catName, categories, sortGroup]);

  if (ids.length === 0) {
    return (
      <EmptyState
        title="无匹配条目"
        hint="调整筛选或搜索词，换一条航路再探。"
        icon="MagnifyingGlass"
      />
    );
  }

  return (
    <div className="vh-kb-list flex flex-col overflow-y-auto">
      {primaryLabel && <div className="vh-kb-list-sort-hint vh-text-caption">{primaryLabel}</div>}
      {groups.map((g) => {
        if ('isLayer' in g && g.isLayer) {
          return (
            <div key={g.key} className="vh-kb-list-layer">
              <span className="vh-kb-list-layer-name">{g.label}</span>
              {g.subtitle ? <span className="vh-kb-list-layer-sub">{g.subtitle}</span> : null}
            </div>
          );
        }
        const rankingLeaf =
          g.familyId != null
            ? 'llm-line'
            : g.key && !String(g.key).startsWith('layer:') && !String(g.key).startsWith('fam:')
              ? String(g.key)
              : undefined;
        const groupPrimary = rankingLeaf
          ? primaryRankingSystem(bundle.rankingSystems.values(), rankingLeaf)
          : undefined;
        return (
          <div key={g.key} className="vh-kb-list-group">
            {g.label && (
              <div className="vh-kb-list-cat">
                {g.code ? <span className="vh-mono vh-kb-code">{g.code}</span> : null}
                {g.familyId ? (
                  <button
                    type="button"
                    className="vh-link"
                    title="打开产品族"
                    onClick={() => onSelect(g.familyId!)}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: 'pointer',
                      font: 'inherit',
                      color: 'inherit',
                    }}
                  >
                    {g.label}
                  </button>
                ) : (
                  <span>{g.label}</span>
                )}
                {g.subtitle ? (
                  <span className="vh-kb-list-layer-sub" style={{ marginLeft: 4 }}>
                    {g.subtitle}
                  </span>
                ) : null}
                <span className="vh-mono vh-kb-count">{g.ids.length}</span>
                {groupPrimary && (
                  <span className="vh-kb-list-cat-sort" title={groupPrimary.name}>
                    {groupPrimary.shortName}
                  </span>
                )}
              </div>
            )}
            <div className="vh-kb-list-cards flex flex-col">
              {g.ids.map((id) => {
                const entry = bundle.entries.get(id);
                if (!entry) return null;
                const primary = primaryRankingSystem(
                  bundle.rankingSystems.values(),
                  entry.category,
                );
                const primaryRank = primary
                  ? entryRankingForSystem(entry.rankings, primary.id)
                  : undefined;
                return (
                  <EntryCard
                    key={id}
                    entry={entry}
                    selected={id === selectedId}
                    favorited={isFavorite(id)}
                    rating={getRating(id)}
                    inCompare={compareIds.includes(id)}
                    showCategory={nav.kind === 'all'}
                    primaryRankLabel={
                      primary && primaryRank
                        ? `${primary.shortName} ${formatRankingPrimary(primaryRank, primary)}`
                        : undefined
                    }
                    onClick={() => onSelect(id)}
                    onToggleCompare={onToggleCompare ? () => onToggleCompare(id) : undefined}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function regionColor(region: Entry['region']): string {
  if (region === 'domestic') return 'var(--region-domestic)';
  if (region === 'overseas') return 'var(--region-overseas)';
  return 'var(--ink-3)';
}

function pricingTone(model: PricingModel): string | undefined {
  if (model === 'free' || model === 'open-source') return 'success';
  if (model === 'freemium') return 'info';
  if (model === 'usage') return 'warning';
  return undefined;
}

function EntryCard({
  entry,
  selected,
  favorited,
  rating,
  inCompare,
  showCategory,
  primaryRankLabel,
  onClick,
  onToggleCompare,
}: {
  entry: Entry;
  selected: boolean;
  favorited: boolean;
  rating: number | null;
  inCompare: boolean;
  showCategory: boolean;
  primaryRankLabel?: string;
  onClick: () => void;
  onToggleCompare?: () => void;
}) {
  const { categories } = useContent();
  const layer = layerOfCategory(entry.category, categories);

  return (
    <div
      data-selected={selected}
      className="vh-kb-entry flex items-start gap-2"
      style={{ width: '100%', fontFamily: 'var(--font-body)' }}
    >
      {onToggleCompare && (
        <button
          type="button"
          title={inCompare ? '移出对比' : '加入对比'}
          aria-label={inCompare ? '移出对比' : '加入对比'}
          onClick={(e) => {
            e.stopPropagation();
            onToggleCompare();
          }}
          className="vh-kb-entry-compare"
          style={{
            color: inCompare ? 'var(--pigment-primary)' : 'var(--ink-3)',
          }}
        >
          <Icon name="Columns" size={15} weight={inCompare ? 'fill' : 'regular'} />
        </button>
      )}
      <button
        type="button"
        onClick={onClick}
        className="vh-kb-entry-main flex items-start gap-2.5 text-left"
      >
        <div className="vh-kb-entry-icon">
          <Icon name={CATEGORY_ICONS[entry.category] ?? 'Circle'} size={18} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="flex items-center gap-2">
            <span
              title={
                entry.region === 'domestic'
                  ? '国内'
                  : entry.region === 'overseas'
                    ? '国外'
                    : '国内外'
              }
              className="vh-kb-region-dot"
              style={{ background: regionColor(entry.region) }}
            />
            <span className="vh-kb-entry-name">{entry.name}</span>
            {favorited && (
              <Icon name="Star" size={13} weight="fill" color="var(--pigment-warning)" />
            )}
          </div>
          <div className="vh-kb-entry-oneliner">{entry.oneLiner}</div>
          <div className="vh-kb-entry-meta flex flex-wrap gap-1">
            {primaryRankLabel && (
              <span className="vh-tag" data-tone="seal" title="主榜位次">
                {primaryRankLabel}
              </span>
            )}
            {entry.category === 'llm-family' && (
              <span className="vh-tag" title="产品族：导航用，不宜与档位同榜">
                产品族
              </span>
            )}
            {entry.category === 'llm-line' && (
              <span className="vh-tag" title="选型档位：默认可比">
                档位
                {entry.currentVersion ? ` · ${entry.currentVersion}` : ''}
              </span>
            )}
            {showCategory && layer && (
              <span className="vh-tag vh-kb-entry-layer-tag">{layer.label}</span>
            )}
            <span className="vh-tag" data-tone={pricingTone(entry.pricing.model)}>
              {entry.pricing.model}
            </span>
            <span className="vh-tag">{entry.maturity}</span>
            <span
              className="vh-mono vh-tag"
              data-tone={isStale(entry.lastReviewed) ? 'warning' : undefined}
              title={`复核 ${entry.lastReviewed}`}
            >
              {formatReviewedRelative(entry.lastReviewed)}
            </span>
            {rating != null && (
              <span className="vh-tag" data-tone="warning">
                ★ {rating}
              </span>
            )}
          </div>
        </div>
      </button>
    </div>
  );
}
