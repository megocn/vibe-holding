import type { Entry, EntryUpdate, Id, UpdateType } from '@vh/core';

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
