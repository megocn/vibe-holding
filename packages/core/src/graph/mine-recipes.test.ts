import { describe, expect, it } from 'vitest';
import type { Edge } from '../schema/edge.ts';
import type { Entry } from '../schema/entry.ts';
import type { StackRecipe } from '../schema/recipe.ts';
import type { ContentBundle } from '../types.ts';
import { learningPath, mineRecipeDrafts } from './mine-recipes.ts';

function entry(partial: Partial<Entry> & { id: string; category: string; name: string }): Entry {
  return {
    oneLiner: partial.oneLiner ?? partial.name,
    descriptionMd: 'd',
    officialUrl: 'https://example.com',
    region: 'overseas',
    pricing: { model: 'freemium' },
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
    ...partial,
  } as Entry;
}

function makeBundle(): ContentBundle {
  const entries = new Map<string, Entry>([
    ['cursor', entry({ id: 'cursor', name: 'Cursor', category: 'coding-agent' })],
    ['claude', entry({ id: 'claude', name: 'Claude', category: 'llm' })],
    ['nextjs', entry({ id: 'nextjs', name: 'Next', category: 'framework' })],
    ['react', entry({ id: 'react', name: 'React', category: 'ui-library' })],
    ['vercel', entry({ id: 'vercel', name: 'Vercel', category: 'cloud-deploy' })],
    ['supabase', entry({ id: 'supabase', name: 'Supabase', category: 'baas-auth' })],
    ['netlify', entry({ id: 'netlify', name: 'Netlify', category: 'cloud-deploy' })],
  ]);

  // 两套部分重叠方案 → 共现对可长出更完整、且不同于任一模板的草稿
  const r1: StackRecipe = {
    id: 'r1',
    name: 'R1',
    target: 't',
    layers: {
      'coding-agent': 'cursor',
      llm: 'claude',
      framework: 'nextjs',
      'cloud-deploy': 'vercel',
    },
    rationaleMd: 'x',
    caveats: [],
  };
  const r2: StackRecipe = {
    id: 'r2',
    name: 'R2',
    target: 't',
    layers: {
      'coding-agent': 'cursor',
      llm: 'claude',
      framework: 'nextjs',
      'baas-auth': 'supabase',
    },
    rationaleMd: 'x',
    caveats: [],
  };

  const edges: Edge[] = [
    {
      id: 'e-prereq',
      from: 'react',
      to: 'nextjs',
      type: 'prerequisite_of',
      weight: 0.9,
      confidence: 'verified',
      sources: [],
      createdAt: '2026-01-01',
    },
    {
      id: 'e-cuw',
      from: 'vercel',
      to: 'supabase',
      type: 'commonly_used_with',
      weight: 0.8,
      confidence: 'community',
      sources: [],
      createdAt: '2026-01-01',
    },
  ];

  return {
    entries,
    edges,
    vendors: new Map(),
    categories: [],
    concepts: new Map(),
    recipes: new Map([
      [r1.id, r1],
      [r2.id, r2],
    ]),
    rankingSystems: new Map(),
    popularity: new Map(),
  };
}

describe('mineRecipeDrafts', () => {
  it('从共现挖掘出草稿且无冲突', () => {
    const bundle = makeBundle();
    const drafts = mineRecipeDrafts(bundle, { maxDrafts: 5 });
    expect(drafts.length).toBeGreaterThan(0);
    expect(drafts[0]?.id.startsWith('draft-co-')).toBe(true);
    expect(Object.keys(drafts[0]?.layers ?? {}).length).toBeGreaterThanOrEqual(3);
    const ids = Object.values(drafts[0]?.layers ?? {});
    expect(ids).toContain('cursor');
    expect(ids).toContain('claude');
  });

  it('可叠加 extraStacks 共现', () => {
    const bundle = makeBundle();
    const drafts = mineRecipeDrafts(bundle, {
      maxDrafts: 5,
      extraStacks: [
        {
          layers: {
            'coding-agent': 'cursor',
            'cloud-deploy': 'netlify',
            framework: 'nextjs',
          },
        },
      ],
    });
    expect(drafts.length).toBeGreaterThan(0);
  });
});

describe('learningPath', () => {
  it('按前置关系排序', () => {
    const bundle = makeBundle();
    const path = learningPath(bundle, 'nextjs');
    expect(path[0]).toBe('react');
    expect(path.at(-1)).toBe('nextjs');
  });

  it('无前置时仅自身', () => {
    const bundle = makeBundle();
    expect(learningPath(bundle, 'cursor')).toEqual(['cursor']);
  });
});
