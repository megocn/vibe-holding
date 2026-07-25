import type { Entry, RankingSystem } from '@vh/core';
import { collectUpdates } from './intel.ts';

export interface CatalogProvenance {
  entryCount: number;
  rankingSystemCount: number;
  /** 去重后的公开权威短名，已按 order 排序 */
  authorityLabels: string[];
  /** 近 30 日 updates 事件数（已发生，不含未来预告） */
  updatesLast30Days: number;
  /** 库内最新一条已发生的 update 事件日期 */
  latestUpdateDate: string | null;
  /** 条目 lastReviewed 最大值：信息最后审阅/写入日 */
  lastReviewedDate: string | null;
}

const INTERNAL_AUTH_RE = /vibeholding|editorial/i;

function localDateIso(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** 首页「信息来源」公示用：条目规模 + 公开权威名 + 近期更新量。 */
export function buildCatalogProvenance(
  entries: Iterable<Entry>,
  rankingSystems: Iterable<RankingSystem>,
  now = new Date(),
): CatalogProvenance {
  const entryList = [...entries];
  const systems = [...rankingSystems].sort((a, b) => (a.order ?? 99) - (b.order ?? 99));

  const seen = new Set<string>();
  const authorityLabels: string[] = [];
  for (const s of systems) {
    if (INTERNAL_AUTH_RE.test(s.authority) || INTERNAL_AUTH_RE.test(s.shortName)) continue;
    const label = s.shortName.trim();
    if (!label || seen.has(label)) continue;
    seen.add(label);
    authorityLabels.push(label);
  }

  const todayIso = localDateIso(now);
  const cut = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30);
  const cutIso = localDateIso(cut);

  const updates = collectUpdates(entryList);
  // 预告类事件（如「将于某日 EOL」）日期可能在未来，不算「已发生」
  const occurred = updates.filter((u) => u.update.date <= todayIso);
  const updatesLast30Days = occurred.filter((u) => u.update.date >= cutIso).length;
  const latestUpdateDate = occurred[0]?.update.date ?? null;

  let lastReviewedDate: string | null = null;
  for (const e of entryList) {
    const d = e.lastReviewed;
    if (!d || d > todayIso) continue;
    if (!lastReviewedDate || d > lastReviewedDate) lastReviewedDate = d;
  }

  return {
    entryCount: entryList.length,
    rankingSystemCount: systems.length,
    authorityLabels,
    updatesLast30Days,
    latestUpdateDate,
    lastReviewedDate,
  };
}
