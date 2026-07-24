import type { Confidence, Id } from '@vh/core';
import type { Core } from 'cytoscape';
import { type ReactNode, useEffect, useMemo, useRef, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import {
  CLUSTER_NODE_THRESHOLD,
  type GraphFilter,
  buildGraphElements,
  computeForceLayout,
  createCytoscape,
  layoutKindForLens,
  mirrorPositions,
  parseCategoryClusterId,
  runBreadthfirstLayout,
  runCoseLayout,
  shouldUseCategoryClusters,
} from '../lib/cytoscape-graph.ts';
import {
  EDGE_GROUP_LABEL,
  LEGEND_SAMPLE_CATEGORIES,
  type GraphThemeMode,
  type RelationGroup,
  readDocumentTheme,
  resolveGraphPalette,
} from '../lib/graph-style.ts';
import { GRAPH_LENSES, type GraphLens, lensMeta } from '../lib/graph-views.ts';
import { relMeta } from '../lib/relations.ts';
import { useUserData } from '../lib/userdata.tsx';
import { Icon } from './Icon.tsx';

interface GraphViewProps {
  focusId: Id | null;
  onFocus: (id: Id | null) => void;
  onOpenInKnowledge: (id: Id) => void;
  /** 图上两点建边：选中 from 后再点 to */
  onCreateEdge?: (from: Id, to: Id) => void;
}

const ALL_GROUPS = Object.keys(EDGE_GROUP_LABEL) as RelationGroup[];
const ALL_CONF: Confidence[] = ['verified', 'community', 'inferred'];

export function GraphView({ focusId, onFocus, onOpenInKnowledge, onCreateEdge }: GraphViewProps) {
  const { bundle, graph } = useContent();
  const { data: userData } = useUserData();
  const [hops, setHops] = useState(2);
  const [lens, setLens] = useState<GraphLens>('ecosystem');
  const [recipeId, setRecipeId] = useState<string | null>(null);
  const [legendOpen, setLegendOpen] = useState(true);
  const [filterOpen, setFilterOpen] = useState(true);
  const [edgeGroups, setEdgeGroups] = useState<Set<RelationGroup>>(() => new Set(ALL_GROUPS));
  const [confidences, setConfidences] = useState<Set<Confidence>>(() => new Set(ALL_CONF));
  const [categories, setCategories] = useState<Set<string>>(() => new Set());
  const [cyInstance, setCyInstance] = useState<Core | null>(null);
  const [layoutBusy, setLayoutBusy] = useState(false);
  const [nodeEdgeCount, setNodeEdgeCount] = useState({ nodes: 0, edges: 0, clustered: false });
  const [clusterMode, setClusterMode] = useState<'auto' | 'on' | 'off'>('auto');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(() => new Set());
  const [linkMode, setLinkMode] = useState(false);
  const [linkFrom, setLinkFrom] = useState<Id | null>(null);
  const [themeMode, setThemeMode] = useState<GraphThemeMode>(() => readDocumentTheme());
  const hostRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const onFocusRef = useRef(onFocus);
  const onOpenRef = useRef(onOpenInKnowledge);
  const onCreateEdgeRef = useRef(onCreateEdge);
  const linkModeRef = useRef(linkMode);
  const linkFromRef = useRef(linkFrom);
  const expandCatRef = useRef((cat: string) => {
    setExpandedCategories((prev) => {
      if (prev.has(cat)) return prev;
      const next = new Set(prev);
      next.add(cat);
      return next;
    });
  });
  onFocusRef.current = onFocus;
  onOpenRef.current = onOpenInKnowledge;
  onCreateEdgeRef.current = onCreateEdge;
  linkModeRef.current = linkMode;
  linkFromRef.current = linkFrom;

  useEffect(() => {
    const root = document.documentElement;
    const sync = () => setThemeMode(readDocumentTheme());
    sync();
    const mo = new MutationObserver(sync);
    mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    return () => mo.disconnect();
  }, []);

  const palette = useMemo(() => resolveGraphPalette(themeMode), [themeMode]);

  const focusName = focusId ? (bundle.entries.get(focusId)?.name ?? focusId) : null;
  const recipes = useMemo(() => [...bundle.recipes.values()], [bundle.recipes]);
  const activeRecipeId = recipeId ?? recipes[0]?.id ?? null;
  const lensInfo = lensMeta(lens);

  const personalIds = useMemo(() => {
    const s = new Set<string>();
    for (const id of userData.favorites) s.add(id);
    for (const id of userData.follows) s.add(id);
    for (const stack of userData.myStacks) {
      for (const id of Object.values(stack.layers ?? {})) s.add(id);
    }
    return s;
  }, [userData.favorites, userData.follows, userData.myStacks]);

  const presentCategories = useMemo(() => {
    const ids = new Set<string>();
    for (const e of bundle.entries.values()) ids.add(e.category);
    return [...ids].sort();
  }, [bundle.entries]);

  const filter: GraphFilter = useMemo(() => {
    const allGroupsOn = edgeGroups.size === ALL_GROUPS.length;
    const allConfOn = confidences.size === ALL_CONF.length;
    return {
      edgeGroups: allGroupsOn ? null : edgeGroups,
      confidences: allConfOn ? null : confidences,
      categories: categories.size === 0 ? null : categories,
    };
  }, [edgeGroups, confidences, categories]);

  useEffect(() => {
    const el = hostRef.current;
    if (!el) return;
    let cancelled = false;

    cyRef.current?.destroy();
    cyRef.current = null;
    setCyInstance(null);

    const elements = buildGraphElements(bundle, graph, {
      focusId,
      hops,
      favoriteIds: new Set(userData.favorites),
      filter,
      lens,
      recipeId: activeRecipeId,
      personalIds,
      clusterMode,
      expandedCategories,
      palette,
    });
    const nCount = elements.filter(
      (e) => e.group === 'nodes' && !e.data?.isCluster && !e.data?.isCategoryCluster,
    ).length;
    const clusterCount = elements.filter(
      (e) => e.group === 'nodes' && e.data?.isCategoryCluster,
    ).length;
    const eCount = elements.filter((e) => e.group === 'edges').length;
    const clustered =
      clusterCount > 0 ||
      shouldUseCategoryClusters(clusterMode, bundle.entries.size, focusId, lens);
    setNodeEdgeCount({ nodes: nCount + clusterCount, edges: eCount, clustered });

    const host = el;
    const kind = layoutKindForLens(lens);
    const w = host.clientWidth || 800;
    const h = host.clientHeight || 600;

    async function mount() {
      setLayoutBusy(true);
      let positions = null as Awaited<ReturnType<typeof computeForceLayout>> | null;
      try {
        if (kind === 'mirror') {
          positions = mirrorPositions(elements, w, h);
        } else if (kind === 'force') {
          positions = await computeForceLayout(elements, w, h);
        }
      } catch {
        positions = null;
      }
      if (cancelled) return;

      const cy = createCytoscape(host, elements, positions, palette);
      cyRef.current = cy;
      setCyInstance(cy);
      cy.nodes().removeClass('link-source');
      if (linkFromRef.current) cy.$id(linkFromRef.current).addClass('link-source');

      cy.on('tap', 'node', (evt) => {
        const id = evt.target.id() as string;
        if (id.startsWith('vendor:')) return;
        const cat = parseCategoryClusterId(id);
        if (cat) {
          if (linkModeRef.current) return;
          expandCatRef.current(cat);
          return;
        }
        if (linkModeRef.current && onCreateEdgeRef.current) {
          const from = linkFromRef.current;
          if (!from) {
            setLinkFrom(id as Id);
            onFocusRef.current(id as Id);
            return;
          }
          if (from === id) {
            setLinkFrom(null);
            return;
          }
          onCreateEdgeRef.current(from, id as Id);
          setLinkFrom(null);
          setLinkMode(false);
          return;
        }
        onFocusRef.current(id as Id);
      });
      cy.on('dbltap', 'node', (evt) => {
        if (linkModeRef.current) return;
        const id = evt.target.id() as string;
        if (id.startsWith('vendor:') || parseCategoryClusterId(id)) return;
        onOpenRef.current(id as Id);
      });

      if (kind === 'dag') {
        runBreadthfirstLayout(cy, focusId ? [focusId] : undefined);
      } else if (kind === 'cose' && !positions) {
        runCoseLayout(cy);
      }

      requestAnimationFrame(() => {
        cy.fit(undefined, 64);
      });
      setLayoutBusy(false);
    }

    void mount();

    return () => {
      cancelled = true;
      cyRef.current?.destroy();
      cyRef.current = null;
      setCyInstance(null);
    };
  }, [
    bundle,
    graph,
    focusId,
    hops,
    userData.favorites,
    filter,
    lens,
    activeRecipeId,
    personalIds,
    clusterMode,
    expandedCategories,
    palette,
  ]);

  // 建边模式：高亮起点节点（不重建图）
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.nodes().removeClass('link-source');
    if (linkFrom) cy.$id(linkFrom).addClass('link-source');
  }, [linkFrom]);

  function fit() {
    cyRef.current?.fit(undefined, 48);
  }
  function zoomBy(factor: number) {
    const cy = cyRef.current;
    if (!cy) return;
    cy.zoom({
      level: cy.zoom() * factor,
      renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
    });
  }

  const related = focusId ? graph.related(focusId) : {};
  const relatedKeys = Object.keys(related).sort();
  const alts = focusId ? graph.alternatives(focusId) : [];
  const domestic = focusId ? graph.domesticEquivalents(focusId) : [];
  const impact = focusId ? graph.impactOf(focusId) : [];
  const conflicts = focusId
    ? (related.conflicts_with ?? []).filter((id) => bundle.entries.has(id))
    : [];

  function toggleGroup(g: RelationGroup) {
    setEdgeGroups((prev) => {
      const next = new Set(prev);
      if (next.has(g)) {
        if (next.size > 1) next.delete(g);
      } else next.add(g);
      return next;
    });
  }
  function toggleConf(c: Confidence) {
    setConfidences((prev) => {
      const next = new Set(prev);
      if (next.has(c)) {
        if (next.size > 1) next.delete(c);
      } else next.add(c);
      return next;
    });
  }
  function toggleCat(id: string) {
    setCategories((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="flex" style={{ height: '100%', minHeight: 0 }}>
      <aside
        className="vh-column flex flex-col gap-3 overflow-y-auto"
        style={{
          width: 280,
          flexShrink: 0,
          padding: 14,
        }}
      >
        <div>
          <div
            className="vh-text-caption"
            style={{ letterSpacing: '0.12em', color: 'var(--pigment-seal)', marginBottom: 4 }}
          >
            舆图
          </div>
          <div className="vh-text-h3" style={{ color: 'var(--ink-1)', margin: 0 }}>
            知识图谱
          </div>
        </div>
        <div>
          {focusName ? (
            <div className="flex items-start gap-2" style={{ alignItems: 'flex-start' }}>
              <div className="vh-text-caption" style={{ flex: 1, minWidth: 0 }}>
                焦点：
                <strong style={{ color: 'var(--ink-1)', wordBreak: 'break-word' }}>{focusName}</strong>
              </div>
              <button
                type="button"
                className="vh-btn"
                onClick={() => onFocus(null)}
                title="清除焦点，显示全图"
                aria-label="清除焦点"
                style={{
                  flexShrink: 0,
                  padding: '2px 8px',
                  fontSize: 11,
                  lineHeight: 1.4,
                }}
              >
                <Icon name="X" size={12} /> 清除
              </button>
            </div>
          ) : (
            <div className="vh-text-caption">未设焦点 · 显示全图</div>
          )}
        </div>

        <div>
          <div className="vh-text-caption" style={{ marginBottom: 6 }}>
            视图
          </div>
          <div className="flex flex-wrap gap-1">
            {GRAPH_LENSES.map((l) => {
              const on = lens === l.id;
              return (
                <button
                  key={l.id}
                  type="button"
                  className="vh-chip"
                  title={l.hint}
                  onClick={() => setLens(l.id)}
                  data-on={on ? 'true' : 'false'}
                >
                  {l.label}
                </button>
              );
            })}
          </div>
          <div className="vh-text-caption" style={{ color: 'var(--ink-3)', marginTop: 6 }}>
            {lensInfo.hint}
          </div>
          {lensInfo.needsFocus && !focusId && (
            <div
              className="vh-text-caption"
              style={{ color: 'var(--pigment-warning)', marginTop: 4 }}
            >
              建议先设焦点以查看替代簇
            </div>
          )}
          {lens === 'recipe' && recipes.length > 0 && (
            <select
              className="vh-input"
              value={activeRecipeId ?? ''}
              onChange={(e) => setRecipeId(e.target.value || null)}
              style={{
                marginTop: 8,
                width: '100%',
                boxSizing: 'border-box',
              }}
            >
              {recipes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          )}
          <div className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)', marginTop: 6 }}>
            {nodeEdgeCount.nodes} 节点 · {nodeEdgeCount.edges} 边
            {nodeEdgeCount.clustered ? ' · 分类聚类' : ''}
            {layoutBusy ? ' · 布局中…' : ''}
          </div>
        </div>

        {onCreateEdge && (
          <div>
            <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 6 }}>图上建边</div>
            <button
              type="button"
              className="vh-btn"
              onClick={() => {
                setLinkMode((m) => !m);
                setLinkFrom(null);
              }}
              style={{
                width: '100%',
                fontSize: 12,
                background: linkMode ? 'var(--pigment-primary)' : undefined,
                color: linkMode ? 'var(--paper-0)' : undefined,
                borderColor: linkMode ? 'var(--pigment-primary)' : undefined,
              }}
            >
              <Icon name="GitBranch" size={14} />{' '}
              {linkMode ? '建边中…（再点取消）' : '开启建边模式'}
            </button>
            <div style={{ fontSize: 11, color: 'var(--ink-3)', marginTop: 6 }}>
              {linkMode
                ? linkFrom
                  ? `已选起点「${bundle.entries.get(linkFrom)?.name ?? linkFrom}」· 再点终点`
                  : '先点起点，再点终点 → 打开边编辑器'
                : '两点连线创建关系，保存至本机覆盖层'}
            </div>
            {linkMode && linkFrom && (
              <button
                type="button"
                className="vh-btn"
                style={{ marginTop: 6, fontSize: 11, width: '100%' }}
                onClick={() => setLinkFrom(null)}
              >
                清除起点
              </button>
            )}
          </div>
        )}

        {lens === 'ecosystem' && (
          <div>
            <div className="vh-text-caption" style={{ marginBottom: 6 }}>
              大图聚类
            </div>
            <div className="flex gap-1" style={{ marginBottom: 6 }}>
              {(
                [
                  ['auto', `自动(≥${CLUSTER_NODE_THRESHOLD})`],
                  ['on', '开'],
                  ['off', '关'],
                ] as const
              ).map(([mode, label]) => {
                const on = clusterMode === mode;
                return (
                  <button
                    key={mode}
                    type="button"
                    className="vh-chip"
                    onClick={() => setClusterMode(mode)}
                    data-on={on ? 'true' : 'false'}
                    style={{ flex: 1, textAlign: 'center' }}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
            <div className="vh-text-caption" style={{ color: 'var(--ink-3)', marginBottom: 6 }}>
              单击分类簇展开；设焦点则改邻域裁剪（懒渲染）
            </div>
            {expandedCategories.size > 0 && (
              <button
                type="button"
                className="vh-btn"
                style={{ fontSize: 11, width: '100%' }}
                onClick={() => setExpandedCategories(new Set())}
              >
                折叠已展开分类（{expandedCategories.size}）
              </button>
            )}
          </div>
        )}

        <div style={{ fontSize: 13, color: 'var(--ink-2)' }}>
          <div style={{ marginBottom: 6 }}>邻域跳数</div>
          <div className="flex gap-1">
            {[1, 2, 3].map((h) => (
              <button
                key={h}
                type="button"
                className="vh-btn"
                onClick={() => setHops(h)}
                disabled={lens === 'recipe' || lens === 'personal'}
                style={{
                  flex: 1,
                  background: hops === h ? 'var(--pigment-primary)' : undefined,
                  color: hops === h ? 'var(--paper-0)' : undefined,
                  borderColor: hops === h ? 'var(--pigment-primary)' : undefined,
                }}
              >
                {h}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-1">
          <button type="button" className="vh-btn" onClick={fit} title="适应窗口">
            <Icon name="ArrowsOut" size={14} />
          </button>
          <button type="button" className="vh-btn" onClick={() => zoomBy(1.2)} title="放大">
            <Icon name="MagnifyingGlassPlus" size={14} />
          </button>
          <button type="button" className="vh-btn" onClick={() => zoomBy(1 / 1.2)} title="缩小">
            <Icon name="MagnifyingGlassMinus" size={14} />
          </button>
          {focusId && (
            <button
              type="button"
              className="vh-btn"
              onClick={() => onOpenInKnowledge(focusId)}
              title="在知识库打开"
            >
              <Icon name="ArrowSquareOut" size={14} />
            </button>
          )}
          <button
            type="button"
            className="vh-btn"
            onClick={() => onFocus(null)}
            title="清除焦点，显示全图"
            disabled={!focusId}
            aria-label="清除焦点"
          >
            <Icon name="Graph" size={14} /> 清除焦点
          </button>
        </div>

        <Collapsible title="过滤" open={filterOpen} onToggle={() => setFilterOpen((o) => !o)}>
          <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 6 }}>关系分组</div>
          <div className="flex flex-wrap gap-1" style={{ marginBottom: 10 }}>
            {ALL_GROUPS.map((g) => {
              const on = edgeGroups.has(g);
              return (
                <button
                  key={g}
                  type="button"
                  className="vh-btn"
                  onClick={() => toggleGroup(g)}
                  style={{
                    padding: '2px 8px',
                    fontSize: 12,
                    borderColor: on ? palette.edgeGroup[g] : undefined,
                    color: on ? palette.edgeGroup[g] : undefined,
                  }}
                >
                  {EDGE_GROUP_LABEL[g]}
                </button>
              );
            })}
          </div>
          <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 6 }}>可信度</div>
          <div className="flex flex-wrap gap-1" style={{ marginBottom: 10 }}>
            {ALL_CONF.map((c) => {
              const on = confidences.has(c);
              return (
                <button
                  key={c}
                  type="button"
                  className="vh-btn"
                  onClick={() => toggleConf(c)}
                  style={{
                    padding: '2px 8px',
                    fontSize: 12,
                    borderColor: on ? 'var(--pigment-primary)' : undefined,
                    color: on ? 'var(--pigment-primary)' : undefined,
                  }}
                >
                  {c}
                </button>
              );
            })}
          </div>
          <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 6 }}>
            分类（空=全部）
          </div>
          <div className="flex flex-wrap gap-1">
            {presentCategories.map((c) => {
              const on = categories.has(c);
              const name = bundle.categories.find((x) => x.id === c)?.name ?? c;
              return (
                <button
                  key={c}
                  type="button"
                  className="vh-btn"
                  onClick={() => toggleCat(c)}
                  title={c}
                  style={{
                    padding: '2px 8px',
                    fontSize: 11,
                    borderColor: on ? 'var(--pigment-primary)' : undefined,
                    color: on ? 'var(--pigment-primary)' : undefined,
                  }}
                >
                  {name}
                </button>
              );
            })}
          </div>
          {categories.size > 0 && (
            <button
              type="button"
              className="vh-btn"
              style={{ marginTop: 8, fontSize: 12 }}
              onClick={() => setCategories(new Set())}
            >
              清除分类过滤
            </button>
          )}
        </Collapsible>

        {focusId && (
          <div>
            <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 8 }}>
              图应用（G4–G6）
            </div>
            <ToolBlock
              title="冲突（G4）"
              empty="无 conflicts_with"
              ids={conflicts}
              resolve={(id) => bundle.entries.get(id)?.name ?? id}
              onPick={onFocus}
              warn
            />
            <ToolBlock
              title="平替（G5）"
              empty="无 alternative / 开源平替"
              ids={alts}
              resolve={(id) => bundle.entries.get(id)?.name ?? id}
              onPick={onFocus}
            />
            <ToolBlock
              title="国内对标（G5）"
              empty="无 domestic_equivalent"
              ids={domestic}
              resolve={(id) => bundle.entries.get(id)?.name ?? id}
              onPick={onFocus}
            />
            <ToolBlock
              title="影响面（G6）"
              empty="无下游依赖/托管关系"
              ids={impact.filter((id) => bundle.entries.has(id))}
              resolve={(id) => bundle.entries.get(id)?.name ?? id}
              onPick={onFocus}
            />
          </div>
        )}

        {focusId && relatedKeys.length > 0 && (
          <div>
            <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 8 }}>焦点关联</div>
            <div className="flex flex-col gap-2">
              {relatedKeys.slice(0, 8).map((key) => (
                <div key={key}>
                  <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 4 }}>
                    {relMeta(key).label}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {(related[key] ?? []).slice(0, 6).map((tid) => {
                      const name = bundle.entries.get(tid)?.name ?? tid;
                      const clickable = bundle.entries.has(tid);
                      return (
                        <button
                          key={tid}
                          type="button"
                          className="vh-tag"
                          disabled={!clickable}
                          onClick={() => clickable && onFocus(tid)}
                          style={{
                            cursor: clickable ? 'pointer' : 'default',
                            color: clickable ? 'var(--pigment-primary)' : undefined,
                          }}
                        >
                          {name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <Collapsible title="图例" open={legendOpen} onToggle={() => setLegendOpen((o) => !o)}>
          <div className="flex flex-col gap-3" style={{ fontSize: 12, color: 'var(--ink-2)' }}>
            <div>
              <div style={{ marginBottom: 6, color: 'var(--ink-3)' }}>节点大小</div>
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5">
                  <span
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: 999,
                      background: palette.fallbackFill,
                      border: `1.5px solid ${palette.region.both}`,
                    }}
                  />
                  少连接
                </span>
                <span className="flex items-center gap-1.5">
                  <span
                    style={{
                      width: 16,
                      height: 16,
                      borderRadius: 999,
                      background: palette.fallbackFill,
                      border: `2px solid ${palette.focus}`,
                      boxShadow: `0 0 0 3px ${palette.focus}33`,
                    }}
                  />
                  焦点 / 多连接
                </span>
              </div>
            </div>

            <div>
              <div style={{ marginBottom: 6, color: 'var(--ink-3)' }}>分类色（七卷示意）</div>
              <div className="flex flex-wrap gap-x-3 gap-y-1.5">
                {LEGEND_SAMPLE_CATEGORIES.map((c) => (
                  <span key={c.id} className="flex items-center gap-1.5">
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 999,
                        background: palette.categoryFill(c.id),
                      }}
                    />
                    {c.label}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div style={{ marginBottom: 6, color: 'var(--ink-3)' }}>地区描边</div>
              <div className="flex flex-wrap gap-x-3 gap-y-1.5">
                <span className="flex items-center gap-1.5">
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 999,
                      border: `2px solid ${palette.region.domestic}`,
                    }}
                  />
                  国内
                </span>
                <span className="flex items-center gap-1.5">
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 999,
                      border: `2px solid ${palette.region.overseas}`,
                    }}
                  />
                  国外
                </span>
                <span className="flex items-center gap-1.5">
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 999,
                      border: `2px dashed ${palette.region.both}`,
                    }}
                  />
                  双栖
                </span>
              </div>
            </div>

            <div>
              <div style={{ marginBottom: 6, color: 'var(--ink-3)' }}>成熟度（深浅）</div>
              <div className="flex items-center gap-2">
                {(
                  [
                    ['experimental', '实验'],
                    ['beta', 'Beta'],
                    ['stable', '稳定'],
                    ['mature', '成熟'],
                  ] as const
                ).map(([key, label]) => (
                  <span key={key} className="flex items-center gap-1">
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 999,
                        background: palette.categoryFill('framework'),
                        opacity: palette.maturityAlpha[key],
                      }}
                    />
                    {label}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div style={{ marginBottom: 6, color: 'var(--ink-3)' }}>关系分组</div>
              <div className="flex flex-col gap-1.5">
                {(Object.keys(EDGE_GROUP_LABEL) as RelationGroup[]).map((g) => (
                  <div key={g} className="flex items-center gap-2">
                    <span
                      style={{
                        width: 24,
                        height: 3,
                        background: palette.edgeGroup[g],
                        borderRadius: 2,
                        opacity: palette.edgeOpacity + 0.2,
                      }}
                    />
                    {EDGE_GROUP_LABEL[g]}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div style={{ marginBottom: 6, color: 'var(--ink-3)' }}>可信度</div>
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center gap-2">
                  <span style={{ width: 24, borderTop: '2px solid var(--ink-2)' }} />
                  实线 · verified
                </div>
                <div className="flex items-center gap-2">
                  <span style={{ width: 24, borderTop: '2px dashed var(--ink-2)' }} />
                  虚线 · community
                </div>
                <div className="flex items-center gap-2">
                  <span style={{ width: 24, borderTop: '2px dotted var(--ink-2)' }} />
                  点线 · inferred
                </div>
              </div>
            </div>
          </div>
        </Collapsible>

        <div style={{ fontSize: 12, color: 'var(--ink-3)' }}>
          {linkMode ? '建边模式：点起点 → 点终点' : '单击设焦点 · 双击打开详情 · 滚轮缩放'}
          {lens === 'ecosystem' && !linkMode ? ' · 单击分类簇展开' : ''}
        </div>
      </aside>

      <div className="vh-graph-host" style={{ flex: 1, minWidth: 0, position: 'relative' }}>
        <div ref={hostRef} style={{ position: 'absolute', inset: 0 }} />
        {nodeEdgeCount.nodes === 0 && (
          <div
            className="vh-text-sm"
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--ink-3)',
              pointerEvents: 'none',
              zIndex: 2,
            }}
          >
            当前视图无节点
            {lens === 'learning' ? '（种子尚无 prerequisite_of 边）' : ''}
            {lens === 'personal' && personalIds.size === 0 ? ' · 先收藏/关注或保存技术栈' : ''}
          </div>
        )}
        <GraphMiniMap cy={cyInstance} />
      </div>
    </div>
  );
}

