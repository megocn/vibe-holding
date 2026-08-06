import { describe, expect, it } from 'vitest';
import {
  EntryRanking,
  RankingSystem,
  formatRankingChangePhrase,
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
      brief: '对话',
      categories: ['llm'],
      metric: 'mixed',
      metricUnit: 'Elo',
      url: 'https://arena.ai/leaderboard',
      description: '盲测 Elo',
      authority: 'Arena AI',
      order: 1,
    });
    expect(s.shortName).toBe('LMArena');
    expect(s.brief).toBe('对话');
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

  it('升降文案：名次越小越好，无 previous 不编造', () => {
    expect(
      formatRankingChangePhrase({
        systemId: 'x',
        rank: 8,
        previousRank: 10,
        period: 'p',
        asOf: '2026-08-06',
      }),
    ).toBe('升 2 名');
    expect(
      formatRankingChangePhrase({
        systemId: 'x',
        rank: 12,
        previousRank: 10,
        period: 'p',
        asOf: '2026-08-06',
      }),
    ).toBe('跌 2 名');
    expect(
      formatRankingChangePhrase({
        systemId: 'x',
        rank: 10,
        previousRank: 10,
        score: 1510,
        previousScore: 1500,
        period: 'p',
        asOf: '2026-08-06',
      }),
    ).toBe('名次持平，得分 +10');
    expect(
      formatRankingChangePhrase({
        systemId: 'x',
        rank: 5,
        period: 'p',
        asOf: '2026-08-06',
      }),
    ).toBeUndefined();
  });

  it('主榜排序：名次优先，无快照沉底', () => {
    const systems = [
      RankingSystem.parse({
        id: 'lmarena-text',
        name: 'Arena',
        shortName: 'LMArena',
        brief: '对话',
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
        brief: '综合',
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

  it('无权威快照时按外部突出度兜底，其次 maturity，最后名称', () => {
    const systems: never[] = []; // 该分类无主榜
    const resolve = (id: string) => {
      const map: Record<string, { name: string; maturity: string }> = {
        popular: { name: 'Z popular', maturity: 'beta' },
        mid: { name: 'A mid', maturity: 'stable' },
        none1: { name: 'Y none', maturity: 'mature' },
        none2: { name: 'B none', maturity: 'beta' },
      };
      const m = map[id];
      return m ? { category: 'x', name: m.name, rankings: [], maturity: m.maturity } : undefined;
    };
    const prom: Record<string, number> = { popular: 0.9, mid: 0.4 };
    const sorted = sortIdsByPrimaryRanking(['none1', 'mid', 'none2', 'popular'], resolve, systems, {
      prominenceOf: (id) => prom[id],
    });
    // 有突出度的按分降序在前；无信号者沉底，先 maturity(mature<beta) 再名称
    expect(sorted).toEqual(['popular', 'mid', 'none1', 'none2']);
  });
});
