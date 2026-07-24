import { Edge } from './schema/edge.ts';
import { Entry } from './schema/entry.ts';
import { Category, Concept, Vendor } from './schema/meta.ts';
import { PopularitySnapshot } from './schema/popularity.ts';
import { RankingSystem } from './schema/ranking.ts';
import { StackRecipe } from './schema/recipe.ts';
import type { SearchDoc } from './search.ts';
import type { ContentBundle } from './types.ts';

/** 原始内容（未校验），通常由构建期脚本从 content/ 生成。 */
export interface RawContent {
  entries: unknown[];
  edges: unknown[];
  vendors: unknown[];
  concepts: unknown[];
  recipes: unknown[];
  categories: unknown[];
  rankingSystems?: unknown[];
  /** 外部客观流行度快照（content/signals/popularity.json 的内容） */
  popularity?: unknown;
  /** 构建期预计算的检索文档；运行时若存在可直接装配索引，省去重建。 */
  searchDocs?: SearchDoc[];
}

/**
 * 从原始内容装配为 ContentBundle（浏览器安全，无 fs 依赖）。
 * 逐项用 Zod 校验，非法数据抛错。
 */
export function buildBundle(raw: RawContent): ContentBundle {
  const entries = raw.entries.map((e) => Entry.parse(e));
  const vendors = raw.vendors.map((v) => Vendor.parse(v));
  const concepts = raw.concepts.map((c) => Concept.parse(c));
  const recipes = raw.recipes.map((r) => StackRecipe.parse(r));
  const rankingSystems = (raw.rankingSystems ?? []).map((r) => RankingSystem.parse(r));
  const popularity = raw.popularity ? PopularitySnapshot.parse(raw.popularity).entries : {};
  return {
    entries: new Map(entries.map((e) => [e.id, e])),
    edges: raw.edges.map((x) => Edge.parse(x)),
    vendors: new Map(vendors.map((v) => [v.id, v])),
    categories: raw.categories.map((c) => Category.parse(c)),
    concepts: new Map(concepts.map((c) => [c.id, c])),
    recipes: new Map(recipes.map((r) => [r.id, r])),
    rankingSystems: new Map(rankingSystems.map((r) => [r.id, r])),
    popularity: new Map(Object.entries(popularity)),
  };
}