function Collapsible({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: ReactNode;
}) {
  return (
    <div>
      <button
        type="button"
        onClick={onToggle}
        className="flex items-center gap-1"
        style={{
          border: 'none',
          background: 'transparent',
          color: 'var(--ink-2)',
          cursor: 'pointer',
          fontSize: 13,
          padding: 0,
        }}
      >
        <Icon name={open ? 'CaretDown' : 'CaretRight'} size={12} />
        {title}
      </button>
      {open && <div style={{ marginTop: 8 }}>{children}</div>}
    </div>
  );
}

function ToolBlock({
  title,
  empty,
  ids,
  resolve,
  onPick,
  warn,
}: {
  title: string;
  empty: string;
  ids: Id[];
  resolve: (id: Id) => string;
  onPick: (id: Id) => void;
  warn?: boolean;
}) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div
        style={{
          fontSize: 12,
          color: warn && ids.length ? 'var(--pigment-warning)' : 'var(--ink-3)',
          marginBottom: 4,
        }}
      >
        {title}
      </div>
      {ids.length === 0 ? (
        <div style={{ fontSize: 12, color: 'var(--ink-3)' }}>{empty}</div>
      ) : (
        <div className="flex flex-wrap gap-1">
          {ids.slice(0, 12).map((id) => (
            <button
              key={id}
              type="button"
              className="vh-tag"
              onClick={() => onPick(id)}
              style={{
                cursor: 'pointer',
                color: warn ? 'var(--pigment-danger)' : 'var(--pigment-primary)',
              }}
            >
              {resolve(id)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/** SVG 迷你地图：节点散点 + 当前视口矩形（只读概览）。 */
function GraphMiniMap({ cy }: { cy: Core | null }) {
  const [, setTick] = useState(0);

  useEffect(() => {
    if (!cy) return;
    const bump = () => setTick((t) => t + 1);
    cy.on('pan zoom position layoutstop', bump);
    bump();
    return () => {
      cy.off('pan zoom position layoutstop', bump);
    };
  }, [cy]);

  if (!cy || cy.nodes().length === 0) return null;

  const bb = cy.elements().boundingBox();
  const pad = 20;
  const w = 140;
  const h = 100;
  const spanX = Math.max(bb.w, 1) + pad * 2;
  const spanY = Math.max(bb.h, 1) + pad * 2;
  const ox = bb.x1 - pad;
  const oy = bb.y1 - pad;
  const sx = w / spanX;
  const sy = h / spanY;

  const ext = cy.extent();
  const vx = (ext.x1 - ox) * sx;
  const vy = (ext.y1 - oy) * sy;
  const vw = (ext.x2 - ext.x1) * sx;
  const vh = (ext.y2 - ext.y1) * sy;

  return (
    <div
      style={{
        position: 'absolute',
        right: 12,
        bottom: 12,
        width: w,
        height: h,
        background: 'color-mix(in oklch, var(--paper-1) 92%, transparent)',
        border: '1px solid var(--line)',
        borderRadius: 6,
        overflow: 'hidden',
        boxShadow: 'var(--shadow-sm)',
        zIndex: 5,
        pointerEvents: 'none',
        backdropFilter: 'blur(0px)',
      }}
    >
      <svg width={w} height={h} role="img" aria-label="图谱迷你地图">
        <title>图谱迷你地图</title>
        <rect width={w} height={h} fill="var(--paper-0)" opacity={0.35} />
        {cy.nodes().map((n) => {
          const p = n.position();
          const id = n.id();
          const isFocus = n.data('isFocus');
          if (n.data('isCluster')) return null;
          const isCat = n.data('isCategoryCluster');
          return (
            <circle
              key={id}
              cx={(p.x - ox) * sx}
              cy={(p.y - oy) * sy}
              r={isFocus ? 3.5 : isCat ? 3 : 2.2}
              fill={isFocus ? 'var(--pigment-primary)' : isCat ? 'var(--ink-2)' : 'var(--ink-3)'}
            />
          );
        })}
        <rect
          x={vx}
          y={vy}
          width={Math.max(vw, 8)}
          height={Math.max(vh, 8)}
          fill="none"
          stroke="var(--pigment-primary)"
          strokeWidth={1.5}
          opacity={0.7}
        />
      </svg>
    </div>
  );
}
