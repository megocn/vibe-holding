import type { Confidence, ContentBundle, Edge, GraphEngine, Id, StackRecipe } from '@vh/core';
import { isSymmetric } from '@vh/core';
import type { Core, ElementDefinition } from 'cytoscape';
import cytoscape from 'cytoscape';
import {
  type GraphPalette,
  type RelationGroup,
  CATEGORY_HUE,
  confidenceLineStyle,
  cyOklch,
  nodeVisualSize,
  relationGroup,
  resolveGraphPalette,
  vendorFill,
} from './graph-style.ts';
import { type GraphLens, LENS_EDGE_TYPES, lensMeta } from './graph-views.ts';
import type { LayoutPositions, LayoutRequest } from './layout.worker.ts';

export interface GraphFilter {
  /** 空 = 全部分组 */
  edgeGroups: Set<RelationGroup> | null;
  /** 空 = 全部可信度 */
  confidences: Set<Confidence> | null;
  /** 空 = 全部分类 */
  categories: Set<string> | null;
}

export interface GraphElementsOpts {
  focusId: Id | null;
  hops: number;
  favoriteIds?: Set<string>;
  filter?: GraphFilter;
  lens?: GraphLens;
  recipeId?: string | null;
  /** 个人视图：收藏 ∪ 关注 ∪ 技术栈层 */
  personalIds?: Set<string>;
  /**
   * 大图聚类：`auto` = 无焦点且节点数 ≥ 阈值时按分类折叠；
   * `on` 强制；`off` 关闭。展开的分类见 expandedCategories。
   */
  clusterMode?: 'auto' | 'on' | 'off';
  expandedCategories?: Set<string>;
  /** 主题色板；缺省读 document */
  palette?: GraphPalette;
}

/** 超过此节点数时 auto 模式启用分类聚类 */
export const CLUSTER_NODE_THRESHOLD = 24;

/** 无向邻接上的跳数（焦点=0）；无焦点时返回空 Map */
function hopDistances(focusId: Id | null, edges: Edge[], nodeIds: Id[]): Map<string, number> {
  const dist = new Map<string, number>();
  if (!focusId) return dist;
  const adj = new Map<string, string[]>();
  for (const id of nodeIds) adj.set(id, []);
  for (const e of edges) {
    if (!adj.has(e.from) || !adj.has(e.to)) continue;
    adj.get(e.from)!.push(e.to);
    adj.get(e.to)!.push(e.from);
  }
  const q: string[] = [focusId];
  dist.set(focusId, 0);
  while (q.length) {
    const cur = q.shift()!;
    const d = dist.get(cur)!;
    for (const n of adj.get(cur) ?? []) {
      if (dist.has(n)) continue;
      dist.set(n, d + 1);
      q.push(n);
    }
  }
  return dist;
}

export function categoryClusterId(categoryId: string): string {
  return `cat:${categoryId}`;
}

export function parseCategoryClusterId(id: string): string | null {
  return id.startsWith('cat:') ? id.slice(4) : null;
}

export function shouldUseCategoryClusters(
  mode: 'auto' | 'on' | 'off' | undefined,
  nodeCount: number,
  focusId: Id | null,
  lens: GraphLens,
): boolean {
  if (mode === 'off') return false;
  if (mode === 'on') return true;
  // auto：仅生态全景、无焦点、节点够多时折叠（有焦点已是邻域裁剪）
  if (focusId) return false;
  if (lens !== 'ecosystem') return false;
  return nodeCount >= CLUSTER_NODE_THRESHOLD;
}

function passFilter(
  e: Edge,
  entryCategory: (id: Id) => string | undefined,
  f?: GraphFilter,
): boolean {
  if (!f) return true;
  if (f.edgeGroups && f.edgeGroups.size > 0 && !f.edgeGroups.has(relationGroup(e.type))) {
    return false;
  }
  if (f.confidences && f.confidences.size > 0 && !f.confidences.has(e.confidence)) {
    return false;
  }
  if (f.categories && f.categories.size > 0) {
    const ca = entryCategory(e.from);
    const cb = entryCategory(e.to);
    if ((!ca || !f.categories.has(ca)) && (!cb || !f.categories.has(cb))) return false;
  }
  return true;
}

