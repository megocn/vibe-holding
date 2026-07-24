import { describe, expect, it } from 'vitest';
import {
  EntryRanking,
  RankingSystem,
  formatRankingPrimary,
  formatRankingScore,
  primaryRankingSystem,
  rankingSortKey,
  sortIdsByPrimaryRanking,
} from './ranking.ts';

describe('RankingSystem / EntryRanking', () => {
  it('解析权威体系', () => {
    const s = RankingSystem.parse({
      id: 'lmarena-text',
      name: 'Arena AI Text',
      shortName: 'LMArena',
      categories: ['llm'],
      metric: 'mixed',
      metricUnit: 'Elo',
      url: 'https://arena.ai/leaderboard',
      description: '盲测 Elo',
      authority: 'Arena AI',
      order: 1,
    });
    expect(s.shortName).toBe('LMArena');
  });

  it('条目排名至少一项指标', () => {
    expect(() =>
      EntryRanking.parse({
        systemId: 'lmarena-text',
        period: '2026-07',
        asOf: '2026-07-20',
      }),
    ).toThrow();
    const r = EntryRanking.parse({
      systemId: 'lmarena-text',
      rank: 1,
      score: 1512,
      period: '2026-07',
      asOf: '2026-07-20',
    });
    expect(formatRankingPrimary(r, { shortName: 'LMArena', metricUnit: 'Elo' })).toBe(
      '#1 · 1512 Elo',
    );
    expect(formatRankingScore(r, { metricUnit: 'Elo' })).toBe('1512 Elo');
  });

  it('主榜排序：名次优先，无快照沉底', () => {
    const systems = [
      RankingSystem.parse({
        id: 'lmarena-text',
        name: 'Arena',
        shortName: 'LMArena',
        categories: ['llm'],
        metric: 'mixed',
        url: 'https://arena.ai/leaderboard',
        description: 'x',
        authority: 'Arena',
        order: 1,
      }),
      RankingSystem.parse({
        id: 'aa',
        name: 'AA',
        shortName: 'AA',
        categories: ['llm'],
        metric: 'score',
        url: 'https://example.com',
        description: 'x',
        authority: 'AA',
        order: 2,
      }),
    ];
    expect(primaryRankingSystem(systems, 'llm')?.id).toBe('lmarena-text');
    expect(rankingSortKey({ systemId: 'x', rank: 1, period: 'p', asOf: '2026-01-01' })).toBe(1);
    expect(rankingSortKey({ systemId: 'x', rank: 4, period: 'p', asOf: '2026-01-01' })).toBe(4);

    const sorted = sortIdsByPrimaryRanking(
      ['b', 'a', 'c'],
      (id) => {
        if (id === 'a')
          return {
            category: 'llm',
            name: 'A',
            rankings: [{ systemId: 'lmarena-text', rank: 4, period: 'p', asOf: '2026-01-01' }],
          };
        if (id === 'b')
          return {
            category: 'llm',
            name: 'B',
            rankings: [{ systemId: 'lmarena-text', rank: 1, period: 'p', asOf: '2026-01-01' }],
          };
        return { category: 'llm', name: 'C', rankings: [] };
      },
      systems,
    );
    expect(sorted).toEqual(['b', 'a', 'c']);
  });
});
