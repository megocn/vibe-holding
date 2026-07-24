import type { Id } from './schema/common.ts';
import type { Edge } from './schema/edge.ts';
import type { StackRecipe } from './schema/recipe.ts';

/**
 * 由我的技术栈层共现生成私有 commonly_used_with 边。
 * weight = 共现次数 / 最大共现；confidence = inferred；id 前缀 pe-。
 */
export function buildPersonalEdgesFromStacks(
  stacks: Array<Pick<StackRecipe, 'layers'> | { layers?: Record<string, string> }>,
): Edge[] {
  const pairCount = new Map<string, { a: Id; b: Id; count: number }>();

  for (const stack of stacks) {
    const layers = stack.layers ?? {};
    const ids = [...new Set(Object.values(layers))].filter(Boolean).sort() as Id[];
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const a = ids[i] as Id;
        const b = ids[j] as Id;
        const key = `${a}|${b}`;
        const prev = pairCount.get(key);
        if (prev) prev.count += 1;
        else pairCount.set(key, { a, b, count: 1 });
      }
    }
  }

  if (pairCount.size === 0) return [];

  const max = Math.max(...[...pairCount.values()].map((p) => p.count));
  const today = new Date().toISOString().slice(0, 10);
  const edges: Edge[] = [];
  for (const { a, b, count } of pairCount.values()) {
    edges.push({
      id: `pe-${a}-${b}`,
      from: a,
      to: b,
      type: 'commonly_used_with',
      weight: count / max,
      note: `个人技术栈共现 ×${count}`,
      confidence: 'inferred',
      sources: [],
      createdAt: today,
    });
  }
  return edges.sort((x, y) => x.id.localeCompare(y.id));
}
