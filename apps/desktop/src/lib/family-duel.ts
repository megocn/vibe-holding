import type { ContentBundle, Id } from '@vh/core';
import {
  buildScoreBoundsFromLines,
  computeProminence,
  entryRankingForSystem,
  lineIdsOfFamily,
  scoreLlmFamily,
  sortLlmFamiliesFromBundle,
} from '@vh/core';
import duelArtMeta from '../generated/family-duel.json';

/** 首页对垒战报展示的关键榜（族内旗舰 max）。 */
const DUEL_METRICS = [
  { systemId: 'lmarena-text', label: 'Text' },
  { systemId: 'lmarena-webdev', label: 'WebDev' },
  { systemId: 'lmarena-agent', label: 'Agent' },
  { systemId: 'artificial-analysis-index', label: 'AA' },
] as const;

export interface FamilyDuelMetric {
  systemId: string;
  label: string;
  rank?: number;
  scoreLabel?: string;
  lineName?: string;
}

export interface FamilyDuelFighter {
  id: Id;
  name: string;
  place: 1 | 2;
  /** 综合分 S，一位小数 */
  scoreS: number;
  oneLiner?: string;
  metrics: FamilyDuelMetric[];
}

export interface FamilyDuelBoard {
  week: string;
  weekLabel: string;
  first: FamilyDuelFighter;
  second: FamilyDuelFighter;
  imageSrc: string;
  /** 插画是否对应当前双强（错配时仍展示现算战绩） */
  artMatches: boolean;
  artWeek: string;
}

export interface FamilyDuelArtMeta {
  week: string;
  firstId: string;
  secondId: string;
  image: string;
  generatedAt: string;
  note?: string;
}

/** ISO 周键，如 2026-W30（周一为一周之始）。 */
export function isoWeekKey(date = new Date()): string {
  const t = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const day = t.getUTCDay() || 7;
  t.setUTCDate(t.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((t.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return `${t.getUTCFullYear()}-W${String(week).padStart(2, '0')}`;
}

function weekDisplayLabel(week: string): string {
  const m = /^(\d{4})-W(\d{2})$/.exec(week);
  if (!m) return week;
  return `${m[1]} · 第 ${Number(m[2])} 周`;
}

function bestMetricAmongLines(
  bundle: ContentBundle,
  lineIds: Id[],
  systemId: string,
): FamilyDuelMetric | null {
  let best:
    | {
        rank: number;
        score?: number;
        lineName: string;
      }
    | undefined;

  for (const lid of lineIds) {
    const line = bundle.entries.get(lid);
    if (!line) continue;
    const snap = entryRankingForSystem(line.rankings, systemId);
    if (!snap || snap.rank == null) continue;
    if (!best || snap.rank < best.rank) {
      best = { rank: snap.rank, score: snap.score, lineName: line.name };
    }
  }
  if (!best) return null;

  const sys = bundle.rankingSystems.get(systemId);
  const def = DUEL_METRICS.find((d) => d.systemId === systemId);
  return {
    systemId,
    label: def?.label ?? sys?.brief ?? sys?.shortName ?? systemId,
    rank: best.rank,
    scoreLabel:
      best.score != null
        ? sys?.metricUnit
          ? `${best.score} ${sys.metricUnit}`
          : String(best.score)
        : undefined,
    lineName: best.lineName,
  };
}

function buildFighter(
  bundle: ContentBundle,
  familyId: Id,
  place: 1 | 2,
  prominence: Map<string, number>,
): FamilyDuelFighter | null {
  const fam = bundle.entries.get(familyId);
  if (!fam || fam.category !== 'llm-family') return null;

  const lineIds = lineIdsOfFamily(bundle.edges, familyId).filter((id) =>
    bundle.entries.has(id),
  );
  const lines = lineIds.map((lid) => {
    const e = bundle.entries.get(lid)!;
    return { id: lid, rankings: e.rankings, maturity: e.maturity };
  });
  const allLines = [...bundle.entries.values()]
    .filter((e) => e.category === 'llm-line')
    .map((e) => ({ rankings: e.rankings }));
  const bounds = buildScoreBoundsFromLines(allLines);

  let prom = 0;
  let anyProm = false;
  for (const pid of [familyId, ...lineIds]) {
    const p = prominence.get(pid);
    if (p != null) {
      anyProm = true;
      prom = Math.max(prom, p);
    }
  }

  const breakdown = scoreLlmFamily({
    familyId,
    familyName: fam.name,
    familyMaturity: fam.maturity,
    lines,
    prominence01: anyProm ? prom : undefined,
    scoreBounds: bounds,
  });

  const metrics: FamilyDuelMetric[] = [];
  for (const def of DUEL_METRICS) {
    const m = bestMetricAmongLines(bundle, lineIds, def.systemId);
    if (m) metrics.push(m);
  }

  return {
    id: familyId,
    name: fam.name,
    place,
    scoreS: Math.round(breakdown.S * 10) / 10,
    oneLiner: fam.oneLiner,
    metrics,
  };
}

/** 取「大语言模型与多模态」综合分前二族，组装首页对垒板。 */
export function buildFamilyDuelBoard(bundle: ContentBundle): FamilyDuelBoard | null {
  const prominence = computeProminence(bundle.entries.values(), bundle.popularity);
  const order = sortLlmFamiliesFromBundle(bundle, {
    prominenceOf: (id) => prominence.get(id),
  });
  if (order.length < 2) return null;

  const firstId = order[0] as Id;
  const secondId = order[1] as Id;
  const first = buildFighter(bundle, firstId, 1, prominence);
  const second = buildFighter(bundle, secondId, 2, prominence);
  if (!first || !second) return null;

  const art = duelArtMeta as FamilyDuelArtMeta;
  const week = isoWeekKey();
  const artMatches =
    art.firstId === firstId && art.secondId === secondId && art.week === week;

  return {
    week,
    weekLabel: weekDisplayLabel(week),
    first,
    second,
    imageSrc: art.image || '/illustrations/family-duel.webp',
    artMatches,
    artWeek: art.week,
  };
}
