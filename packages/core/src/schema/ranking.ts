import { z } from 'zod';
import { Id, IsoDate } from './common.ts';

/**
 * 权威排行体系的度量形态。
 * - rank：名次（1 为最优）
 * - score：连续分值（Elo / 指数 / 下载量等）
 * - tier：象限/档位（Leader / Challenger 等）
 * - share：采用率/份额百分比
 * - mixed：同时可能有 rank + score / tier
 */
export const RankingMetric = z.enum(['rank', 'score', 'tier', 'share', 'mixed']);
export type RankingMetric = z.infer<typeof RankingMetric>;

/** 分类级权威排行/标准体系（市面公认，每类通常 1–2 个）。 */
export const RankingSystem = z.object({
  id: Id,
  name: z.string().min(1),
  shortName: z.string().min(1).max(32),
  /** 适用分类 id（对应 categories.json） */
  categories: z.array(Id).min(1),
  metric: RankingMetric,
  /** 分值单位文案，如 Elo、%、pts */
  metricUnit: z.string().max(24).optional(),
  url: z.string().url(),
  description: z.string().min(1),
  /** 运营方 / 权威来源，如 Arena AI、solidIT、Gartner */
  authority: z.string().min(1),
  /** 更新节奏：weekly / monthly / annual / ad-hoc */
  updateCadence: z.string().max(24).optional(),
  /** 展示排序（同分类内，越小越靠前） */
  order: z.number().int().default(1),
});
export type RankingSystem = z.infer<typeof RankingSystem>;

/**
 * 条目在某套排行体系中的快照。
 * rank / score / tier / share 至少填一项；asOf 为快照日期。
 */
export const EntryRanking = z
  .object({
    systemId: Id,
    /** 名次，1 = 最优 */
    rank: z.number().int().positive().optional(),
    /** 原始分值（Elo、指数分、下载量等） */
    score: z.number().optional(),
    /** 分值展示文案；缺省时由 score + 体系 metricUnit 拼 */
    scoreLabel: z.string().max(48).optional(),
    /** 档位/象限，如 Leader、Admired #1 */
    tier: z.string().max(40).optional(),
    /** 采用率/份额（0–100） */
    share: z.number().min(0).max(100).optional(),
    /** 榜单期次，如 2026-07、2025 Survey */
    period: z.string().min(1).max(40),
    sourceUrl: z.string().url().optional(),
    note: z.string().max(200).optional(),
    asOf: IsoDate,
  })
  .refine(
    (r) =>
      r.rank != null ||
      r.score != null ||
      r.tier != null ||
      r.share != null ||
      Boolean(r.scoreLabel),
    { message: 'rankings 项须至少提供 rank / score / scoreLabel / tier / share 之一' },
  );
export type EntryRanking = z.infer<typeof EntryRanking>;

/** 将分值格式化为展示串。 */
export function formatRankingScore(
  ranking: EntryRanking,
  system?: Pick<RankingSystem, 'metricUnit'> | null,
): string | undefined {
  if (ranking.scoreLabel) return ranking.scoreLabel;
  if (ranking.score == null) return undefined;
  const unit = system?.metricUnit;
  if (!unit) return String(ranking.score);
  if (unit === '%') return `${ranking.score}%`;
  return `${ranking.score} ${unit}`;
}

/** 单条排名的主展示文案（名次优先，其次档位/份额/分值）。 */
export function formatRankingPrimary(
  ranking: EntryRanking,
  system?: Pick<RankingSystem, 'metricUnit' | 'shortName'> | null,
): string {
  const parts: string[] = [];
  if (ranking.rank != null) parts.push(`#${ranking.rank}`);
  if (ranking.tier) parts.push(ranking.tier);
  if (ranking.share != null) parts.push(`${ranking.share}%`);
  const score = formatRankingScore(ranking, system);
  if (score && ranking.rank == null && ranking.share == null) parts.push(score);
  else if (score && ranking.rank != null) parts.push(score);
  return parts.join(' · ') || system?.shortName || '—';
}

/** 分类下最权威（order 最小）的排行体系。 */
export function primaryRankingSystem(
  systems: Iterable<RankingSystem>,
  categoryId: string,
): RankingSystem | undefined {
  let best: RankingSystem | undefined;
  for (const s of systems) {
    if (!s.categories.includes(categoryId)) continue;
    if (
      !best ||
      s.order < best.order ||
      (s.order === best.order && s.id.localeCompare(best.id) < 0)
    ) {
      best = s;
    }
  }
  return best;
}

/**
 * 排序键：越小越靠前。
 * 优先名次（1 最优）；无名字时用 −score / −share（分值/份额越高越前）；
 * 仅有 tier 时按常见档位；完全无快照则排最后。
 */
export function rankingSortKey(ranking: EntryRanking | undefined): number {
  if (!ranking) return Number.POSITIVE_INFINITY;
  if (ranking.rank != null) return ranking.rank;
  if (ranking.score != null) return -ranking.score;
  if (ranking.share != null) return -ranking.share;
  if (ranking.tier) {
    const t = ranking.tier.toLowerCase();
    if (t.includes('leader') || t.includes('category leader') || t.includes('#1')) return 1000;
    if (t.includes('top') || t.includes('frontier') || t.includes('admired')) return 1100;
    if (t.includes('challenger') || t.includes('rising') || t.includes('competitive')) return 1200;
    if (t.includes('niche') || t.includes('legacy') || t.includes('prior')) return 1400;
    return 1300;
  }
  if (ranking.scoreLabel) return 1500;
  return Number.POSITIVE_INFINITY;
}

/** 取条目在指定体系上的快照。 */
export function entryRankingForSystem(
  rankings: EntryRanking[],
  systemId: string,
): EntryRanking | undefined {
  return rankings.find((r) => r.systemId === systemId);
}

/**
 * 按分类主榜排序条目 id（同分类内）；跨分类时保持相对分组由调用方处理。
 * 无主榜或无快照的条目沉底，再按名称。
 */
export function sortIdsByPrimaryRanking(
  ids: string[],
  resolve: (id: string) => { category: string; name: string; rankings: EntryRanking[] } | undefined,
  systems: Iterable<RankingSystem>,
): string[] {
  const primaryByCat = new Map<string, RankingSystem | undefined>();
  const primaryOf = (cat: string) => {
    if (!primaryByCat.has(cat)) primaryByCat.set(cat, primaryRankingSystem(systems, cat));
    return primaryByCat.get(cat);
  };

  return [...ids].sort((a, b) => {
    const ea = resolve(a);
    const eb = resolve(b);
    if (!ea && !eb) return a.localeCompare(b);
    if (!ea) return 1;
    if (!eb) return -1;
    const sa = primaryOf(ea.category);
    const sb = primaryOf(eb.category);
    const ra = sa ? entryRankingForSystem(ea.rankings, sa.id) : undefined;
    const rb = sb ? entryRankingForSystem(eb.rankings, sb.id) : undefined;
    const ka = rankingSortKey(ra);
    const kb = rankingSortKey(rb);
    if (ka !== kb) return ka - kb;
    return ea.name.localeCompare(eb.name, 'zh') || a.localeCompare(b);
  });
}
