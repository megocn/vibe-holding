import { describe, expect, it } from 'vitest';
import { buildPersonalEdgesFromStacks } from './personal.ts';

describe('buildPersonalEdgesFromStacks', () => {
  it('无栈时为空', () => {
    expect(buildPersonalEdgesFromStacks([])).toEqual([]);
  });

  it('单栈多层产生共现边', () => {
    const edges = buildPersonalEdgesFromStacks([
      { layers: { a: 'cursor', b: 'nextjs', c: 'vercel' } },
    ]);
    expect(edges).toHaveLength(3);
    expect(edges.every((e) => e.type === 'commonly_used_with')).toBe(true);
    expect(edges.every((e) => e.confidence === 'inferred')).toBe(true);
    expect(edges.every((e) => e.id.startsWith('pe-'))).toBe(true);
    expect(edges.every((e) => e.weight === 1)).toBe(true);
  });

  it('多栈提升共现权重', () => {
    const edges = buildPersonalEdgesFromStacks([
      { layers: { a: 'cursor', b: 'nextjs' } },
      { layers: { a: 'cursor', b: 'nextjs', c: 'supabase' } },
    ]);
    const pair = edges.find((e) => e.from === 'cursor' && e.to === 'nextjs');
    const other = edges.find((e) => e.from === 'cursor' && e.to === 'supabase');
    expect(pair?.weight).toBe(1);
    expect(other?.weight).toBe(0.5);
  });
});
