import { describe, expect, it } from 'vitest';
import {
  pointsFromRank,
  pointsFromRanking,
  scoreLlmFamily,
  sortLlmFamilyIds,
} from './llm-family-score.ts';

describe('llm-family-score', () => {
  it('pointsFromRank：#1=100，#2≈92，平滑衰减', () => {
    expect(pointsFromRank(1)).toBe(100);
    expect(pointsFromRank(2)).toBeCloseTo(100 - 12 * Math.log(2), 5);
    expect(pointsFromRank(10)).toBeCloseTo(100 - 12 * Math.log(10), 5);
    expect(pointsFromRank(0)).toBe(0);
  });

  it('pointsFromRanking：优先 rank，tier 弱分 45', () => {
    expect(
      pointsFromRanking(
        { systemId: 'x', rank: 1, period: 'p', asOf: '2026-01-01' },
        'lmarena-text',
      ),
    ).toBe(100);
    expect(
      pointsFromRanking(
        { systemId: 'x', tier: 'Open-weight frontier', period: 'p', asOf: '2026-01-01' },
        'lmarena-text',
      ),
    ).toBe(45);
    expect(pointsFromRanking(undefined, 'lmarena-text')).toBeUndefined();
  });

  it('族内每榜取 max，不全榜时重归一化', () => {
    const strong = scoreLlmFamily({
      familyId: 'claude',
      familyName: 'Claude',
      familyMaturity: 'mature',
      lines: [
        {
          id: 'claude-opus',
          rankings: [
            { systemId: 'lmarena-text', rank: 1, period: 'p', asOf: '2026-01-01' },
            { systemId: 'lmarena-webdev', rank: 2, period: 'p', asOf: '2026-01-01' },
            { systemId: 'lmarena-agent', rank: 1, period: 'p', asOf: '2026-01-01' },
          ],
        },
        {
          id: 'claude-sonnet',
          rankings: [
            { systemId: 'lmarena-text', rank: 5, period: 'p', asOf: '2026-01-01' },
          ],
        },
      ],
    });
    // Text 取 #1 而非 #5
    expect(strong.bestTextRank).toBe(1);
    expect(strong.hasBoard).toBe(true);
    expect(strong.L).toBeGreaterThan(80);
    expect(strong.S).toBeGreaterThan(60);

    const thin = scoreLlmFamily({
      familyId: 'niche',
      familyName: 'Niche',
      lines: [
        {
          id: 'n1',
          rankings: [
            { systemId: 'lmarena-vision', rank: 1, period: 'p', asOf: '2026-01-01' },
          ],
        },
      ],
    });
    // 仅冷门榜：coverage 低 → L 被惩罚；仍有 board
    expect(thin.hasBoard).toBe(true);
    expect(thin.coverage).toBeLessThan(0.1);
    expect(thin.L).toBeLessThan(strong.L);
  });

  it('sortLlmFamilyIds：有榜按 S；无榜沉底；强族靠前', () => {
    const sorted = sortLlmFamilyIds(
      ['orphan', 'weak', 'claude', 'kimi'],
      (id) => {
        if (id === 'claude')
          return {
            familyId: 'claude',
            familyName: 'Claude',
            familyMaturity: 'mature',
            lines: [
              {
                id: 'claude-fable',
                rankings: [
                  { systemId: 'lmarena-text', rank: 1, period: 'p', asOf: '2026-01-01' },
                  { systemId: 'lmarena-webdev', rank: 2, period: 'p', asOf: '2026-01-01' },
                  { systemId: 'lmarena-agent', rank: 1, period: 'p', asOf: '2026-01-01' },
                  {
                    systemId: 'artificial-analysis-index',
                    rank: 1,
                    score: 60,
                    period: 'p',
                    asOf: '2026-01-01',
                  },
                  { systemId: 'swe-bench-pro', rank: 1, score: 80, period: 'p', asOf: '2026-01-01' },
                ],
              },
            ],
          };
        if (id === 'kimi')
          return {
            familyId: 'kimi',
            familyName: 'Kimi',
            familyMaturity: 'stable',
            lines: [
              {
                id: 'kimi-k3',
                rankings: [
                  { systemId: 'lmarena-text', rank: 10, period: 'p', asOf: '2026-01-01' },
                  { systemId: 'lmarena-webdev', rank: 1, period: 'p', asOf: '2026-01-01' },
                  { systemId: 'lmarena-agent', rank: 4, period: 'p', asOf: '2026-01-01' },
                  {
                    systemId: 'artificial-analysis-index',
                    rank: 3,
                    score: 57,
                    period: 'p',
                    asOf: '2026-01-01',
                  },
                  {
                    systemId: 'openrouter-popularity',
                    rank: 11,
                    period: 'p',
                    asOf: '2026-01-01',
                  },
                ],
              },
            ],
          };
        if (id === 'weak')
          return {
            familyId: 'weak',
            familyName: 'Weak',
            lines: [
              {
                id: 'w1',
                rankings: [
                  { systemId: 'lmarena-text', rank: 40, period: 'p', asOf: '2026-01-01' },
                ],
              },
            ],
          };
        if (id === 'orphan')
          return {
            familyId: 'orphan',
            familyName: 'Orphan',
            familyMaturity: 'mature',
            lines: [{ id: 'o1', rankings: [] }],
            prominence01: 0.9,
          };
        return undefined;
      },
    );

    expect(sorted[0]).toBe('claude');
    expect(sorted.indexOf('kimi')).toBeLessThan(sorted.indexOf('weak'));
    expect(sorted[sorted.length - 1]).toBe('orphan');
  });

  it('无榜组内：突出度优先于成熟度', () => {
    const sorted = sortLlmFamilyIds(
      ['a', 'b'],
      (id) => {
        if (id === 'a')
          return {
            familyId: 'a',
            familyName: 'A',
            familyMaturity: 'mature',
            lines: [],
            prominence01: 0.1,
          };
        return {
          familyId: 'b',
          familyName: 'B',
          familyMaturity: 'beta',
          lines: [],
          prominence01: 0.9,
        };
      },
    );
    expect(sorted).toEqual(['b', 'a']);
  });
});
