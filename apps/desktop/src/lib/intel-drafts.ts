import type { Entry, EntryUpdate, Id, UpdateType } from '@vh/core';
import { todayIso } from './intel.ts';

const KEY = 'vh-intel-drafts';

export type DraftOrigin = 'manual' | 'simulated-scrape' | 'feed-scrape';
export type DraftStatus = 'pending' | 'accepted' | 'rejected';

export interface IntelDraft {
  id: string;
  entryId: Id;
  update: EntryUpdate;
  status: DraftStatus;
  createdAt: string;
  origin: DraftOrigin;
  reviewerNote?: string;
}

function newDraftId(): string {
  return `draft-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}

export function loadIntelDrafts(): IntelDraft[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (d): d is IntelDraft =>
        d &&
        typeof d === 'object' &&
        typeof d.id === 'string' &&
        typeof d.entryId === 'string' &&
        d.update &&
        typeof d.update.summary === 'string',
    );
  } catch {
    return [];
  }
}

export function saveIntelDrafts(drafts: IntelDraft[]): void {
  localStorage.setItem(KEY, JSON.stringify(drafts));
}

export function pendingDrafts(drafts: IntelDraft[]): IntelDraft[] {
  return drafts
    .filter((d) => d.status === 'pending')
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt) || b.id.localeCompare(a.id));
}

export function addIntelDraft(
  drafts: IntelDraft[],
  input: {
    entryId: Id;
    update: EntryUpdate;
    origin?: DraftOrigin;
  },
): IntelDraft[] {
  const draft: IntelDraft = {
    id: newDraftId(),
    entryId: input.entryId,
    update: input.update,
    status: 'pending',
    createdAt: todayIso(),
    origin: input.origin ?? 'manual',
  };
  return [draft, ...drafts];
}

export function setDraftStatus(
  drafts: IntelDraft[],
  id: string,
  status: DraftStatus,
  reviewerNote?: string,
): IntelDraft[] {
  return drafts.map((d) =>
    d.id === id ? { ...d, status, reviewerNote: reviewerNote ?? d.reviewerNote } : d,
  );
}

export function removeIntelDraft(drafts: IntelDraft[], id: string): IntelDraft[] {
  return drafts.filter((d) => d.id !== id);
}

/** 将草稿合并进条目（去重：同 date+summary）；返回新 Entry 或 null（已存在）。 */
export function mergeDraftIntoEntry(entry: Entry, draft: IntelDraft): Entry | null {
  const u = draft.update;
  const dup = entry.updates.some((x) => x.date === u.date && x.summary === u.summary);
  if (dup) return null;
  return {
    ...entry,
    updates: [...entry.updates, u].sort((a, b) => b.date.localeCompare(a.date)),
    lastReviewed: todayIso(),
  };
}

const DEMO_TEMPLATES: Array<{
  entryId: Id;
  type: UpdateType;
  summary: string;
  sourcePath?: string;
}> = [
  {
    entryId: 'cursor',
    type: 'feature',
    summary: '【草稿】Agent 模式支持多文件并行编辑预览',
    sourcePath: 'https://cursor.com/changelog',
  },
  {
    entryId: 'vercel',
    type: 'pricing',
    summary: '【草稿】Hobby 计划边缘请求配额调整（待核实）',
    sourcePath: 'https://vercel.com/blog',
  },
  {
    entryId: 'supabase',
    type: 'feature',
    summary: '【草稿】Edge Functions 冷启动优化公告',
    sourcePath: 'https://supabase.com/blog',
  },
  {
    entryId: 'stripe',
    type: 'policy',
    summary: '【草稿】部分地区 KYC 要求更新说明',
    sourcePath: 'https://stripe.com/blog',
  },
  {
    entryId: 'nextjs',
    type: 'deprecation',
    summary: '【草稿】旧版 Image Optimization 配置项即将弃用',
    sourcePath: 'https://nextjs.org/blog',
  },
];

/**
 * 为内容库中存在的条目生成模拟抓取草稿（跳过已有相同 summary 的 pending）。
 * 真实抓取见 `intel-scrape.ts`（T-INTEL-4）。
 */
export function seedSimulatedDrafts(
  drafts: IntelDraft[],
  entryIds: Set<string>,
): { drafts: IntelDraft[]; added: number } {
  let next = drafts;
  let added = 0;
  const pendingSummaries = new Set(
    next.filter((d) => d.status === 'pending').map((d) => `${d.entryId}|${d.update.summary}`),
  );
  const date = todayIso();

  for (const t of DEMO_TEMPLATES) {
    if (!entryIds.has(t.entryId)) continue;
    const key = `${t.entryId}|${t.summary}`;
    if (pendingSummaries.has(key)) continue;
    next = addIntelDraft(next, {
      entryId: t.entryId,
      origin: 'simulated-scrape',
      update: {
        date,
        type: t.type,
        summary: t.summary,
        source: t.sourcePath,
      },
    });
    pendingSummaries.add(key);
    added += 1;
  }
  return { drafts: next, added };
}
