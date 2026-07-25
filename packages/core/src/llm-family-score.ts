import { lineIdsOfFamily } from './schema/meta.ts';
import type { EntryRanking } from './schema/ranking.ts';
import { entryRankingForSystem } from './schema/ranking.ts';
import type { ContentBundle } from './types.ts';

/**
 * B 类产品族综合分（榜单优先）。
 * 详设：docs-internal/modules/01-知识库.md §2.3
 */

/** 综合分外层权重（合计 1）。 */
export const FAMILY_SCORE_BLEND = {
  L: 0.82,
  U: 0.1,
  P: 0.05,
  M: 0.03,
} as const;

/** 榜单 L 内各体系权重（合计 1；OpenRouter 不进 L）。 */
export const FAMILY_LEADERBOARD_WEIGHTS: Readonly<Record<string, number>> = {
  'lmarena-text': 0.3,
  'lmarena-webdev': 0.2,
  'lmarena-agent': 0.16,
  'artificial-analysis-index': 0.14,
  'swe-bench-pro': 0.12,
  // 其余 Arena 合计 0.08，均分
  'lmarena-vision': 0.08 / 3,
  'lmarena-document': 0.08 / 3,
  'lmarena-search': 0.08 / 3,
};

const OPENROUTER_SYSTEM = 'openrouter-popularity';
const TIER_ONLY_POINTS = 45;
const TIE_EPS = 0.5;

/** 无名次时 score → 0–100 的经验上下界（可被快照池覆盖）。 */
const DEFAULT_SCORE_BOUNDS: Readonly<Record<string, { lo: number; hi: number }>> = {
  'lmarena-text': { lo: 1200, hi: 1520 },
  'lmarena-webdev': { lo: 1400, hi: 1700 },
  'lmarena-vision': { lo: 1180, hi: 1350 },
  'lmarena-document': { lo: 1350, hi: 1550 },
  'lmarena-search': { lo: 1150, hi: 1280 },
  'artificial-analysis-index': { lo: 20, hi: 65 },
  'swe-bench-pro': { lo: 40, hi: 85 },
};

const MATURITY_POINTS: Record<string, number> = {
  mature: 100,
  stable: 75,
  beta: 40,
  experimental: 15,
};

export interface LlmFamilyScoreBreakdown {
  familyId: string;
  /** 综合分 S（0–100 量级） */
  S: number;
  L: number;
  U: number;
  P: number;
  M: number;
  /** 是否至少有一条用于 L/U 的权威快照 */
  hasBoard: boolean;
  /** 族内 Text / WebDev 最佳名次（并列用；越小越好；无则 ∞） */
  bestTextRank: number;
  bestWebdevRank: number;
  coverage: number;
}

function clamp01(x: number): number {
  return x < 0 ? 0 : x > 1 ? 1 : x;
}

/** rank → 0–100：points = max(0, 100 − 12·ln(rank)) */
export function pointsFromRank(rank: number): number {
  if (!Number.isFinite(rank) || rank < 1) return 0;
  return Math.max(0, 100 - 12 * Math.log(rank));
}

function mapScoreToPoints(score: number, lo: number, hi: number): number {
  if (hi <= lo) return 50;
  return clamp01((score - lo) / (hi - lo)) * 100;
}

/**
 * 单条快照 → 0–100。
 * 优先 rank；否则 score（用 bounds）；再否则 tier 弱分 45；share 直接作分（0–100）。
 */
export function pointsFromRanking(
  ranking: EntryRanking | undefined,
  systemId: string,
  scoreBounds?: ReadonlyMap<string, { lo: number; hi: number }>,
): number | undefined {
  if (!ranking) return undefined;
  if (ranking.rank != null) return pointsFromRank(ranking.rank);
  if (ranking.score != null) {
    const b =
      scoreBounds?.get(systemId) ??
      DEFAULT_SCORE_BOUNDS[systemId] ??
      ({ lo: ranking.score * 0.7, hi: ranking.score * 1.05 } as const);
    return mapScoreToPoints(ranking.score, b.lo, b.hi);
  }
  if (ranking.share != null) return clamp01(ranking.share / 100) * 100;
  if (ranking.tier) return TIER_ONLY_POINTS;
  if (ranking.scoreLabel) return TIER_ONLY_POINTS;
  return undefined;
}

