import type { ContentBundle, Id } from '@vh/core';
import { familyIdOf, lineIdsOfFamily } from '@vh/core';

export interface LlmFamilyNode {
  familyId: Id;
  familyName: string;
  /** 族条目 + 下属档位（档在前排序：旗舰优先可按 name） */
  lineIds: Id[];
}

/** 从 part_of 边构建 LLM 族→档 树（上下层）。 */
export function buildLlmFamilyTree(bundle: ContentBundle): LlmFamilyNode[] {
  const families = [...bundle.entries.values()]
    .filter((e) => e.category === 'llm-family')
    .sort((a, b) => a.name.localeCompare(b.name, 'zh'));

  return families.map((fam) => {
    const lineIds = lineIdsOfFamily(bundle.edges, fam.id)
      .filter((id) => bundle.entries.has(id))
      .sort((a, b) => {
        const na = bundle.entries.get(a)?.name ?? a;
        const nb = bundle.entries.get(b)?.name ?? b;
        return na.localeCompare(nb, 'zh');
      });
    return { familyId: fam.id, familyName: fam.name, lineIds };
  });
}

export function llmScopeIds(
  bundle: ContentBundle,
  familyId?: Id,
): Set<Id> {
  const tree = buildLlmFamilyTree(bundle);
  const ids = new Set<Id>();
  for (const node of tree) {
    if (familyId && node.familyId !== familyId) continue;
    ids.add(node.familyId);
    for (const lid of node.lineIds) ids.add(lid);
  }
  return ids;
}

export function isLlmSectionNav(
  categoryId: Id,
  categories: { id: string; kind?: string; parent?: string }[],
): boolean {
  if (categoryId === 'llm' || categoryId === 'llm-family' || categoryId === 'llm-line')
    return true;
  const cat = categories.find((c) => c.id === categoryId);
  return cat?.parent === 'llm' || cat?.id === 'llm';
}

export { familyIdOf, lineIdsOfFamily };
