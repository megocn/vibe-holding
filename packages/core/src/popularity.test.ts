import { describe, expect, it } from 'vitest';
import { computeProminence, prominenceOfSignal } from './popularity.ts';
import type { Entry } from './schema/entry.ts';
import type { PopularitySignal } from './schema/popularity.ts';

const asOf = '2026-07-24';

function mustScore(n: number | undefined): number {
  expect(n).toBeTypeOf('number');
  if (typeof n !== 'number') throw new Error('expected prominence score');
  return n;
}

describe('prominenceOfSignal', () => {
  it('无信号返回 undefined', () => {
    expect(prominenceOfSignal(undefined)).toBeUndefined();
    expect(prominenceOfSignal({})).toBeUndefined();
  });

  it('星标越多分越高', () => {
    const a = mustScore(prominenceOfSignal({ github: { repo: 'a/a', stars: 100000, asOf } }));
    const b = mustScore(prominenceOfSignal({ github: { repo: 'b/b', stars: 100, asOf } }));
    expect(a).toBeGreaterThan(b);
    expect(a).toBeLessThanOrEqual(1);
  });

  it('域名排名越小（越流行）分越高', () => {
    const top = mustScore(prominenceOfSignal({ domain: { domain: 't', trancoRank: 100, asOf } }));
    const low = mustScore(
      prominenceOfSignal({ domain: { domain: 'l', trancoRank: 500000, asOf } }),
    );
    expect(top).toBeGreaterThan(low);
  });

  it('取模态最大值：弱域名信号不应拖累强 github/npm', () => {
    // MUI：强 github/npm + 一般域名；Mantine：稍弱 github/npm，无域名
    const mui: PopularitySignal = {
      github: { repo: 'mui/material-ui', stars: 98629, asOf },
      npm: { pkg: '@mui/material', downloads: 38268786, asOf },
      domain: { domain: 'mui.com', trancoRank: 56634, asOf },
    };
    const mantine: PopularitySignal = {
      github: { repo: 'mantinedev/mantine', stars: 31476, asOf },
      npm: { pkg: '@mantine/core', downloads: 8352172, asOf },
    };
    expect(mustScore(prominenceOfSignal(mui))).toBeGreaterThan(
      mustScore(prominenceOfSignal(mantine)),
    );
  });
});

describe('computeProminence', () => {
  it('仅对有信号的条目产出分', () => {
    const entries = [
      { id: 'has', category: 'c' },
      { id: 'none', category: 'c' },
    ] as Entry[];
    const pop = new Map<string, PopularitySignal>([
      ['has', { github: { repo: 'x/x', stars: 5000, asOf } }],
    ]);
    const scores = computeProminence(entries, pop);
    expect(scores.has('has')).toBe(true);
    expect(scores.has('none')).toBe(false);
  });
});