function maturityPoints(m: string | undefined): number {
  if (m != null && Object.prototype.hasOwnProperty.call(MATURITY_POINTS, m)) {
    return MATURITY_POINTS[m]!;
  }
  return 75; // stable 缺省
}

function bestRankAmong(
  lines: { rankings: EntryRanking[] }[],
  systemId: string,
): number {
  let best = Number.POSITIVE_INFINITY;
  for (const line of lines) {
    const r = entryRankingForSystem(line.rankings, systemId)?.rank;
    if (r != null && r < best) best = r;
  }
  return best;
}

/** 从一批档位快照推导各体系 score 上下界（有数据时覆盖默认）。 */
export function buildScoreBoundsFromLines(
  lines: Iterable<{ rankings: EntryRanking[] }>,
): Map<string, { lo: number; hi: number }> {
  const bySys = new Map<string, number[]>();
  for (const line of lines) {
    for (const r of line.rankings) {
      if (r.score == null) continue;
      const arr = bySys.get(r.systemId) ?? [];
      arr.push(r.score);
      bySys.set(r.systemId, arr);
    }
  }
  const out = new Map<string, { lo: number; hi: number }>();
  for (const [id, def] of Object.entries(DEFAULT_SCORE_BOUNDS)) {
    out.set(id, { ...def });
  }
  for (const [id, scores] of bySys) {
    if (scores.length < 2) continue;
    const lo = Math.min(...scores);
    const hi = Math.max(...scores);
    if (hi > lo) out.set(id, { lo, hi });
  }
  return out;
}

export interface ScoreLlmFamilyInput {
  familyId: string;
  familyName: string;
  familyMaturity?: string;
  lines: { id: string; rankings: EntryRanking[]; maturity?: string }[];
  /** 族与下属档的 prominence（0–1）取 max 后 ×100 */
  prominence01?: number;
  scoreBounds?: ReadonlyMap<string, { lo: number; hi: number }>;
}

/** 计算单个产品族综合分。 */
export function scoreLlmFamily(input: ScoreLlmFamilyInput): LlmFamilyScoreBreakdown {
  const { lines, scoreBounds } = input;
  const weightEntries = Object.entries(FAMILY_LEADERBOARD_WEIGHTS);
  const totalW = weightEntries.reduce((s, [, w]) => s + w, 0);

  let weighted = 0;
  let presentW = 0;
  let hasAnyLU = false;

  for (const [systemId, w] of weightEntries) {
    let best: number | undefined;
    for (const line of lines) {
      const snap = entryRankingForSystem(line.rankings, systemId);
      const pts = pointsFromRanking(snap, systemId, scoreBounds);
      if (pts == null) continue;
      hasAnyLU = true;
      best = best == null ? pts : Math.max(best, pts);
    }
    if (best == null) continue;
    weighted += w * best;
    presentW += w;
  }

  const coverage = totalW > 0 ? presentW / totalW : 0;
  const Lraw = presentW > 0 ? weighted / presentW : 0;
  const L = Lraw * (0.85 + 0.15 * coverage);

  let U = 0;
  for (const line of lines) {
    const snap = entryRankingForSystem(line.rankings, OPENROUTER_SYSTEM);
    const pts = pointsFromRanking(snap, OPENROUTER_SYSTEM, scoreBounds);
    if (pts == null) continue;
    hasAnyLU = true;
    U = Math.max(U, pts);
  }

  const P = clamp01(input.prominence01 ?? 0) * 100;
  const M = maturityPoints(input.familyMaturity);

  const S =
    FAMILY_SCORE_BLEND.L * L +
    FAMILY_SCORE_BLEND.U * U +
    FAMILY_SCORE_BLEND.P * P +
    FAMILY_SCORE_BLEND.M * M;

  return {
    familyId: input.familyId,
    S,
    L,
    U,
    P,
    M,
    hasBoard: hasAnyLU,
    bestTextRank: bestRankAmong(lines, 'lmarena-text'),
    bestWebdevRank: bestRankAmong(lines, 'lmarena-webdev'),
    coverage,
  };
}