function collectRecipeIds(recipe: StackRecipe | undefined): Set<Id> {
  const s = new Set<Id>();
  if (!recipe) return s;
  for (const id of Object.values(recipe.layers)) s.add(id);
  return s;
}

/** 按分类折叠：未展开分类 → 簇节点；跨类边聚合。 */
function buildCategoryClusterElements(
  bundle: ContentBundle,
  nodes: Id[],
  edges: Edge[],
  opts: { favoriteIds?: Set<string>; expanded: Set<string>; palette: GraphPalette },
): ElementDefinition[] {
  const { palette } = opts;
  const byCat = new Map<string, Id[]>();
  for (const id of nodes) {
    const entry = bundle.entries.get(id);
    if (!entry) continue;
    const list = byCat.get(entry.category) ?? [];
    list.push(id);
    byCat.set(entry.category, list);
  }

  const expanded = opts.expanded;
  const endpointOf = (id: Id): string | null => {
    const entry = bundle.entries.get(id);
    if (!entry) return null;
    if (expanded.has(entry.category)) return id;
    return categoryClusterId(entry.category);
  };

  const elements: ElementDefinition[] = [];

  for (const [cat, ids] of byCat) {
    const catMeta = bundle.categories.find((c) => c.id === cat);
    const label = catMeta?.name ?? cat;
    if (expanded.has(cat)) {
      for (const id of ids) {
        const entry = bundle.entries.get(id);
        if (!entry) continue;
        elements.push({
          group: 'nodes',
          data: {
            id,
            label: entry.name,
            category: entry.category,
            region: entry.region,
            maturity: entry.maturity,
            size: 40,
            fill: palette.categoryFill(entry.category),
            alpha: palette.maturityAlpha[entry.maturity] ?? 0.75,
            stroke: palette.region[entry.region] ?? palette.region.both,
            hop: 0,
            showLabel: true,
            isFocus: false,
            isFavorite: opts.favoriteIds?.has(id) ?? false,
            isCategoryCluster: false,
          },
        });
      }
    } else {
      const fill = palette.categoryClusterFill(cat);
      const h = CATEGORY_HUE[cat] ?? 232;
      const stroke = palette.mode === 'dark' ? cyOklch(0.72, 0.1, h) : cyOklch(0.48, 0.1, h);
      const size = 44 + Math.min(ids.length, 10) * 2;
      elements.push({
        group: 'nodes',
        data: {
          id: categoryClusterId(cat),
          label: `${label}  ${ids.length}`,
          category: cat,
          region: 'both',
          maturity: 'stable',
          size,
          fill,
          alpha: 1,
          stroke,
          hop: 0,
          showLabel: true,
          isFocus: false,
          isFavorite: false,
          isCategoryCluster: true,
          memberCount: ids.length,
          clusterCategory: cat,
        },
      });
    }
  }

  // 聚合边：同一端点对合并
  const agg = new Map<string, { count: number; weight: number; group: RelationGroup }>();
  for (const e of edges) {
    const a = endpointOf(e.from);
    const b = endpointOf(e.to);
    if (!a || !b || a === b) continue;
    const [lo, hi] = a < b ? [a, b] : [b, a];
    const key = `${lo}|${hi}`;
    const prev = agg.get(key);
    const group = relationGroup(e.type);
    if (prev) {
      prev.count += 1;
      prev.weight = Math.max(prev.weight, e.weight);
    } else {
      agg.set(key, { count: 1, weight: e.weight, group });
    }
  }

  let ei = 0;
  for (const [key, meta] of agg) {
    const [source, target] = key.split('|') as [string, string];
    elements.push({
      group: 'edges',
      data: {
        id: `agg-${ei++}`,
        source,
        target,
        type: 'commonly_used_with',
        weight: meta.weight,
        confidence: 'inferred',
        group: meta.group,
        color: palette.edgeGroup[meta.group],
        width: 1.5 + Math.min(meta.count, 8) * 0.55,
        lineDash: confidenceLineStyle('inferred'),
        directed: false,
        isConflict: false,
        aggCount: meta.count,
      },
    });
  }

  return elements;
}

