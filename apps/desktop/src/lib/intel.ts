import {
  formatRankingPrimary,
  type Entry,
  type EntryRanking,
  type EntryUpdate,
  type Id,
  type RankingSystem,
  type UpdateType,
} from '@vh/core';

export const UPDATE_TYPE_META: Record<UpdateType, { label: string; icon: string; color: string }> =
  {
    release: { label: '版本', icon: 'Tag', color: 'var(--pigment-seal)' },
    feature: { label: '功能', icon: 'Sparkle', color: 'var(--pigment-primary)' },
    pricing: { label: '定价', icon: 'CurrencyDollar', color: 'var(--pigment-warning)' },
    policy: { label: '政策', icon: 'Scales', color: 'var(--pigment-info)' },
    deprecation: { label: '弃用', icon: 'Warning', color: 'var(--pigment-danger)' },
    other: { label: '其他', icon: 'Info', color: 'var(--ink-3)' },
  };

export const STALE_DAYS = 180;

export interface FeedItem {
  entryId: Id;
  entryName: string;
  update: EntryUpdate;
}

export interface ActivityItem {
  entryId: Id;
  entryName: string;
  date: string;
  kind: 'update' | 'ranking';
  label: string;
  icon: string;
  summary: string;
  key: string;
}

/** 从条目集合聚合更新，按日期倒序。 */
export function collectUpdates(
  entries: Iterable<Entry>,
  opts?: { onlyIds?: Set<Id>; limit?: number },
): FeedItem[] {
  const items: FeedItem[] = [];
  for (const e of entries) {
    if (opts?.onlyIds && !opts.onlyIds.has(e.id)) continue;
    for (const u of e.updates) {
      items.push({ entryId: e.id, entryName: e.name, update: u });
    }
  }
  items.sort((a, b) => b.update.date.localeCompare(a.update.date));
  if (opts?.limit != null) return items.slice(0, opts.limit);
  return items;
}

/**
 * 首页动态流：业务事件 + 排行快照。
 * 同一条目同一天的多个榜单合并成一条，避免排行日更淹没版本/定价事件。
 */
export function collectActivities(
  entries: Iterable<Entry>,
  rankingSystems: ReadonlyMap<Id, RankingSystem>,
  opts?: { onlyIds?: Set<Id>; limit?: number },
): ActivityItem[] {
  const items: ActivityItem[] = [];

  for (const entry of entries) {
    if (opts?.onlyIds && !opts.onlyIds.has(entry.id)) continue;

    for (const update of entry.updates) {
      const meta = UPDATE_TYPE_META[update.type];
      items.push({
        entryId: entry.id,
        entryName: entry.name,
        date: update.date,
        kind: 'update',
        label: meta.label,
        icon: meta.icon,
        summary: update.summary,
        key: `update-${entry.id}-${update.date}-${update.summary}`,
      });
    }

    const rankingsByDate = new Map<string, EntryRanking[]>();
    for (const ranking of entry.rankings) {
      const rows = rankingsByDate.get(ranking.asOf) ?? [];
      rows.push(ranking);
      rankingsByDate.set(ranking.asOf, rows);
    }

    for (const [date, rankings] of rankingsByDate) {
      rankings.sort((a, b) => {
        const oa = rankingSystems.get(a.systemId)?.order ?? 99;
        const ob = rankingSystems.get(b.systemId)?.order ?? 99;
        return oa - ob || a.systemId.localeCompare(b.systemId);
      });
      const preview = rankings.slice(0, 2).map((ranking) => {
        const system = rankingSystems.get(ranking.systemId);
        const systemName = system?.shortName ?? ranking.systemId;
        return `${systemName} ${formatRankingPrimary(ranking, system)}`;
      });
      if (rankings.length > preview.length) preview.push(`另 ${rankings.length - preview.length} 榜`);

      items.push({
        entryId: entry.id,
        entryName: entry.name,
        date,
        kind: 'ranking',
        label: '排行',
        icon: 'TrendUp',
        summary: preview.join(' · '),
        key: `ranking-${entry.id}-${date}`,
      });
    }
  }

  items.sort(
    (a, b) =>
      b.date.localeCompare(a.date) ||
      (a.kind === b.kind ? a.entryName.localeCompare(b.entryName) : a.kind === 'update' ? -1 : 1),
  );
  if (opts?.limit != null) return items.slice(0, opts.limit);
  return items;
}

export function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function daysSince(iso: string, now = Date.now()): number {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return 0;
  return Math.floor((now - t) / (24 * 60 * 60 * 1000));
}

/** 相对天数文案：今天 / N天前 */
export function formatReviewedRelative(iso: string, now = Date.now()): string {
  const days = daysSince(iso, now);
  if (days <= 0) return '今天';
  return `${days}天前`;
}

/** 详情用：复核 YYYY-MM-DD · N 天前 */
export function formatReviewedLabel(iso: string, now = Date.now()): string {
  return `复核 ${iso} · ${formatReviewedRelative(iso, now)}`;
}

export function isStale(lastReviewed: string, threshold = STALE_DAYS): boolean {
  return daysSince(lastReviewed) > threshold;
}

export function collectStaleEntries(entries: Iterable<Entry>, threshold = STALE_DAYS): Entry[] {
  return [...entries]
    .filter((e) => isStale(e.lastReviewed, threshold))
    .sort((a, b) => a.lastReviewed.localeCompare(b.lastReviewed));
}
