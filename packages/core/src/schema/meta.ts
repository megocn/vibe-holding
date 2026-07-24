import { z } from 'zod';
import { Id, Region } from './common.ts';

export const Vendor = z.object({
  id: Id,
  name: z.string(),
  region: Region,
  url: z.string().url().optional(),
  note: z.string().optional(),
});
export type Vendor = z.infer<typeof Vendor>;

/**
 * 分类两级：
 * - **section**：图廓分区（A–V），只用于导航地图，不直接挂条目、不挂排行。
 * - **leaf**：可比较叶类（如 ui-icons vs ui-kits），条目与权威排行挂在此级。
 */
export const CategoryKind = z.enum(['section', 'leaf']);
export type CategoryKind = z.infer<typeof CategoryKind>;

export const Category = z
  .object({
    id: Id,
    /** 仅 section 使用 A–V 字母代号；leaf 可省略 */
    code: z.string().regex(/^[A-Z]$/, 'section 代号需为单个大写字母 A–V').optional(),
    name: z.string(),
    /** leaf 必须指向 section；section 无 parent */
    parent: Id.optional(),
    kind: CategoryKind.default('section'),
    order: z.number().int(),
  })
  .superRefine((c, ctx) => {
    if (c.kind === 'section') {
      if (!c.code) {
        ctx.addIssue({ code: 'custom', message: 'section 必须有 A–V code', path: ['code'] });
      }
      if (c.parent) {
        ctx.addIssue({ code: 'custom', message: 'section 不应有 parent', path: ['parent'] });
      }
    } else if (!c.parent) {
      ctx.addIssue({ code: 'custom', message: 'leaf 必须有 parent（指向 section）', path: ['parent'] });
    }
  });
export type Category = z.infer<typeof Category>;

/** 由叶类 id 解析所属图廓 section id；若本身是 section 则返回自身。 */
export function sectionIdOf(
  categories: Iterable<Pick<Category, 'id' | 'kind' | 'parent'>>,
  categoryId: string,
): string {
  const byId = categoryIdIndex(categories);
  const cat = byId.get(categoryId);
  if (!cat) return categoryId;
  if (cat.kind === 'leaf' && cat.parent) return cat.parent;
  return cat.id;
}

/** 某 section 下的全部 leaf（按 order）。 */
export function leavesOfSection(
  categories: Iterable<Category>,
  sectionId: string,
): Category[] {
  return [...categories]
    .filter((c) => c.kind === 'leaf' && c.parent === sectionId)
    .sort((a, b) => a.order - b.order);
}

/** 判断 id 是否为 section（或未知时按非 leaf 处理）。 */
export function isSectionCategory(
  categories: Iterable<Pick<Category, 'id' | 'kind'>>,
  categoryId: string,
): boolean {
  const cat = categoryIdIndex(categories).get(categoryId);
  return !cat || cat.kind === 'section';
}

function categoryIdIndex(
  categories: Iterable<Pick<Category, 'id' | 'kind' | 'parent'>>,
): Map<string, Pick<Category, 'id' | 'kind' | 'parent'>> {
  const m = new Map<string, Pick<Category, 'id' | 'kind' | 'parent'>>();
  for (const c of categories) m.set(c.id, c);
  return m;
}

/** LLM 等「档位→产品族」：沿 part_of 边找家族条目 id。 */
export function familyIdOf(
  edges: Iterable<{ from: string; to: string; type: string }>,
  lineId: string,
): string | undefined {
  for (const e of edges) {
    if (e.type === 'part_of' && e.from === lineId) return e.to;
  }
  return undefined;
}

/** 产品族下的选型档位（part_of 指向该族的条目）。 */
export function lineIdsOfFamily(
  edges: Iterable<{ from: string; to: string; type: string }>,
  familyId: string,
): string[] {
  const out: string[] = [];
  for (const e of edges) {
    if (e.type === 'part_of' && e.to === familyId) out.push(e.from);
  }
  return out;
}

export const Concept = z.object({
  id: Id,
  name: z.string(),
  summaryMd: z.string(),
  aliases: z.array(z.string()).default([]),
});
export type Concept = z.infer<typeof Concept>;
