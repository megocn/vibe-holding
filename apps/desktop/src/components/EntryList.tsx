import type { Entry, Id, PricingModel, RankingSystem } from '@vh/core';
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
import {
  memo,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type MouseEvent,
} from 'react';
import { useContent } from '../lib/content.tsx';
import { formatReviewedRelative, isStale } from '../lib/intel.ts';
import { buildLlmFamilyTree, isLlmSectionNav } from '../lib/llm-tree.ts';
import { useUserData } from '../lib/userdata.tsx';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';
import type { KbNav } from './Sidebar.tsx';

/** 首屏挂载条目数：避免「全部」下一次挂 ~1200 卡导致切知识库卡顿 */
const INITIAL_VISIBLE = 72;
/** 滚动触底 / 空闲续载每批条数 */
const BATCH_VISIBLE = 96;

interface EntryListProps {
  ids: Id[];
  selectedId: Id | null;
  onSelect: (id: Id) => void;
  compareIds?: Id[];
  onToggleCompare?: (id: Id) => void;
  /** 当前导航；「全部」时按卷分组列表 */
  nav?: KbNav;
  /** 与叶图落点双向 hover 高亮 */
  hoverId?: Id | null;
  onHover?: (id: Id | null) => void;
}

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

export function EntryList({
  ids,
  selectedId,
  onSelect,
  compareIds = [],
  onToggleCompare,
  nav = { kind: 'all' },
  hoverId = null,
  onHover,
}: EntryListProps) {
  const { bundle, categories } = useContent();
  const { isFavorite, getRating } = useUserData();
  const catName = useMemo(() => new Map(categories.map((c) => [c.id, c])), [categories]);
  const rankingSystems = useMemo(
    () => [...bundle.rankingSystems.values()],
    [bundle.rankingSystems],
  );
  /** 叶类 → 主榜；列表行与组头复用，避免每行再扫一遍 systems */
  const primaryByCategory = useMemo(() => {
    const map = new Map<string, RankingSystem | undefined>();
    const ensure = (cat: string) => {
      if (!map.has(cat)) map.set(cat, primaryRankingSystem(rankingSystems, cat));
      return map.get(cat);
    };
    for (const id of ids) {
      const e = bundle.entries.get(id);
      if (e) ensure(e.category);
    }
    ensure('llm-line');
    return map;
  }, [ids, bundle.entries, rankingSystems]);

  const layerLabelByCategory = useMemo(() => {
    if (nav.kind !== 'all') return null as Map<string, string> | null;
    const m = new Map<string, string>();
    for (const c of categories) {
      const layer = layerOfCategory(c.id, categories);
      if (layer) m.set(c.id, layer.label);
    }
    return m;
  }, [nav.kind, categories]);

  const compareSet = useMemo(() => new Set(compareIds), [compareIds]);

  // 从叶图 hover 过来时，把对应中栏行滚进视口
  useEffect(() => {
    if (!hoverId || !onHover) return;
    const el = document.querySelector<HTMLElement>(
      `.vh-kb-list [data-entry-id="${CSS.escape(hoverId)}"]`,
    );
    el?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [hoverId, onHover]);

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
        rankingSystems,
        { prominenceOf: (id) => prominence.get(id) },
      ),
    [bundle.entries, rankingSystems, prominence],
  );

  const primaryLabel = useMemo(() => {
    if (nav.kind === 'family') return '按榜单综合分排序（旗舰聚合）';
    if (nav.kind !== 'category') return null;
    if (isLlmSectionNav(nav.categoryId, categories)) return '按榜单综合分排序（旗舰聚合）';
    const sys = primaryRankingSystem(rankingSystems, nav.categoryId);
    const catEntries = [...bundle.entries.values()].filter((e) => e.category === nav.categoryId);
    // 仅当类内确有主榜快照时宣称「按权威榜」；否则诚实标流行度兜底
    const hasPrimarySnap =
      !!sys && catEntries.some((e) => entryRankingForSystem(e.rankings, sys.id) != null);
    if (hasPrimarySnap && sys) return `按 ${sys.shortName} 排序`;
    const hasSignal = catEntries.some((e) => prominence.has(e.id));
    return hasSignal ? '按流行度排序（GitHub/域名等外部信号）' : null;
  }, [nav, rankingSystems, bundle.entries, categories, prominence]);

  const groups = useMemo((): ListGroup[] => {
    const entrySection = (entryCategory: Id) => sectionIdOf(categories, entryCategory);
    const idSet = new Set(ids);

    const llmTreeGroups = (familyFilter?: Id): ListGroup[] => {
      const tree = buildLlmFamilyTree(bundle);
      const out: ListGroup[] = [];
      for (const n of tree) {
        if (familyFilter && n.familyId !== familyFilter) continue;
        const scope = [n.familyId, ...n.lineIds].filter((id) => idSet.has(id));
        // 列表里族头单独展示，ids 只放档位（上下层更清晰）
        const lineOnly = n.lineIds.filter((id) => idSet.has(id));
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
      const layerIdSet = new Set(layerIds);
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
              const lineOnly = n.lineIds.filter((id) => layerIdSet.has(id));
              if (lineOnly.length === 0 && !layerIdSet.has(n.familyId)) continue;
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

  const totalEntries = useMemo(
    () => groups.reduce((n, g) => n + (g.isLayer ? 0 : g.ids.length), 0),
    [groups],
  );

  /** 当前应挂载的条目上限（按 groups 顺序计数） */
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE);
  const listRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // 导航 / 筛选变更时重置窗口
  useEffect(() => {
    setVisibleCount(INITIAL_VISIBLE);
  }, [ids, nav.kind, nav]);

  // 选中或 hover 的条目须在窗口内，否则滚不动 / 高亮丢失
  useEffect(() => {
    const need = selectedId ?? hoverId;
    if (!need) return;
    let idx = 0;
    for (const g of groups) {
      if (g.isLayer) continue;
      for (const id of g.ids) {
        if (id === need) {
          setVisibleCount((v) => Math.max(v, idx + 1 + 8));
          return;
        }
        idx += 1;
      }
    }
  }, [selectedId, hoverId, groups]);

  const hasMore = visibleCount < totalEntries;

  const grow = useCallback(() => {
    setVisibleCount((v) => Math.min(totalEntries, v + BATCH_VISIBLE));
  }, [totalEntries]);

  // 触底续载
  useEffect(() => {
    if (!hasMore) return;
    const root = listRef.current;
    const target = sentinelRef.current;
    if (!root || !target) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) grow();
      },
      { root, rootMargin: '240px 0px', threshold: 0 },
    );
    io.observe(target);
    return () => io.disconnect();
  }, [hasMore, grow, visibleCount]);

  // 首屏落地后只再预取一批，其余随滚动触底；避免空闲连灌整库
  useEffect(() => {
    if (visibleCount !== INITIAL_VISIBLE || totalEntries <= INITIAL_VISIBLE) return;
    let cancelled = false;
    const schedule =
      typeof requestIdleCallback === 'function'
        ? (cb: () => void) => {
            const id = requestIdleCallback(cb, { timeout: 500 });
            return () => cancelIdleCallback(id);
          }
        : (cb: () => void) => {
            const id = window.setTimeout(cb, 100);
            return () => clearTimeout(id);
          };
    const cancel = schedule(() => {
      if (!cancelled) grow();
    });
    return () => {
      cancelled = true;
      cancel();
    };
  }, [visibleCount, totalEntries, grow, ids, nav]);

  /** 按 visibleCount 裁切后的纯数据（避免在 map 里改 budget） */
  const windowedGroups = useMemo(() => {
    let budget = visibleCount;
    const out: Array<ListGroup & { visibleIds: Id[] }> = [];
    for (const g of groups) {
      if (g.isLayer) {
        if (budget <= 0) break;
        out.push({ ...g, visibleIds: [] });
        continue;
      }
      if (budget <= 0) break;
      const take = Math.min(g.ids.length, budget);
      if (take === 0) continue;
      budget -= take;
      out.push({
        ...g,
        visibleIds: take < g.ids.length ? g.ids.slice(0, take) : g.ids,
      });
    }
    return out;
  }, [groups, visibleCount]);

  if (ids.length === 0) {
    return (
      <EmptyState
        title="无匹配条目"
        hint="调整筛选或搜索词，换一条航路再探。"
        icon="MagnifyingGlass"
      />
    );
  }

  const showCompare = Boolean(onToggleCompare);

  return (
    <div ref={listRef} className="vh-kb-list flex flex-col overflow-y-auto">
      {primaryLabel && <div className="vh-kb-list-sort-hint vh-text-caption">{primaryLabel}</div>}
      {windowedGroups.map((g) => {
        if (g.isLayer) {
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
        const groupPrimary = rankingLeaf ? primaryByCategory.get(rankingLeaf) : undefined;

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
              {g.visibleIds.map((id) => {
                const entry = bundle.entries.get(id);
                if (!entry) return null;
                const primary = primaryByCategory.get(entry.category);
                const primaryRank = primary
                  ? entryRankingForSystem(entry.rankings, primary.id)
                  : undefined;
                return (
                  <EntryCard
                    key={id}
                    entry={entry}
                    selected={id === selectedId}
                    hoverSync={id === hoverId}
                    favorited={isFavorite(id)}
                    rating={getRating(id)}
                    inCompare={compareSet.has(id)}
                    showCompare={showCompare}
                    layerLabel={layerLabelByCategory?.get(entry.category)}
                    primaryRankLabel={
                      primary && primaryRank
                        ? `${primary.shortName} ${formatRankingPrimary(primaryRank, primary)}`
                        : undefined
                    }
                    onSelect={onSelect}
                    onHoverChange={onHover}
                    onToggleCompare={onToggleCompare}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
      {hasMore && (
        <div ref={sentinelRef} className="vh-kb-list-more" aria-hidden>
          <span className="vh-text-caption" style={{ color: 'var(--ink-3)' }}>
            续载中…
          </span>
        </div>
      )}
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

const EntryCard = memo(function EntryCard({
  entry,
  selected,
  hoverSync,
  favorited,
  rating,
  inCompare,
  showCompare,
  layerLabel,
  primaryRankLabel,
  onSelect,
  onHoverChange,
  onToggleCompare,
}: {
  entry: Entry;
  selected: boolean;
  hoverSync: boolean;
  favorited: boolean;
  rating: number | null;
  inCompare: boolean;
  showCompare: boolean;
  layerLabel?: string;
  primaryRankLabel?: string;
  onSelect: (id: Id) => void;
  onHoverChange?: (id: Id | null) => void;
  onToggleCompare?: (id: Id) => void;
}) {
  const onMainClick = useCallback(() => onSelect(entry.id), [onSelect, entry.id]);
  const onCompareClick = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      onToggleCompare?.(entry.id);
    },
    [onToggleCompare, entry.id],
  );

  return (
    <div
      data-selected={selected}
      data-hover-sync={hoverSync ? 'true' : undefined}
      data-entry-id={entry.id}
      className="vh-kb-entry flex items-start gap-2"
      style={{ width: '100%', fontFamily: 'var(--font-body)' }}
      onMouseEnter={() => onHoverChange?.(entry.id)}
      onMouseLeave={() => onHoverChange?.(null)}
    >
      {showCompare && onToggleCompare && (
        <button
          type="button"
          title={inCompare ? '移出对比' : '加入对比'}
          aria-label={inCompare ? '移出对比' : '加入对比'}
          onClick={onCompareClick}
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
        onClick={onMainClick}
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
            {layerLabel && <span className="vh-tag vh-kb-entry-layer-tag">{layerLabel}</span>}
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
});