/** 从内容库构建 Cytoscape elements（视图投影 + 焦点邻域）。 */
export function buildGraphElements(
  bundle: ContentBundle,
  graph: GraphEngine,
  opts: GraphElementsOpts,
): ElementDefinition[] {
  const { focusId, hops, favoriteIds, filter, lens = 'ecosystem', recipeId, personalIds } = opts;
  const palette = opts.palette ?? resolveGraphPalette();
  const catOf = (id: Id) => bundle.entries.get(id)?.category;
  const typeAllow = LENS_EDGE_TYPES[lens];

  let nodes: Id[];
  let edges: Edge[];

  if (lens === 'recipe') {
    const recipe = recipeId ? bundle.recipes.get(recipeId) : bundle.recipes.values().next().value;
    const layerIds = collectRecipeIds(recipe);
    nodes = [...layerIds].filter((id) => bundle.entries.has(id));
    const nodeSet = new Set(nodes);
    edges = bundle.edges.filter(
      (e) => nodeSet.has(e.from) && nodeSet.has(e.to) && passFilter(e, catOf, filter),
    );
  } else if (lens === 'personal') {
    const ids = new Set<string>(personalIds ?? []);
    if (focusId) ids.add(focusId);
    nodes = [...ids].filter((id) => bundle.entries.has(id));
    const nodeSet = new Set(nodes);
    edges = bundle.edges.filter(
      (e) => nodeSet.has(e.from) && nodeSet.has(e.to) && passFilter(e, catOf, filter),
    );
  } else if (lens === 'alternatives' && focusId && bundle.entries.has(focusId)) {
    const alts = new Set<Id>([focusId, ...graph.alternatives(focusId)]);
    // 二跳替代簇
    for (const a of [...alts]) {
      for (const b of graph.alternatives(a)) alts.add(b);
    }
    nodes = [...alts].filter((id) => bundle.entries.has(id));
    const nodeSet = new Set(nodes);
    edges = bundle.edges.filter(
      (e) =>
        nodeSet.has(e.from) &&
        nodeSet.has(e.to) &&
        (!typeAllow || typeAllow.has(e.type)) &&
        passFilter(e, catOf, filter),
    );
  } else if (focusId && bundle.entries.has(focusId)) {
    const sub = graph.subgraph([focusId], hops);
    nodes = sub.nodes.filter((id) => bundle.entries.has(id));
    edges = sub.edges.filter((e) => bundle.entries.has(e.from) && bundle.entries.has(e.to));
  } else {
    nodes = [...bundle.entries.keys()];
    edges = bundle.edges.filter((e) => bundle.entries.has(e.from) && bundle.entries.has(e.to));
  }

  if (typeAllow) {
    edges = edges.filter((e) => typeAllow.has(e.type));
  }

  edges = edges.filter((e) => passFilter(e, catOf, filter));

  // 镜像视图：无焦点时保留所有镜像边端点
  if (lens === 'mirror' && (!focusId || !bundle.entries.has(focusId))) {
    const linked = new Set<Id>();
    for (const e of edges) {
      linked.add(e.from);
      linked.add(e.to);
    }
    nodes = [...linked].filter((id) => bundle.entries.has(id));
  }

  // 依赖 / 学习：裁到有边的节点（保留焦点）
  if (lens === 'dependency' || lens === 'learning' || lens === 'compat') {
    const linked = new Set<Id>();
    for (const e of edges) {
      linked.add(e.from);
      linked.add(e.to);
    }
    if (focusId) linked.add(focusId);
    if (linked.size > 0) nodes = nodes.filter((id) => linked.has(id));
  }

  const hasEdgeFilter =
    (filter?.edgeGroups && filter.edgeGroups.size > 0) ||
    (filter?.confidences && filter.confidences.size > 0);
  const hasCatFilter = filter?.categories && filter.categories.size > 0;

  if (hasCatFilter && filter?.categories) {
    const cats = filter.categories;
    nodes = nodes.filter((id) => {
      if (id === focusId) return true;
      const c = catOf(id);
      return c != null && cats.has(c);
    });
    const nodeSet = new Set(nodes);
    edges = edges.filter((e) => nodeSet.has(e.from) && nodeSet.has(e.to));
  }

  if (hasEdgeFilter || hasCatFilter) {
    const linked = new Set<Id>();
    for (const e of edges) {
      linked.add(e.from);
      linked.add(e.to);
    }
    if (focusId) linked.add(focusId);
    if (hasEdgeFilter && !hasCatFilter) {
      nodes = nodes.filter((id) => linked.has(id));
    }
  }

  // 厂商视图：补全同 vendor 的孤立节点（有焦点时）
  if (lens === 'vendor' && focusId) {
    const focusVendor = bundle.entries.get(focusId)?.vendorId;
    if (focusVendor) {
      for (const e of bundle.entries.values()) {
        if (e.vendorId === focusVendor) {
          if (!nodes.includes(e.id)) nodes.push(e.id);
        }
      }
    }
  }

  const useClusters = shouldUseCategoryClusters(opts.clusterMode, nodes.length, focusId, lens);
  if (useClusters && lens !== 'vendor') {
    return buildCategoryClusterElements(bundle, nodes, edges, {
      favoriteIds,
      expanded: opts.expandedCategories ?? new Set(),
      palette,
    });
  }

  const degree = new Map<string, number>();
  for (const e of edges) {
    degree.set(e.from, (degree.get(e.from) ?? 0) + 1);
    degree.set(e.to, (degree.get(e.to) ?? 0) + 1);
  }

  const hopsFromFocus = hopDistances(focusId, edges, nodes);

  const elements: ElementDefinition[] = [];
  const vendorParents = new Set<string>();

  if (lens === 'vendor') {
    for (const id of nodes) {
      const entry = bundle.entries.get(id);
      if (!entry?.vendorId) continue;
      const pid = `vendor:${entry.vendorId}`;
      if (vendorParents.has(pid)) continue;
      vendorParents.add(pid);
      const v = bundle.vendors.get(entry.vendorId);
      elements.push({
        group: 'nodes',
        data: {
          id: pid,
          label: v?.name ?? entry.vendorId,
          isCluster: true,
          size: 1,
          fill: 'transparent',
          alpha: 0,
          stroke: 'transparent',
          isFocus: false,
          isFavorite: false,
          hop: 0,
          showLabel: true,
        },
      });
    }
  }

  for (const id of nodes) {
    const entry = bundle.entries.get(id);
    if (!entry) continue;
    const deg = degree.get(id) ?? 1;
    const isFocus = id === focusId;
    const hop = hopsFromFocus.has(id) ? hopsFromFocus.get(id)! : focusId ? 2 : 0;
    let fill = palette.categoryFill(entry.category);
    if (lens === 'vendor' && entry.vendorId) fill = vendorFill(entry.vendorId, palette.mode);
    let alpha = palette.maturityAlpha[entry.maturity] ?? 0.75;
    if (focusId && hop >= 2) alpha = Math.max(0.28, alpha * 0.72);
    const stroke = palette.region[entry.region] ?? palette.region.both;
    const parent = lens === 'vendor' && entry.vendorId ? `vendor:${entry.vendorId}` : undefined;
    const size = nodeVisualSize({ degree: deg, isFocus, hop: focusId ? hop : null });
    // 始终显示标签；层次靠尺寸/透明度/字色，不藏字
    const showLabel = true;
    elements.push({
      group: 'nodes',
      data: {
        id,
        label: entry.name,
        category: entry.category,
        region: entry.region,
        maturity: entry.maturity,
        size,
        fill,
        alpha,
        stroke,
        hop,
        showLabel,
        isFocus,
        isFavorite: favoriteIds?.has(id) ?? false,
        isPersonal: personalIds?.has(id) ?? false,
        isRecipeLayer: lens === 'recipe',
        ...(parent ? { parent } : {}),
      },
    });
  }

  for (const e of edges) {
    const group = relationGroup(e.type);
    let color = palette.edgeGroup[group];
    if (lens === 'compat') {
      color = e.type === 'conflicts_with' ? palette.conflict : palette.compat;
    }
    if (lens === 'mirror') {
      color = palette.mirror;
    }
    elements.push({
      group: 'edges',
      data: {
        id: e.id,
        source: e.from,
        target: e.to,
        type: e.type,
        weight: e.weight,
        confidence: e.confidence,
        group,
        color,
        width: 1.5 + e.weight * 2.2,
        lineDash: confidenceLineStyle(e.confidence),
        directed: !isSymmetric(e.type),
        isConflict: e.type === 'conflicts_with',
      },
    });
  }

  return elements;
}

