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
  /** 卡片旁 2–4 字能力提示，如「对话」「文生图」 */
  brief: z.string().min(2).max(4),
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
 *
 * previous*：上一期可比字段（活水 upsert 时写入），供首页动态展示升/跌；
 * 无历史时不填，不编造变动。
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
    /** 上一期名次（1 最优）；与 rank 对照得升降 */
    previousRank: z.number().int().positive().optional(),
    /** 上一期分值 */
    previousScore: z.number().optional(),
    /** 上一期份额 */
    previousShare: z.number().min(0).max(100).optional(),
    /** 上一期快照日 */
    previousAsOf: IsoDate.optional(),
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

function trimNum(n: number): string {
  if (Number.isInteger(n)) return String(n);
  const s = n.toFixed(2).replace(/\.?0+$/, '');
  return s === '-0' ? '0' : s;
}

/**
 * 相对上一期的通俗升降文案。无 previous* 或不可比时返回 undefined（勿编造）。
 * 名次数值越小越好：previousRank 10 → rank 8 为「升 2 名」。
 */
export function formatRankingChangePhrase(ranking: EntryRanking): string | undefined {
  if (ranking.rank != null && ranking.previousRank != null) {
    const d = ranking.previousRank - ranking.rank;
    if (d > 0) return `升 ${d} 名`;
    if (d < 0) return `跌 ${-d} 名`;
    if (ranking.score != null && ranking.previousScore != null) {
      const sd = ranking.score - ranking.previousScore;
      if (sd > 0) return `名次持平，得分 +${trimNum(sd)}`;
      if (sd < 0) return `名次持平，得分 ${trimNum(sd)}`;
    }
    if (ranking.share != null && ranking.previousShare != null) {
      const sd = ranking.share - ranking.previousShare;
      if (Math.abs(sd) >= 0.05) {
        return sd > 0
          ? `名次持平，份额 +${trimNum(sd)} 点`
          : `名次持平，份额 ${trimNum(sd)} 点`;
      }
    }
    return '较上次持平';
  }

  if (ranking.score != null && ranking.previousScore != null) {
    const d = ranking.score - ranking.previousScore;
    if (d > 0) return `升 ${trimNum(d)} 分`;
    if (d < 0) return `跌 ${trimNum(-d)} 分`;
    return '较上次持平';
  }

  if (ranking.share != null && ranking.previousShare != null) {
    const d = ranking.share - ranking.previousShare;
    if (Math.abs(d) < 0.05) return '份额较上次持平';
    return d > 0 ? `份额升 ${trimNum(d)} 点` : `份额跌 ${trimNum(-d)} 点`;
  }

  return undefined;
}

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

/** maturity 兜底排序权重（越小越靠前）。 */
const MATURITY_ORDER: Record<string, number> = {
  mature: 0,
  stable: 1,
  beta: 2,
  experimental: 3,
};
function maturityRank(m: string | undefined): number {
  return (m != null ? MATURITY_ORDER[m] : undefined) ?? 2.5;
}

/** 排序时可解析出的条目信息。 */
export interface RankingSortInfo {
  category: string;
  name: string;
  rankings: EntryRanking[];
  /** 可选：条目成熟度（无外部信号时的次级兜底） */
  maturity?: string;
}

export interface SortByRankingOptions {
  /**
   * 无权威快照时的兜底：条目的外部客观突出度分（0–1，越大越主流）。
   * 缺省则退回 maturity + 名称。见 computeProminence。
   */
  prominenceOf?: (id: string) => number | undefined;
}

/**
 * 按分类主榜排序条目 id（同分类内）；跨分类时保持相对分组由调用方处理。
 *
 * 兜底优先级（都无权威快照时）：外部客观突出度（GitHub/npm/域名流行度）→ maturity → 名称。
 * 即「有榜听榜；无榜时更主流 / 更被采用的摆前面」，名称仅作最终并列键。
 */
export function sortIdsByPrimaryRanking(
  ids: string[],
  resolve: (id: string) => RankingSortInfo | undefined,
  systems: Iterable<RankingSystem>,
  options: SortByRankingOptions = {},
): string[] {
  const primaryByCat = new Map<string, RankingSystem | undefined>();
  const primaryOf = (cat: string) => {
    if (!primaryByCat.has(cat)) primaryByCat.set(cat, primaryRankingSystem(systems, cat));
    return primaryByCat.get(cat);
  };
  // 突出度缺省视为 -1，确保「有信号」永远排在「完全无信号」之前
  const prom = (id: string) => options.prominenceOf?.(id) ?? -1;

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
    // 权威快照并列（通常是二者皆无快照）→ 外部客观突出度兜底
    const pa = prom(a);
    const pb = prom(b);
    if (pa !== pb) return pb - pa;
    // 再退回成熟度，最后名称
    const ma = maturityRank(ea.maturity);
    const mb = maturityRank(eb.maturity);
    if (ma !== mb) return ma - mb;
    return ea.name.localeCompare(eb.name, 'zh') || a.localeCompare(b);
  });
}
