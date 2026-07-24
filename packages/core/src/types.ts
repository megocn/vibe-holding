import type { Id } from './schema/common.ts';
import type { Edge } from './schema/edge.ts';
import type { Entry } from './schema/entry.ts';
import type { Category, Concept, Vendor } from './schema/meta.ts';
import type { RankingSystem } from './schema/ranking.ts';
import type { StackRecipe } from './schema/recipe.ts';

export interface ContentBundle {
  entries: Map<Id, Entry>;
  edges: Edge[];
  vendors: Map<Id, Vendor>;
  categories: Category[];
  concepts: Map<Id, Concept>;
  recipes: Map<Id, StackRecipe>;
  /** 权威排行体系注册表（按 id） */
  rankingSystems: Map<Id, RankingSystem>;
}