export type GraphLayoutKind = 'force' | 'dag' | 'mirror' | 'cose' | 'preset';

export function layoutKindForLens(lens: GraphLens): GraphLayoutKind {
  return lensMeta(lens).layout;
}

/** 国内外镜像：国内左、国外右、both 居中。 */
export function mirrorPositions(
  elements: ElementDefinition[],
  width: number,
  height: number,
): LayoutPositions {
  const nodes = elements.filter((el) => el.group === 'nodes' && el.data && !el.data.isCluster);
  const domestic: ElementDefinition[] = [];
  const overseas: ElementDefinition[] = [];
  const both: ElementDefinition[] = [];
  for (const n of nodes) {
    const r = n.data?.region as string;
    if (r === 'domestic') domestic.push(n);
    else if (r === 'overseas') overseas.push(n);
    else both.push(n);
  }
  const placeCol = (list: ElementDefinition[], x: number) => {
    const out: LayoutPositions = {};
    const gap = Math.min(80, (height - 80) / Math.max(list.length, 1));
    const startY = height / 2 - ((list.length - 1) * gap) / 2;
    list.forEach((n, i) => {
      const id = n.data?.id;
      if (typeof id !== 'string') return;
      out[id] = { x, y: startY + i * gap };
    });
    return out;
  };
  return {
    ...placeCol(domestic, width * 0.22),
    ...placeCol(both, width * 0.5),
    ...placeCol(overseas, width * 0.78),
  };
}