export interface SortLlmFamiliesOptions {
  /** 条目 id → 突出度 0–1 */
  prominenceOf?: (id: string) => number | undefined;
}

/**
 * 按综合分降序排列产品族 id。
 * 无榜沉底；|ΔS|<0.5 时比 Text 名次 → WebDev 名次 → 名称。
 */
export function sortLlmFamilyIds(
  familyIds: string[],
  resolve: (id: string) => ScoreLlmFamilyInput | undefined,
  options: SortLlmFamiliesOptions = {},
): string[] {
  const inputs = familyIds
    .map((id) => resolve(id))
    .filter((x): x is ScoreLlmFamilyInput => x != null);

  const allLines = inputs.flatMap((i) => i.lines);
  const bounds = buildScoreBoundsFromLines(allLines);

  const scored = new Map<string, LlmFamilyScoreBreakdown & { name: string }>();
  for (const input of inputs) {
    const promIds = [input.familyId, ...input.lines.map((l) => l.id)];
    let prom = input.prominence01;
    if (prom == null && options.prominenceOf) {
      let best = 0;
      let any = false;
      for (const id of promIds) {
        const p = options.prominenceOf(id);
        if (p != null) {
          any = true;
          best = Math.max(best, p);
        }
      }
      prom = any ? best : undefined;
    }
    const breakdown = scoreLlmFamily({ ...input, prominence01: prom, scoreBounds: bounds });
    scored.set(input.familyId, { ...breakdown, name: input.familyName });
  }

  return [...familyIds].sort((a, b) => {
    const sa = scored.get(a);
    const sb = scored.get(b);
    if (!sa && !sb) return a.localeCompare(b);
    if (!sa) return 1;
    if (!sb) return -1;

    if (sa.hasBoard !== sb.hasBoard) return sa.hasBoard ? -1 : 1;

    if (!sa.hasBoard) {
      if (sa.P !== sb.P) return sb.P - sa.P;
      if (sa.M !== sb.M) return sb.M - sa.M;
      return sa.name.localeCompare(sb.name, 'zh') || a.localeCompare(b);
    }

    if (Math.abs(sa.S - sb.S) >= TIE_EPS) return sb.S - sa.S;
    if (sa.bestTextRank !== sb.bestTextRank) return sa.bestTextRank - sb.bestTextRank;
    if (sa.bestWebdevRank !== sb.bestWebdevRank) return sa.bestWebdevRank - sb.bestWebdevRank;
    return sa.name.localeCompare(sb.name, 'zh') || a.localeCompare(b);
  });
}

/** 从 ContentBundle 解析族输入并按综合分排序族 id。 */
export function sortLlmFamiliesFromBundle(
  bundle: ContentBundle,
  options: SortLlmFamiliesOptions = {},
): string[] {
  const families = [...bundle.entries.values()].filter((e) => e.category === 'llm-family');
  const ids = families.map((f) => f.id);

  return sortLlmFamilyIds(
    ids,
    (id) => {
      const fam = bundle.entries.get(id);
      if (!fam || fam.category !== 'llm-family') return undefined;
      const lineIds = lineIdsOfFamily(bundle.edges, id).filter((lid) => bundle.entries.has(lid));
      const lines = lineIds.map((lid) => {
        const e = bundle.entries.get(lid)!;
        return { id: lid, rankings: e.rankings, maturity: e.maturity };
      });
      return {
        familyId: id,
        familyName: fam.name,
        familyMaturity: fam.maturity,
        lines,
      };
    },
    options,
  );
}
