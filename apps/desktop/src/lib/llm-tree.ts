import type { ContentBundle, Id } from '@vh/core';
import {
  computeProminence,
  familyIdOf,
  lineIdsOfFamily,
  sortIdsByPrimaryRanking,
  sortLlmFamiliesFromBundle,
} from '@vh/core';

export interface LlmFamilyNode {
  familyId: Id;
  familyName: string;
  /** 下属选型档位（按该档主榜排序） */
  lineIds: Id[];
}

/** 从 part_of 边构建 LLM 族→档 树；族序按榜单综合分（§2.3）。 */
export function buildLlmFamilyTree(bundle: ContentBundle): LlmFamilyNode[] {
  const prominence = computeProminence(bundle.entries.values(), bundle.popularity);
  const familyOrder = sortLlmFamiliesFromBundle(bundle, {
    prominenceOf: (id) => prominence.get(id),
  });

  return familyOrder.map((familyId) => {
    const fam = bundle.entries.get(familyId)!;
    const rawLines = lineIdsOfFamily(bundle.edges, familyId).filter((id) =>
      bundle.entries.has(id),
    );
    const lineIds = sortIdsByPrimaryRanking(
      rawLines,
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
    );
    return { familyId, familyName: fam.name, lineIds };
  });
}

export function llmScopeIds(bundle: ContentBundle, familyId?: Id): Set<Id> {
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
