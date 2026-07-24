import { describe, expect, it } from 'vitest';
import type { Edge } from '../schema/edge.ts';
import type { Entry } from '../schema/entry.ts';
import type { StackRecipe } from '../schema/recipe.ts';
import type { ContentBundle } from '../types.ts';
import { buildGraph } from './engine.ts';
import { INVERSE, isSymmetric } from './inverse.ts';

function entry(
  id: string,
  vendorId?: string,
  category = 'coding-agent',
  region: Entry['region'] = 'overseas',
): Entry {
  return {
    id,
    name: id,
    category,
    vendorId,
    region,
    oneLiner: id,
    descriptionMd: '',
    officialUrl: 'https://example.com',
    pricing: { model: 'free' },
    availability: { chinaAccessible: true, needsCompany: false, needsIcp: false, regions: [] },
    tags: [],
    maturity: 'stable',
    tutorialLinks: [],
    externalLinks: [],
    pitfalls: [],
    updates: [],
    rankings: [],
    sources: [],
    lastReviewed: '2026-07-01',
  };
}

function edge(from: string, to: string, type: Edge['type'], weight = 0.9): Edge {
  return {
    id: `${from}-${type}-${to}`,
    from,
    to,
    type,
    weight,
    confidence: 'verified',
    sources: [],
    createdAt: '2026-07-01',
  };
}

function makeBundle(): ContentBundle {
  const paidHost = entry('paid-host', undefined, 'cloud-deploy');
  paidHost.pricing = { model: 'subscription' };
  paidHost.availability = {
    chinaAccessible: false,
    needsCompany: false,
    needsIcp: false,
    regions: [],
  };
  const entries = new Map<string, Entry>(
    [
      entry('cursor', 'anysphere'),
      entry('trae', 'bytedance', 'coding-agent', 'domestic'),
      entry('windsurf'),
      entry('claude-opus', 'anthropic', 'llm'),
      entry('nextjs', 'vercel', 'framework'),
      entry('react', undefined, 'framework'),
      entry('vercel', 'vercel', 'cloud-deploy'),
      entry('netlify', undefined, 'cloud-deploy'),
      entry('supabase', 'vercel', 'baas-auth'),
      paidHost,
    ].map((e) => [e.id, e]),
  );
  const edges: Edge[] = [
    edge('cursor', 'windsurf', 'alternative_to'),
    edge('cursor', 'claude-opus', 'powered_by'),
    edge('trae', 'cursor', 'domestic_equivalent_of'),
    edge('nextjs', 'react', 'depends_on'),
    edge('vercel', 'netlify', 'conflicts_with'),
    edge('cursor', 'nextjs', 'commonly_used_with', 0.7),
    edge('nextjs', 'vercel', 'commonly_used_with', 0.9),
  ];
  const recipes = new Map<string, StackRecipe>([
    [
      'r1',
      {
        id: 'r1',
        name: 'r1',
        target: '',
        layers: { agent: 'cursor', fw: 'nextjs', deploy: 'vercel' },
        rationaleMd: '',
        caveats: [],
      },
    ],
  ]);
  return {
    entries,
    edges,
    vendors: new Map(),
    categories: [],
    concepts: new Map(),
    recipes,
    rankingSystems: new Map(),
    popularity: new Map(),
  };
}

describe('inverse map', () => {
  it('每个 EdgeType 都有反向映射', () => {
    expect(INVERSE.alternative_to).toBe('self');
    expect(isSymmetric('alternative_to')).toBe(true);
    expect(isSymmetric('depends_on')).toBe(false);
    expect(INVERSE.depends_on).toBe('dependency_of');
    expect(INVERSE.domestic_equivalent_of).toBe('overseas_equivalent_of');
  });
});

describe('graph engine', () => {
  const g = buildGraph(makeBundle());

  it('neighbors 返回双向相连边', () => {
    expect(g.neighbors('cursor')).toHaveLength(4);
    expect(g.neighbors('react')).toHaveLength(1);
    expect(g.neighbors('cursor', { types: ['powered_by'] })).toHaveLength(1);
    expect(g.neighbors('cursor', { minWeight: 0.8 })).toHaveLength(3);
  });

  it('related 从入边取反向标签', () => {
    // react 是 nextjs depends_on 的目标，从 react 视角应为 dependency_of
    expect(g.related('react').dependency_of).toEqual(['nextjs']);
    // cursor 出边 powered_by 保持原样
    expect(g.related('cursor').powered_by).toEqual(['claude-opus']);
  });

  it('国内外对标：国内→国外写入，反向视图给出国内平替', () => {
    // trae --domestic_equivalent_of--> cursor
    expect(g.related('trae').domestic_equivalent_of).toEqual(['cursor']);
    expect(g.related('cursor').overseas_equivalent_of).toEqual(['trae']);
    expect(g.domesticEquivalents('cursor')).toEqual(['trae']);
    expect(g.domesticEquivalents('trae')).toEqual([]);
  });

  it('alternatives / subgraph / shortestPath', () => {
    expect(g.alternatives('cursor')).toContain('windsurf');
    const sub = g.subgraph(['cursor'], 1);
    expect(sub.nodes).toContain('claude-opus');
    expect(g.shortestPath('react', 'claude-opus')).toEqual([
      'react',
      'nextjs',
      'cursor',
      'claude-opus',
    ]);
    expect(g.shortestPath('react', 'supabase')).toBeNull();
  });

  it('impactOf 沿依赖反向收集受影响节点', () => {
    // nextjs depends_on react → react 的 dependency_of 含 nextjs
    // cursor commonly_used_with nextjs 不计入影响面
    const impact = g.impactOf('react');
    expect(impact).toContain('nextjs');
    // 再从 nextjs：cursor cuw 不算；vercel cuw 不算；若有 hosts 才算
    expect(impact).not.toContain('cursor');
  });

  it('validateStack 检出冲突与供应商集中', () => {
    const issues = g.validateStack({ a: 'vercel', b: 'netlify', c: 'nextjs', d: 'supabase' });
    expect(issues.some((i) => i.kind === 'conflict')).toBe(true);
    expect(issues.some((i) => i.kind === 'vendor-concentration' && i.vendorId === 'vercel')).toBe(
      true,
    );
  });

  it('coOccurrence 从 recipe 推导共现边', () => {
    const co = g.coOccurrence();
    // 3 个层两两共现 -> 3 条边
    expect(co).toHaveLength(3);
    expect(co.every((e) => e.type === 'commonly_used_with' && e.confidence === 'inferred')).toBe(
      true,
    );
  });

  it('recommendForCategory 沿常搭配边排序并排除冲突', () => {
    const ranked = g.recommendForCategory(['cursor'], 'framework');
    expect(ranked[0]?.id).toBe('nextjs');
    expect(ranked[0]?.score).toBeGreaterThan(0);

    const deploy = g.recommendForCategory(['nextjs'], 'cloud-deploy');
    expect(deploy[0]?.id).toBe('vercel');

    const withVercel = g.recommendForCategory(['nextjs', 'vercel'], 'cloud-deploy');
    expect(withVercel.map((c) => c.id)).not.toContain('netlify');
    expect(withVercel.map((c) => c.id)).not.toContain('vercel');
  });

  it('recommendForCategory 尊重预算与国内可访问偏好', () => {
    const freeOnly = g.recommendForCategory([], 'cloud-deploy', { budget: 'free' });
    expect(freeOnly.map((c) => c.id)).not.toContain('paid-host');

    const domestic = g.recommendForCategory([], 'cloud-deploy', { market: 'domestic' });
    expect(domestic.map((c) => c.id)).not.toContain('paid-host');
  });
});
