import { describe, expect, it } from 'vitest';
import { buildBundle } from './bundle.ts';
import { buildIndex } from './search.ts';

const raw = {
  categories: [
    { id: 'coding-agent', code: 'A', name: 'A', order: 1 },
    { id: 'llm', code: 'B', name: 'B', order: 2 },
  ],
  vendors: [],
  concepts: [],
  recipes: [],
  edges: [],
  entries: [
    {
      id: 'cursor',
      name: 'Cursor',
      category: 'coding-agent',
      region: 'overseas',
      oneLiner: 'AI 原生代码编辑器',
      descriptionMd: '基于 VS Code 的 AI 编辑器',
      officialUrl: 'https://cursor.com',
      pricing: { model: 'subscription' },
      availability: { chinaAccessible: true },
      tags: ['ai', 'ide'],
      maturity: 'stable',
      lastReviewed: '2026-07-01',
    },
    {
      id: 'glm',
      name: '智谱 GLM',
      category: 'llm',
      region: 'domestic',
      oneLiner: '国产大模型',
      descriptionMd: 'GLM 系列',
      officialUrl: 'https://bigmodel.cn',
      pricing: { model: 'usage' },
      availability: { chinaAccessible: true },
      tags: ['llm', 'domestic'],
      maturity: 'stable',
      lastReviewed: '2026-07-01',
    },
  ],
};

describe('search index', () => {
  const idx = buildIndex(buildBundle(raw));

  it('按名称命中优先', () => {
    const r = idx.query('cursor');
    expect(r[0]?.id).toBe('cursor');
  });

  it('可命中标签/一句话', () => {
    expect(idx.query('ide').some((r) => r.id === 'cursor')).toBe(true);
    expect(idx.query('国产').some((r) => r.id === 'glm')).toBe(true);
  });

  it('分面筛选：地区 / 分类', () => {
    expect(idx.filter({ region: 'domestic' })).toEqual(['glm']);
    expect(idx.filter({ category: 'coding-agent' })).toEqual(['cursor']);
  });

  it('空查询回退为筛选结果', () => {
    expect(idx.query('').length).toBe(2);
  });
});
