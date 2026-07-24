import { z } from 'zod';
import { Id, IsoDate } from './common.ts';

/**
 * 外部客观流行度信号（由构建期抓取脚本生成，非人工编辑）。
 * 用于「无权威排行」的分类兜底排序：把更主流 / 更被采用的条目摆前面。
 * 每种来源都可缺省；勿手工编造，全部来自可复现的公开数据。
 */

/** GitHub 仓库星标快照。 */
export const GithubSignal = z.object({
  /** owner/repo */
  repo: z.string().min(1),
  stars: z.number().int().nonnegative(),
  asOf: IsoDate,
});
export type GithubSignal = z.infer<typeof GithubSignal>;

/** npm 包近一月下载量快照。 */
export const NpmSignal = z.object({
  pkg: z.string().min(1),
  /** 近 30 天下载量 */
  downloads: z.number().int().nonnegative(),
  asOf: IsoDate,
});
export type NpmSignal = z.infer<typeof NpmSignal>;

/** 站点域名流行度（Tranco 排名，越小越流行）快照。 */
export const DomainSignal = z.object({
  domain: z.string().min(1),
  /** Tranco 排名（1 最流行）；未进榜则缺省 */
  trancoRank: z.number().int().positive(),
  asOf: IsoDate,
});
export type DomainSignal = z.infer<typeof DomainSignal>;

/** 单条目的多来源流行度信号。 */
export const PopularitySignal = z.object({
  github: GithubSignal.optional(),
  npm: NpmSignal.optional(),
  domain: DomainSignal.optional(),
});
export type PopularitySignal = z.infer<typeof PopularitySignal>;

/** 抓取脚本产出的快照文件结构（content/signals/popularity.json）。 */
export const PopularitySnapshot = z.object({
  meta: z
    .object({
      generatedAt: IsoDate.optional(),
      note: z.string().optional(),
    })
    .optional(),
  entries: z.record(Id, PopularitySignal).default({}),
});
export type PopularitySnapshot = z.infer<typeof PopularitySnapshot>;