/** 墨图 stylesheet：标签外置、无 CJK 描边（canvas 粗描边会糊成墨块）。 */
export function buildCytoscapeStyle(palette: GraphPalette) {
  const dark = palette.mode === 'dark';
  return [
    {
      selector: 'core',
      style: {
        'active-bg-opacity': 0,
        'selection-box-color': palette.selected,
        'selection-box-opacity': 0.1,
        'selection-box-border-color': palette.selected,
        'selection-box-border-width': 1,
      },
    },
    {
      selector: 'node',
      style: {
        label: 'data(label)',
        width: 'data(size)',
        height: 'data(size)',
        shape: 'ellipse',
        'background-color': 'data(fill)',
        'background-opacity': 'data(alpha)',
        'border-width': 2.5,
        'border-color': 'data(stroke)',
        'border-opacity': 1,
        'underlay-opacity': dark ? 0.16 : 0.08,
        'underlay-color': 'data(stroke)',
        'underlay-padding': 3,
        'underlay-shape': 'ellipse',
        color: palette.label,
        /* canvas 上楷体加粗易糊，用文楷 Regular */
        'font-family': 'LXGW WenKai, "PingFang SC", "Microsoft YaHei", sans-serif',
        'font-size': 13,
        'font-weight': 400,
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 10,
        'text-wrap': 'wrap',
        'text-max-width': 120,
        'text-opacity': 1,
        'text-background-color': palette.labelBg,
        'text-background-opacity': 0.96,
        'text-background-padding': 3,
        'text-background-shape': 'roundrectangle',
        /* 禁止描边：CJK + outline 在 cytoscape 会叠成黑块 */
        'text-outline-width': 0,
        'text-outline-opacity': 0,
        'overlay-padding': 4,
        'overlay-opacity': 0,
        'z-index': 10,
        'z-index-compare': 'manual',
      },
    },
    {
      /* both 地区：虚线环 + 略加粗，与单地区实线区分 */
      selector: 'node[region = "both"]',
      style: {
        'border-style': 'dashed',
        'border-width': 3,
      },
    },
    {
      /* 远景节点：弱化标签字色，仍可读 */
      selector: 'node[hop >= 2]',
      style: {
        color: palette.labelMuted,
        'font-size': 12,
        'text-background-opacity': 0.9,
        'z-index': 8,
      },
    },
    {
      selector: 'node[?isCluster]',
      style: {
        label: 'data(label)',
        'background-opacity': 0.1,
        'background-color': palette.clusterFill,
        'border-width': 1.5,
        'border-color': palette.clusterBorder,
        'border-style': 'dashed',
        'underlay-opacity': 0,
        'text-valign': 'top',
        'text-margin-y': -10,
        'font-size': 12,
        'font-weight': 400,
        color: palette.labelMuted,
        'text-background-opacity': 0.96,
        'text-outline-width': 0,
        padding: 28,
        shape: 'roundrectangle',
        'z-index': 1,
      },
    },
    {
      /* 分类簇：色块在上、标签在下，避免字挤在灰块里 */
      selector: 'node[?isCategoryCluster]',
      style: {
        shape: 'roundrectangle',
        width: 'data(size)',
        height: 'data(size)',
        'font-size': 13,
        'font-weight': 400,
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 10,
        'text-wrap': 'wrap',
        'text-max-width': 128,
        'border-width': 1.75,
        'border-style': 'solid',
        'border-color': 'data(stroke)',
        'background-opacity': 1,
        'underlay-opacity': dark ? 0.12 : 0.06,
        'underlay-padding': 2,
        'overlay-padding': 4,
        'text-background-color': palette.labelBg,
        'text-background-opacity': 0.98,
        'text-background-padding': 4,
        'text-background-shape': 'roundrectangle',
        'text-outline-width': 0,
        'text-outline-opacity': 0,
        color: palette.label,
        'text-opacity': 1,
        'z-index': 12,
      },
    },
    {
      selector: 'node[?isFocus]',
      style: {
        'border-width': 3.5,
        'border-style': 'solid',
        'border-color': palette.focus,
        'underlay-color': palette.focus,
        'underlay-opacity': dark ? 0.32 : 0.2,
        'underlay-padding': 8,
        'overlay-color': palette.focus,
        'overlay-opacity': 0.08,
        'overlay-padding': 6,
        'font-size': 14,
        'font-weight': 500,
        color: palette.label,
        'text-opacity': 1,
        'text-background-opacity': 0.98,
        'z-index': 20,
      },
    },
    {
      selector: 'node[?isFavorite]',
      style: {
        'border-style': 'double',
        'border-width': 3,
        'border-color': palette.favorite,
      },
    },
    {
      selector: 'node[?isPersonal]',
      style: {
        'border-width': 2.75,
        'border-color': palette.personal,
        'underlay-color': palette.personal,
        'underlay-opacity': 0.16,
      },
    },
    {
      selector: 'node.link-source',
      style: {
        'border-width': 3.5,
        'border-color': palette.focus,
        'underlay-color': palette.focus,
        'underlay-opacity': 0.3,
        'underlay-padding': 9,
        'z-index': 25,
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-color': palette.selected,
        'border-width': 3,
        'underlay-color': palette.selected,
        'underlay-opacity': 0.2,
        'z-index': 22,
      },
    },
    {
      selector: 'edge',
      style: {
        width: 'data(width)',
        'line-color': 'data(color)',
        'target-arrow-color': 'data(color)',
        'curve-style': 'bezier',
        'line-cap': 'round',
        'source-distance-from-node': 4,
        'target-distance-from-node': 4,
        opacity: palette.edgeOpacity,
        'line-style': 'solid',
        'z-index': 1,
        'z-index-compare': 'manual',
      },
    },
    {
      selector: 'edge[?directed]',
      style: {
        'target-arrow-shape': 'tee',
        'arrow-scale': 0.75,
      },
    },
    {
      selector: 'edge[confidence = "community"]',
      style: { 'line-style': 'dashed', opacity: palette.edgeOpacity * 0.9 },
    },
    {
      selector: 'edge[confidence = "inferred"]',
      style: { 'line-style': 'dotted', opacity: palette.edgeOpacity * 0.78 },
    },
    {
      selector: 'edge[?isConflict]',
      style: {
        'line-color': palette.conflict,
        'target-arrow-color': palette.conflict,
        width: 2.75,
        opacity: 0.88,
        'target-arrow-shape': 'triangle',
        'z-index': 5,
      },
    },
  ];
}

