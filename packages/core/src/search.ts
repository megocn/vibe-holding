import type { Id, Maturity, PricingModel, Region } from './schema/common.ts';
import type { Category } from './schema/meta.ts';
import { sectionIdOf } from './schema/meta.ts';
import type { ContentBundle } from './types.ts';

export interface SearchOptions {
  category?: Id;
  region?: Region;
  tags?: string[];
  pricing?: PricingModel;
  maturity?: Maturity;
  chinaAccessible?: boolean;
}

export interface SearchResult {
  id: Id;
  score: number;
}

export interface SearchIndex {
  /** 关键词检索（可叠加分面筛选），按分数降序。 */
  query(text: string, opts?: SearchOptions): SearchResult[];
  /** 仅分面筛选，返回条目 id（按分类 order + 名称稳定排序）。 */
  filter(opts?: SearchOptions): Id[];
}

/**
 * 可序列化的检索文档：构建期由 {@link buildSearchDocs} 预计算并随内容包一起投递，
 * 运行时经 {@link indexFromDocs} 直接装配，省去每次启动重建 haystack 的开销。
 */
export interface SearchDoc {
  id: Id;
  name: string;
  haystackName: string;
  haystackMid: string;
  haystackLow: string;
  category: Id;
  region: Region;
  tags: string[];
  pricing: PricingModel;
  maturity: Maturity;
  chinaAccessible: boolean;
}

function matches(doc: SearchDoc, opts: SearchOptions, sectionOf: (categoryId: Id) => Id): boolean {
  if (opts.category) {
    const want = opts.category;
    if (doc.category !== want && sectionOf(doc.category) !== want) return false;
  }
  if (opts.region && doc.region !== opts.region) return false;
  if (opts.pricing && doc.pricing !== opts.pricing) return false;
  if (opts.maturity && doc.maturity !== opts.maturity) return false;
  if (opts.chinaAccessible !== undefined && doc.chinaAccessible !== opts.chinaAccessible)
    return false;
  if (opts.tags && opts.tags.length > 0) {
    for (const t of opts.tags) if (!doc.tags.includes(t)) return false;
  }
  return true;
}

/** 从内容包提取可序列化的检索文档（构建期调用，产物随内容包投递）。 */
export function buildSearchDocs(bundle: ContentBundle): SearchDoc[] {
  const docs: SearchDoc[] = [];
  for (const e of bundle.entries.values()) {
    docs.push({
      id: e.id,
      name: e.name,
      haystackName: `${e.name} ${e.id}`.toLowerCase(),
      haystackMid: `${e.oneLiner} ${e.tags.join(' ')}`.toLowerCase(),
      haystackLow: e.descriptionMd.toLowerCase(),
      category: e.category,
      region: e.region,
      tags: e.tags,
      pricing: e.pricing.model,
      maturity: e.maturity,
      chinaAccessible: e.availability.chinaAccessible,
    });
  }
  return docs;
}

/**
 * 由（预计算或即时构建的）检索文档装配检索索引。
 * 排序用 id→doc 映射，避免比较器内 O(n) 查找。
 */
export function indexFromDocs(
  docs: SearchDoc[],
  categories: Pick<Category, 'id' | 'kind' | 'parent' | 'order'>[],
): SearchIndex {
  const order = new Map(categories.map((c) => [c.id, c.order]));
  const sectionOf = (categoryId: Id): Id => sectionIdOf(categories, categoryId);
  const byId = new Map(docs.map((d) => [d.id, d]));

  const byCategoryThenName = (a: Id, b: Id): number => {
    const da = byId.get(a);
    const db = byId.get(b);
    if (!da || !db) return 0;
    const oa = order.get(da.category) ?? 999;
    const ob = order.get(db.category) ?? 999;
    if (oa !== ob) return oa - ob;
    return da.name.localeCompare(db.name);
  };

  const filter = (opts: SearchOptions = {}): Id[] =>
    docs
      .filter((d) => matches(d, opts, sectionOf))
      .map((d) => d.id)
      .sort(byCategoryThenName);

  const query = (text: string, opts: SearchOptions = {}): SearchResult[] => {
    const q = text.trim().toLowerCase();
    if (q === '') return filter(opts).map((id) => ({ id, score: 0 }));
    const terms = q.split(/\s+/);
    const results: SearchResult[] = [];
    for (const doc of docs) {
      if (!matches(doc, opts, sectionOf)) continue;
      let score = 0;
      for (const term of terms) {
        if (doc.haystackName.includes(term)) score += 3;
        else if (doc.haystackMid.includes(term)) score += 2;
        else if (doc.haystackLow.includes(term)) score += 1;
      }
      if (score > 0) results.push({ id: doc.id, score });
    }
    return results.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  };

  return { query, filter };
}

/** 从内容包即时构建检索索引（= buildSearchDocs + indexFromDocs）。 */
export function buildIndex(bundle: ContentBundle): SearchIndex {
  return indexFromDocs(buildSearchDocs(bundle), bundle.categories);
}
