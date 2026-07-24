import type { Id, PricingModel, Region } from '../schema/common.ts';
import type { Edge, EdgeType } from '../schema/edge.ts';
import { sectionIdOf } from '../schema/meta.ts';
import type { ContentBundle } from '../types.ts';
import { INVERSE, isSymmetric } from './inverse.ts';

export interface NeighborOptions {
  types?: EdgeType[];
  minWeight?: number;
}

export type StackIssue =
  | { kind: 'conflict'; a: Id; b: Id }
  | { kind: 'vendor-concentration'; vendorId: Id; count: number };

/** 选型向导推荐偏好（G3）。 */
export interface RecommendPrefs {
  /** 目标市场：过滤/加权地区与国内可访问性。 */
  market?: 'overseas' | 'domestic' | 'both';
  /** 预算：free 只保留免费档；low 偏好 freemium；flexible 不限。 */
  budget?: 'free' | 'low' | 'flexible';
  /** 偏好开源定价。 */
  preferOpenSource?: boolean;
}

export interface RankedCandidate {
  id: Id;
  score: number;
  reasons: string[];
}

/** 沿图推荐时计入的边类型及其权重系数。 */
const REL_WEIGHT: Record<string, number> = {
  commonly_used_with: 1,
  compatible_with: 0.95,
  integrates_with: 0.85,
  hosts: 0.75,
  hosted_on: 0.75,
  powered_by: 0.7,
  powers: 0.7,
  depends_on: 0.55,
  dependency_of: 0.55,
  built_on: 0.5,
  foundation_of: 0.5,
  provides_access_to: 0.45,
  accessible_via: 0.45,
  domestic_equivalent_of: 0.4,
  overseas_equivalent_of: 0.4,
};

const FREE_MODELS: PricingModel[] = ['free', 'freemium', 'open-source'];

export interface GraphEngine {
  /** 与该节点相连的所有边（双向）。 */
  neighbors(id: Id, opts?: NeighborOptions): Edge[];
  /** 从该节点视角，按「有效关系类型」分组的邻居 id（有向边入边取反向标签）。 */
  related(id: Id): Record<string, Id[]>;
  /** ids 的 n 跳诱导子图。 */
  subgraph(ids: Id[], hops?: number): { nodes: Id[]; edges: Edge[] };
  /** 无权最短路径（把图当无向图）。 */
  shortestPath(from: Id, to: Id): Id[] | null;
  alternatives(id: Id): Id[];
  domesticEquivalents(id: Id): Id[];
  /**
   * G6 影响面：反向 BFS，沿 dependency_of / powers / hosts / foundation_of
   *（即「谁依赖/使用/托管本节点」），返回受影响节点（不含自身）。
   */
  impactOf(id: Id): Id[];
  /** 校验一套 stack：冲突边 + 供应商过度集中。 */
  validateStack(layers: Record<string, Id>): StackIssue[];
  /** 从 recipes 的层共现推导 commonly_used_with 权重。 */
  coOccurrence(): Edge[];
  /**
   * 给定已选条目，为 targetCategory 推荐候选（G3 沿图选型）。
   * 排除与已选冲突者；无图边时仍按偏好对同分类条目打分。
   */
  recommendForCategory(
    selected: Id[],
    targetCategory: Id,
    prefs?: RecommendPrefs,
  ): RankedCandidate[];
}