export function createCytoscape(
  container: HTMLElement,
  elements: ElementDefinition[],
  positions?: LayoutPositions | null,
  palette: GraphPalette = resolveGraphPalette(),
): Core {
  const cy = cytoscape({
    container,
    elements,
    style: buildCytoscapeStyle(palette) as never,
    layout: positions
      ? { name: 'preset', positions, fit: true, padding: 56 }
      : {
          name: 'cose',
          animate: false,
          padding: 56,
          nodeRepulsion: () => 14000,
          idealEdgeLength: () => 140,
          nestingFactor: 1.2,
          nodeOverlap: 28,
          gravity: 0.6,
          numIter: 1200,
        },
    minZoom: 0.25,
    maxZoom: 2.5,
    wheelSensitivity: 0.25,
    pixelRatio: 'auto',
  });
  return cy;
}

export function runBreadthfirstLayout(cy: Core, roots?: string[]): void {
  cy.layout({
    name: 'breadthfirst',
    directed: true,
    spacingFactor: 1.35,
    padding: 56,
    animate: false,
    roots: roots?.length ? roots : undefined,
  }).run();
}

export function runCoseLayout(cy: Core): void {
  cy.layout({
    name: 'cose',
    animate: false,
    padding: 56,
    nodeRepulsion: () => 16000,
    idealEdgeLength: () => 150,
    nestingFactor: 1.4,
    nodeOverlap: 32,
    gravity: 0.55,
    numIter: 1400,
  }).run();
}

