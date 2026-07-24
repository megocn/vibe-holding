import type { Entry } from './schema/entry.ts';
import type { PopularitySignal } from './schema/popularity.ts';

/**
 * 把多来源流行度信号折算为「突出度分」（0–1，越大越主流），用于无权威榜时的兜底排序。
 *
 * 设计要点：
 * - 客观：只用外部可复现数据（GitHub 星标 / npm 下载 / 域名流行度），不掺编辑主观。
 * - 跨指标可比：各指标用**绝对 log 标度**映射到 0–1（而非同类 min–max），
 *   避免「某条目在稀疏指标上局部第一 → 被拔到 1.0」的假高分。
 * - 多信号融合：取各指标（乘模态权重后）的**最大值**，即「最强的客观采用证据」。
 *   用 max 而非加权平均，是为了避免「某条目在某轴上信号偏弱，反而被没有该轴的条目反超」
 *   （如 MUI 的文档站域名排名一般，不应因此低于无域名信号的 Mantine）。
 * - 诚实：域名流行度对同域多产品会塌缩、且是较弱的间接模态，故权重低于按产品/仓库计的
 *   GitHub/npm；共享域名已在抓取阶段剔除（见 fetch-popularity.ts）。
 */

const WEIGHTS = { github: 1, npm: 0.9, domain: 0.6 } as const;

/** GitHub 星标 → 0–1：约 1e6 星封顶（log10(stars)/6）。 */
function githubScore(stars: number): number {
  return clamp01(Math.log10(stars + 1) / 6);
}

/** npm 近月下载 → 0–1：约 1e9/月封顶（log10(dl)/9）。 */
function npmScore(downloads: number): number {
  return clamp01(Math.log10(downloads + 1) / 9);
}

/** Tranco 排名 → 0–1：rank 1 ≈ 1.0，rank 1e6 ≈ 0（(6 - log10(rank)) / 6）。 */
function domainScore(rank: number): number {
  return clamp01((6 - Math.log10(Math.max(rank, 1))) / 6);
}

function clamp01(x: number): number {
  return x < 0 ? 0 : x > 1 ? 1 : x;
}

/** 单条目突出度分（0–1）：各模态分乘权重后取最大值；无任何信号返回 undefined。 */
export function prominenceOfSignal(signal: PopularitySignal | undefined): number | undefined {
  if (!signal) return undefined;
  const candidates: number[] = [];
  if (signal.github) candidates.push(githubScore(signal.github.stars) * WEIGHTS.github);
  if (signal.npm) candidates.push(npmScore(signal.npm.downloads) * WEIGHTS.npm);
  if (signal.domain) candidates.push(domainScore(signal.domain.trancoRank) * WEIGHTS.domain);
  return candidates.length > 0 ? Math.max(...candidates) : undefined;
}

/**
 * 计算每个条目的突出度分（0–1）。仅对拥有至少一种信号的条目产出；其余不入表。
 * @param entries 全量条目（决定产出范围）
 * @param popularity 条目 id → 流行度信号
 */
export function computeProminence(
  entries: Iterable<Entry>,
  popularity: Map<string, PopularitySignal>,
): Map<string, number> {
  const out = new Map<string, number>();
  for (const e of entries) {
    const score = prominenceOfSignal(popularity.get(e.id));
    if (score != null) out.set(e.id, score);
  }
  return out;
}
