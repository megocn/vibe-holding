import { type FeedSource, feedItemToUpdate, parseFeedXml } from '@vh/core';
import feedsJson from '../../../../content/feeds.json';
import type { IntelDraft } from './intel-drafts.ts';
import { addIntelDraft } from './intel-drafts.ts';

export type { FeedSource };

export const INTEL_FEEDS: FeedSource[] = feedsJson as FeedSource[];

export interface ScrapeFeedResult {
  entryId: string;
  label: string;
  url: string;
  ok: boolean;
  added: number;
  error?: string;
  itemsSeen: number;
}

async function fetchFeedText(url: string): Promise<string> {
  const headers = {
    Accept: 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*',
  };

  try {
    const direct = await fetch(url, { headers, mode: 'cors' });
    if (direct.ok) {
      const text = await direct.text();
      if (text.trim().startsWith('<') || text.includes('<rss') || text.includes('<feed')) {
        return text;
      }
    }
  } catch {
    // fall through to proxy
  }

  const proxy = await fetch(`/__vh_fetch?url=${encodeURIComponent(url)}`);
  if (!proxy.ok) {
    const msg = await proxy.text().catch(() => proxy.statusText);
    throw new Error(`抓取失败 (${proxy.status}): ${msg.slice(0, 120)}`);
  }
  return proxy.text();
}

/**
 * 抓取配置的 RSS/Atom，写入待确认草稿（去重 pending / 同 summary）。
 */
export async function scrapeFeedsToDrafts(
  drafts: IntelDraft[],
  opts?: {
    feeds?: FeedSource[];
    entryIds?: Set<string>;
    /** 每个源最多转草稿条数 */
    perFeedLimit?: number;
    onlyEntryId?: string;
  },
): Promise<{ drafts: IntelDraft[]; results: ScrapeFeedResult[]; added: number }> {
  const feeds = (opts?.feeds ?? INTEL_FEEDS).filter((f) => {
    if (opts?.onlyEntryId && f.entryId !== opts.onlyEntryId) return false;
    if (opts?.entryIds && !opts.entryIds.has(f.entryId)) return false;
    return true;
  });
  const perFeedLimit = opts?.perFeedLimit ?? 3;
  let next = drafts;
  let added = 0;
  const results: ScrapeFeedResult[] = [];

  const pendingKeys = new Set(
    next.filter((d) => d.status === 'pending').map((d) => `${d.entryId}|${d.update.summary}`),
  );

  for (const feed of feeds) {
    const label = feed.label ?? feed.url;
    try {
      const xml = await fetchFeedText(feed.url);
      const items = parseFeedXml(xml).slice(0, perFeedLimit);
      let feedAdded = 0;
      for (const item of items) {
        const update = feedItemToUpdate(item);
        const key = `${feed.entryId}|${update.summary}`;
        if (pendingKeys.has(key)) continue;
        next = addIntelDraft(next, {
          entryId: feed.entryId,
          update,
          origin: 'feed-scrape',
        });
        pendingKeys.add(key);
        feedAdded += 1;
        added += 1;
      }
      results.push({
        entryId: feed.entryId,
        label,
        url: feed.url,
        ok: true,
        added: feedAdded,
        itemsSeen: items.length,
      });
    } catch (err) {
      results.push({
        entryId: feed.entryId,
        label,
        url: feed.url,
        ok: false,
        added: 0,
        itemsSeen: 0,
        error: err instanceof Error ? err.message : String(err),
      });
    }
  }

  return { drafts: next, results, added };
}