let worker: Worker | null = null;

function getLayoutWorker(): Worker {
  if (!worker) {
    worker = new Worker(new URL('./layout.worker.ts', import.meta.url), { type: 'module' });
  }
  return worker;
}

/** 在 Worker 中计算力导向坐标。 */
export function computeForceLayout(
  elements: ElementDefinition[],
  width: number,
  height: number,
): Promise<LayoutPositions> {
  const nodes = elements
    .filter((el) => el.group === 'nodes' && el.data && !el.data.isCluster)
    .map((el) => {
      const size = Number(el.data?.size ?? 32);
      const label = String(el.data?.label ?? '');
      // 视觉半径 + 标签高度/半宽预留，避免字叠字
      const labelPad = Math.min(56, 28 + label.length * 1.2);
      return {
        id: String(el.data?.id ?? ''),
        radius: Math.max(42, size / 2 + labelPad),
      };
    })
    .filter((n) => n.id);
  const edges = elements
    .filter((el) => el.group === 'edges' && el.data)
    .map((el) => ({
      source: String(el.data?.source ?? ''),
      target: String(el.data?.target ?? ''),
    }))
    .filter((e) => e.source && e.target);

  if (nodes.length === 0) return Promise.resolve({});

  // 布局画布略大于视口，给斥力留出走位空间
  const layoutW = Math.max(width * 1.15, 520);
  const layoutH = Math.max(height * 1.15, 400);
  const iterations = Math.min(240, 90 + nodes.length * 5);

  return new Promise((resolve, reject) => {
    const w = getLayoutWorker();
    const onMsg = (ev: MessageEvent<LayoutPositions>) => {
      w.removeEventListener('message', onMsg);
      w.removeEventListener('error', onErr);
      resolve(ev.data);
    };
    const onErr = (err: ErrorEvent) => {
      w.removeEventListener('message', onMsg);
      w.removeEventListener('error', onErr);
      reject(err.error ?? err);
    };
    w.addEventListener('message', onMsg);
    w.addEventListener('error', onErr);
    const req: LayoutRequest = {
      nodes,
      edges,
      width: layoutW,
      height: layoutH,
      iterations,
    };
    w.postMessage(req);
  });
}