export function buildGraph(bundle: ContentBundle, extraEdges: Edge[] = []): GraphEngine {
  const adjacency = new Map<Id, Edge[]>();
  const touch = (node: Id, edge: Edge) => {
    const list = adjacency.get(node);
    if (list) list.push(edge);
    else adjacency.set(node, [edge]);
  };
  for (const edge of [...bundle.edges, ...extraEdges]) {
    touch(edge.from, edge);
    if (edge.to !== edge.from) touch(edge.to, edge);
  }

  const neighbors = (id: Id, opts: NeighborOptions = {}): Edge[] => {
    const list = adjacency.get(id) ?? [];
    return list.filter((e) => {
      if (opts.types && !opts.types.includes(e.type)) return false;
      if (opts.minWeight !== undefined && e.weight < opts.minWeight) return false;
      return true;
    });
  };

  const related = (id: Id): Record<string, Id[]> => {
    const groups: Record<string, Id[]> = {};
    for (const e of adjacency.get(id) ?? []) {
      let effectiveType: string;
      let other: Id;
      if (e.from === id) {
        effectiveType = e.type;
        other = e.to;
      } else {
        effectiveType = isSymmetric(e.type) ? e.type : INVERSE[e.type];
        other = e.from;
      }
      const list = groups[effectiveType] ?? [];
      list.push(other);
      groups[effectiveType] = list;
    }
    return groups;
  };

  const subgraph = (ids: Id[], hops = 1): { nodes: Id[]; edges: Edge[] } => {
    const visited = new Set<Id>(ids);
    let frontier = [...ids];
    for (let h = 0; h < hops; h++) {
      const next: Id[] = [];
      for (const node of frontier) {
        for (const e of adjacency.get(node) ?? []) {
          const other = e.from === node ? e.to : e.from;
          if (!visited.has(other)) {
            visited.add(other);
            next.push(other);
          }
        }
      }
      frontier = next;
      if (frontier.length === 0) break;
    }
    const edges = bundle.edges.filter((e) => visited.has(e.from) && visited.has(e.to));
    return { nodes: [...visited], edges };
  };

  const shortestPath = (from: Id, to: Id): Id[] | null => {
    if (from === to) return [from];
    const prev = new Map<Id, Id>();
    const queue: Id[] = [from];
    const seen = new Set<Id>([from]);
    while (queue.length > 0) {
      const node = queue.shift() as Id;
      for (const e of adjacency.get(node) ?? []) {
        const other = e.from === node ? e.to : e.from;
        if (seen.has(other)) continue;
        seen.add(other);
        prev.set(other, node);
        if (other === to) {
          const path: Id[] = [to];
          let cur: Id | undefined = to;
          while (cur !== undefined && cur !== from) {
            cur = prev.get(cur);
            if (cur !== undefined) path.unshift(cur);
          }
          return path;
        }
        queue.push(other);
      }
    }
    return null;
  };

  const alternatives = (id: Id): Id[] => {
    const r = related(id);
    // alternative_to 对称；开源平替落在 proprietary_counterpart_of（商业→开源的视角标签）
    return [...(r.alternative_to ?? []), ...(r.proprietary_counterpart_of ?? [])];
  };

  /** 国内平替：从当前节点视角，目标落在 overseas_equivalent_of（国外→国内 的反向视图）。 */
  const domesticEquivalents = (id: Id): Id[] => related(id).overseas_equivalent_of ?? [];

  /** 影响面边：从本节点视角的「被依赖/供能/托管」语义标签。 */
  const IMPACT_REL = new Set(['dependency_of', 'powers', 'hosts', 'foundation_of']);

  const impactOf = (id: Id): Id[] => {
    const ordered: Id[] = [];
    const seen = new Set<Id>([id]);
    const queue: Id[] = [id];
    while (queue.length > 0) {
      const cur = queue.shift() as Id;
      const r = related(cur);
      for (const [type, others] of Object.entries(r)) {
        if (!IMPACT_REL.has(type)) continue;
        for (const other of others) {
          if (seen.has(other)) continue;
          seen.add(other);
          ordered.push(other);
          queue.push(other);
        }
      }
    }
    return ordered;
  };

  const validateStack = (layers: Record<string, Id>): StackIssue[] => {
    const issues: StackIssue[] = [];
    const ids = Object.values(layers);
    const idSet = new Set(ids);
    // 冲突：任意两层间存在 conflicts_with
    for (const e of bundle.edges) {
      if (e.type === 'conflicts_with' && idSet.has(e.from) && idSet.has(e.to)) {
        issues.push({ kind: 'conflict', a: e.from, b: e.to });
      }
    }
    // 供应商集中度
    const vendorCount = new Map<Id, number>();
    for (const id of ids) {
      const vendorId = bundle.entries.get(id)?.vendorId;
      if (vendorId) vendorCount.set(vendorId, (vendorCount.get(vendorId) ?? 0) + 1);
    }
    for (const [vendorId, count] of vendorCount) {
      if (count >= 3) issues.push({ kind: 'vendor-concentration', vendorId, count });
    }
    return issues;
  };

  const coOccurrence = (): Edge[] => {
    const pairCount = new Map<string, number>();
    for (const recipe of bundle.recipes.values()) {
      const ids = [...new Set(Object.values(recipe.layers))].sort();
      for (let i = 0; i < ids.length; i++) {
        for (let j = i + 1; j < ids.length; j++) {
          const key = `${ids[i]}|${ids[j]}`;
          pairCount.set(key, (pairCount.get(key) ?? 0) + 1);
        }
      }
    }
    const max = Math.max(1, ...pairCount.values());
    const edges: Edge[] = [];
    for (const [key, count] of pairCount) {
      const [from, to] = key.split('|') as [Id, Id];
      edges.push({
        id: `co-${from}-${to}`,
        from,
        to,
        type: 'commonly_used_with',
        weight: count / max,
        confidence: 'inferred',
        sources: [],
        createdAt: '1970-01-01',
      });
    }
    return edges;
  };

  const conflictsWithSelected = (candidate: Id, selected: Set<Id>): boolean => {
    for (const e of adjacency.get(candidate) ?? []) {
      if (e.type !== 'conflicts_with') continue;
      const other = e.from === candidate ? e.to : e.from;
      if (selected.has(other)) return true;
    }
    return false;
  };

  const regionOk = (region: Region, market: RecommendPrefs['market']): boolean => {
    if (!market || market === 'both') return true;
    if (region === 'both') return true;
    return region === market;
  };

  const matchesTargetCategory = (entryCategory: Id, targetCategory: Id): boolean => {
    if (entryCategory === targetCategory) return true;
    // 选型向导可传 section id：匹配其下所有 leaf
    return sectionIdOf(bundle.categories, entryCategory) === targetCategory;
  };

  const recommendForCategory = (
    selected: Id[],
    targetCategory: Id,
    prefs: RecommendPrefs = {},
  ): RankedCandidate[] => {
    const selectedSet = new Set(selected);
    const scores = new Map<Id, { score: number; reasons: string[] }>();

    const bump = (id: Id, delta: number, reason: string) => {
      const cur = scores.get(id) ?? { score: 0, reasons: [] };
      cur.score += delta;
      if (reason && !cur.reasons.includes(reason)) cur.reasons.push(reason);
      scores.set(id, cur);
    };

    for (const sid of selected) {
      const fromName = bundle.entries.get(sid)?.name ?? sid;
      for (const e of adjacency.get(sid) ?? []) {
        const other = e.from === sid ? e.to : e.from;
        if (selectedSet.has(other)) continue;
        const entry = bundle.entries.get(other);
        if (!entry || !matchesTargetCategory(entry.category, targetCategory)) continue;
        const mult = REL_WEIGHT[e.type];
        if (mult === undefined) continue;
        const delta = e.weight * mult;
        bump(other, delta, `与 ${fromName} · ${e.type} (${e.weight.toFixed(2)})`);
      }
    }

    for (const [id, entry] of bundle.entries) {
      if (!matchesTargetCategory(entry.category, targetCategory)) continue;
      if (selectedSet.has(id)) continue;
      if (conflictsWithSelected(id, selectedSet)) continue;

      if (prefs.market === 'domestic' && !entry.availability.chinaAccessible) continue;
      if (!regionOk(entry.region, prefs.market)) continue;
      if (prefs.budget === 'free' && !FREE_MODELS.includes(entry.pricing.model)) continue;

      if (!scores.has(id)) scores.set(id, { score: 0, reasons: [] });
      const cur = scores.get(id);
      if (!cur) continue;

      if (prefs.market === 'domestic' && (entry.region === 'domestic' || entry.region === 'both')) {
        cur.score += 0.15;
        cur.reasons.push('符合国内市场');
      }
      if (prefs.market === 'overseas' && (entry.region === 'overseas' || entry.region === 'both')) {
        cur.score += 0.1;
      }
      if (
        prefs.budget === 'low' &&
        (entry.pricing.model === 'freemium' || entry.pricing.model === 'free')
      ) {
        cur.score += 0.12;
        cur.reasons.push('低预算友好');
      }
      if (prefs.preferOpenSource && entry.pricing.model === 'open-source') {
        cur.score += 0.2;
        cur.reasons.push('开源优先');
      }
      if (entry.maturity === 'mature' || entry.maturity === 'stable') {
        cur.score += 0.05;
      }
      if (cur.reasons.length === 0 && cur.score === 0) {
        cur.reasons.push('同分类候选');
      }
    }

    return [...scores.entries()]
      .filter(([id]) => {
        const entry = bundle.entries.get(id);
        if (!entry) return false;
        if (conflictsWithSelected(id, selectedSet)) return false;
        if (prefs.market === 'domestic' && !entry.availability.chinaAccessible) return false;
        if (!regionOk(entry.region, prefs.market)) return false;
        if (prefs.budget === 'free' && !FREE_MODELS.includes(entry.pricing.model)) return false;
        return true;
      })
      .map(([id, { score, reasons }]) => ({ id, score, reasons }))
      .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  };

  return {
    neighbors,
    related,
    subgraph,
    shortestPath,
    alternatives,
    domesticEquivalents,
    impactOf,
    validateStack,
    coOccurrence,
    recommendForCategory,
  };
}
