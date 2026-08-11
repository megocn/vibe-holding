/**
 * 活水（aqua）review / candidates → 桌面端待确认队列。
 * 兼容 `private/aqua/reports/review-*.json` 与 `candidates-*.json`。
 */
import type { Entry, EntryUpdate, Id } from '@vh/core';
import type { DraftLevel, DraftOrigin, IntelDraft } from './intel-drafts.ts';
import { todayIso } from './intel.ts';

export type ChangeLevel = DraftLevel;

export const CANDIDATE_ENTRY_ID = '__candidate__' as Id;

export interface AquaReviewItem {
  id: string;
  entryId: string;
  update: EntryUpdate;
  status?: string;
  createdAt?: string;
  origin?: string;
  reviewerNote?: string;
  level?: ChangeLevel;
}

function isUpdateType(v: unknown): v is EntryUpdate['type'] {
  return (
    v === 'release' ||
    v === 'feature' ||
    v === 'pricing' ||
    v === 'policy' ||
    v === 'deprecation' ||
    v === 'other'
  );
}

function isLevel(v: unknown): v is ChangeLevel {
  return v === 'L0' || v === 'L1' || v === 'L2' || v === 'L3';
}

/** 仅真正的扩种卡（无库内条目）；挂在已有 entry 上的 L2/L3 仍走更新确认。 */
export function isExpandSeedDraft(draft: IntelDraft): boolean {
  return draft.entryId === CANDIDATE_ENTRY_ID;
}

export function parseAquaReviewPayload(raw: unknown): AquaReviewItem[] {
  if (!Array.isArray(raw)) return [];
  const out: AquaReviewItem[] = [];
  for (const item of raw) {
    if (!item || typeof item !== 'object') continue;
    const o = item as Record<string, unknown>;
    if (typeof o.id !== 'string' || typeof o.entryId !== 'string') continue;
    const updateRaw = o.update;
    if (!updateRaw || typeof updateRaw !== 'object') continue;
    const u = updateRaw as Record<string, unknown>;
    if (typeof u.summary !== 'string' || typeof u.date !== 'string') continue;
    if (!isUpdateType(u.type)) continue;
    const update: EntryUpdate = {
      date: u.date,
      type: u.type,
      summary: u.summary,
      ...(typeof u.version === 'string' ? { version: u.version } : {}),
      ...(typeof u.source === 'string' ? { source: u.source } : {}),
    };
    out.push({
      id: o.id,
      entryId: o.entryId,
      update,
      status: typeof o.status === 'string' ? o.status : undefined,
      createdAt: typeof o.createdAt === 'string' ? o.createdAt : undefined,
      origin: typeof o.origin === 'string' ? o.origin : undefined,
      reviewerNote: typeof o.reviewerNote === 'string' ? o.reviewerNote : undefined,
      level: isLevel(o.level) ? o.level : undefined,
    });
  }
  return out;
}

/** candidates-YYYY-MM-DD.json → 伪 review 项 */
export function parseCandidatesPayload(raw: unknown): AquaReviewItem[] {
  if (!raw || typeof raw !== 'object') return [];
  const cards = (raw as { cards?: unknown }).cards;
  if (!Array.isArray(cards)) return [];
  const date =
    typeof (raw as { generatedAt?: unknown }).generatedAt === 'string'
      ? (raw as { generatedAt: string }).generatedAt
      : todayIso();
  const out: AquaReviewItem[] = [];
  for (const c of cards) {
    if (!c || typeof c !== 'object') continue;
    const row = c as Record<string, unknown>;
    const subjectKey = typeof row.subjectKey === 'string' ? row.subjectKey : null;
    const name = typeof row.name === 'string' ? row.name : subjectKey;
    if (!subjectKey || !name) continue;
    const url = typeof row.url === 'string' ? row.url : undefined;
    const sources = Array.isArray(row.sources)
      ? row.sources.filter((s): s is string => typeof s === 'string')
      : [];
    const hits = typeof row.hitCount === 'number' ? row.hitCount : 0;
    const score = typeof row.score === 'number' ? row.score : 0;
    const cardMd =
      typeof row.cardMd === 'string'
        ? row.cardMd
        : [
            `## ${name}`,
            '',
            `- 归一键：\`${subjectKey}\``,
            `- 来源：${sources.join(', ') || '—'}（hits=${hits}，score=${score}）`,
            `- URL：${url ?? '—'}`,
            '',
            '建议：对照 expand-catalog 门槛决定是否建条目。',
          ].join('\n');
    out.push({
      id: `aqua-cand-${subjectKey}`,
      entryId: CANDIDATE_ENTRY_ID,
      update: {
        date,
        type: 'other',
        summary: `扩种候选：${name}`.slice(0, 120),
        source: url,
      },
      status: 'pending',
      createdAt: date,
      origin: 'aqua-review',
      reviewerNote: cardMd,
      level: 'L3',
    });
  }
  return out;
}

export function normalizeAquaImportPayload(raw: unknown): AquaReviewItem[] {
  if (Array.isArray(raw)) return parseAquaReviewPayload(raw);
  if (raw && typeof raw === 'object' && Array.isArray((raw as { cards?: unknown }).cards)) {
    return parseCandidatesPayload(raw);
  }
  return [];
}

/**
 * 合并进本地草稿队列：按 id 去重；已存在则跳过（保留用户已改状态）。
 */
export function mergeAquaReviewIntoDrafts(
  drafts: IntelDraft[],
  items: AquaReviewItem[],
): { drafts: IntelDraft[]; added: number; skipped: number } {
  const existing = new Set(drafts.map((d) => d.id));
  let next = [...drafts];
  let added = 0;
  let skipped = 0;
  for (const item of items) {
    if (existing.has(item.id)) {
      skipped += 1;
      continue;
    }
    const origin: DraftOrigin =
      item.entryId === CANDIDATE_ENTRY_ID || item.level === 'L3' || item.origin === 'aqua-review'
        ? 'aqua-review'
        : item.origin === 'feed-scrape'
          ? 'feed-scrape'
          : 'aqua-review';
    const draft: IntelDraft = {
      id: item.id,
      entryId: item.entryId as Id,
      update: item.update,
      status: 'pending',
      createdAt: item.createdAt ?? todayIso(),
      origin,
      reviewerNote: item.reviewerNote,
      level: item.level ?? (item.entryId === CANDIDATE_ENTRY_ID ? 'L3' : undefined),
    };
    next = [draft, ...next];
    existing.add(item.id);
    added += 1;
  }
  return { drafts: next, added, skipped };
}

function titleCaseToken(tok: string): string {
  if (/^\d/.test(tok)) return tok;
  if (tok.length <= 3 && tok === tok.toUpperCase()) return tok;
  return tok.charAt(0).toUpperCase() + tok.slice(1);
}

/** OpenRouter / Arena 等版本级 slug → 可读名 + kebab id */
export function humanizeSubjectSlug(raw: string): { id: string; name: string; vendor?: string } {
  let s = raw.trim();
  // openrouter: vendor/model:variant
  let vendor: string | undefined;
  const slash = s.match(/^([a-z0-9._-]+)\/(.+)$/i);
  if (slash) {
    vendor = slash[1];
    s = slash[2] ?? s;
  }
  s = s
    .replace(/:free$/i, '')
    .replace(/:[\w.-]+$/i, '')
    .replace(/[-_]?\d{8,}(?:t\d+)?$/i, '') // 日期戳 20260723
    .replace(/[-_]?\d{4}-\d{2}-\d{2}$/i, '');
  const idBase = s
    .toLowerCase()
    .replace(/\([^)]*\)/g, ' ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-')
    .slice(0, 40);
  const id = idBase && /^[a-z0-9]/.test(idBase) ? idBase : `candidate-${Date.now().toString(36)}`;
  const nameParts = s
    .replace(/[/_:]+/g, ' ')
    .replace(/[-_]+/g, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map(titleCaseToken);
  let name = nameParts.join(' ') || id;
  if (vendor && !name.toLowerCase().includes(vendor.toLowerCase())) {
    const vNice = vendor.split(/[-_.]/).filter(Boolean).map(titleCaseToken).join('');
    // inclusionai → Inclusionai；常见厂商保留原样可读
    name = `${vNice} ${name}`.trim();
  }
  return { id, name: name.slice(0, 80), vendor };
}

function extractSignalBits(note: string): {
  source?: string;
  hits?: string;
  share?: string;
  tokens?: string;
  scoreLine?: string;
} {
  const source =
    note.match(/[-*]\s*source:\s*(\S+)/i)?.[1] ??
    note
      .match(/来源：([a-z0-9,-]+)/i)?.[1]
      ?.split('（')[0]
      ?.trim();
  const hits =
    note.match(/hits\s*=\s*(\d+)/i)?.[1] ?? note.match(/累计来源:[^（]*（hits=(\d+)/i)?.[1];
  const share = note.match(/share\s*[≈~=]?\s*([\d.]+%?)/i)?.[1];
  const tokens = note.match(/tokens\([^)]+\)\s*=\s*([\d.e+]+)/i)?.[1];
  const scoreLine = note
    .split('\n')
    .map((l) => l.trim())
    .find((l) => /share\s*[≈~=]|tokens\(|score\s*=|votes/i.test(l) && !l.startsWith('-'));
  return { source, hits, share, tokens, scoreLine };
}

export type ExpandCardMeta = {
  raw: string | null;
  name: string;
  url: string | null;
  suggestedId: string;
  suggestedCategory?: Id;
  sourceLabel?: string;
  versionLevelWarning: boolean;
  evidenceLines: string[];
};

/** 从候选卡片正文抽可建条字段 */
export function parseExpandCardMeta(draft: IntelDraft): ExpandCardMeta {
  const note = draft.reviewerNote ?? '';
  const raw =
    note.match(/[-*]\s*raw:\s*`([^`]+)`/i)?.[1]?.trim() ??
    note.match(/归一键：`([^`]+)`/)?.[1]?.trim() ??
    null;
  const fromNameLine = note.match(/[-*]\s*name:\s*(.+)$/im)?.[1]?.trim();
  const fromHeading = note.match(/^##\s+\d*\.?\s*(.+)$/m)?.[1]?.trim();
  const fromSummary = draft.update.summary.replace(/^(未能解析[^：]*：|扩种候选：)/, '').trim();
  const crude = (fromNameLine || fromHeading || fromSummary || raw || '未命名候选').trim();
  const human = humanizeSubjectSlug(raw ?? crude);
  const urlFromNote =
    note.match(/[-*]\s*url:\s*(\S+)/i)?.[1]?.trim() ??
    note.match(/URL：(\S+)/)?.[1]?.trim() ??
    null;
  const url =
    (draft.update.source && /^https?:\/\//.test(draft.update.source)
      ? draft.update.source
      : null) ??
    (urlFromNote && urlFromNote !== '—' && /^https?:\/\//.test(urlFromNote) ? urlFromNote : null);

  const bits = extractSignalBits(note);
  const sourceLabel = bits.source;
  const versionLevelWarning = Boolean(
    raw &&
      (/:\w+/.test(raw) ||
        /\/.+-20\d{6}/.test(raw) ||
        /20\d{6}/.test(raw) ||
        /openrouter/i.test(sourceLabel ?? '') ||
        /arena/i.test(sourceLabel ?? '')),
  );

  let suggestedCategory: Id | undefined;
  if (/openrouter|arena|lmarena|aa\b/i.test(`${sourceLabel ?? ''} ${url ?? ''} ${note}`)) {
    suggestedCategory = 'llm-line' as Id;
  } else if (/producthunt|hn\b|github/i.test(sourceLabel ?? '')) {
    suggestedCategory = undefined;
  }

  const evidenceLines = [
    sourceLabel ? `信源 ${sourceLabel}` : null,
    bits.hits ? `跨轮命中 ${bits.hits} 次` : null,
    bits.share ? `份额 ${bits.share}` : null,
    bits.tokens ? `近窗 tokens ${bits.tokens}` : null,
    url ? `链接 ${url}` : null,
    raw && raw !== human.name ? `外部标识 \`${raw}\`` : null,
  ].filter((x): x is string => Boolean(x));

  return {
    raw,
    name: human.name,
    url,
    suggestedId: human.id,
    suggestedCategory,
    sourceLabel,
    versionLevelWarning,
    evidenceLines,
  };
}

export function suggestEntryId(nameOrRaw: string): string {
  return humanizeSubjectSlug(nameOrRaw).id;
}

/** 生成本机扩种草稿条目（overlay）；用证据预填可读草稿，不编造未核对能力。 */
export function buildExpandStubEntry(input: {
  id: string;
  name: string;
  category: Id;
  officialUrl: string;
  note?: string;
  sourceUrl?: string;
  meta?: ExpandCardMeta;
}): Entry {
  const today = todayIso();
  const sources = [input.sourceUrl, input.officialUrl].filter(
    (u): u is string => typeof u === 'string' && /^https?:\/\//.test(u),
  );
  const uniqSources = [...new Set(sources)];
  const meta = input.meta;
  const evidence = meta?.evidenceLines?.length
    ? meta.evidenceLines
    : [
        input.officialUrl ? `链接 ${input.officialUrl}` : null,
        input.note?.match(/source:\s*(\S+)/i)?.[1]
          ? `信源 ${input.note.match(/source:\s*(\S+)/i)?.[1]}`
          : null,
      ].filter((x): x is string => Boolean(x));

  const sourceHint = meta?.sourceLabel ?? '外部信源';
  const oneLiner = `${sourceHint} 候选 · ${input.name} · 待补同叶差异`.slice(0, 80);

  const cautionBits = [
    '本机草稿，未对照扩种准入验收，勿当作公开库推荐。',
    meta?.versionLevelWarning
      ? '外部标识像版本/路由级 slug（含日期或 :free 等）；优先归并到已有档位条目，确认确需独立建条再补文案与边。'
      : '补写前先核官网与同叶短名单，达不到门槛请直接删本机覆盖。',
  ];

  const descriptionMd = [
    `${input.name}。`,
    '',
    `是什么：活水从 ${sourceHint} 发现的未入库主体；下列事实来自候选证据，产品定位与能力边界待人工核对后改写。`,
    evidence.length ? evidence.map((l) => `- ${l}`).join('\n') : '- （无结构化证据行）',
    '',
    '何时选：待对照同叶 3–8 强短名单后补差异化轴（能力形态 / 生态 / 约束）；仅凭热度或份额不够入库。',
    '',
    `注意什么：${cautionBits.join(' ')}`,
  ].join('\n');

  const pricingModel =
    /:free\b/i.test(meta?.raw ?? '') || /free/i.test(input.officialUrl)
      ? ('free' as const)
      : ('usage' as const);

  return {
    id: input.id as Id,
    name: input.name.slice(0, 80),
    category: input.category,
    region: 'overseas',
    oneLiner,
    descriptionMd,
    officialUrl: input.officialUrl,
    pricing: {
      model: pricingModel,
      notes:
        pricingModel === 'free'
          ? '信源标识含 free；正式定价档位待核官网/控制台'
          : '计费模型待核官网；勿凭榜单份额臆测标价',
    },
    availability: {
      chinaAccessible: false,
      needsCompany: false,
      needsIcp: false,
      regions: [],
    },
    tags: ['aqua-expand-draft'],
    maturity: 'experimental',
    pitfalls: cautionBits,
    updates: [],
    rankings: [],
    tutorialLinks: [],
    externalLinks: [],
    sources: uniqSources.length ? uniqSources : [input.officialUrl],
    lastReviewed: today,
  };
}

/** 开发服务器：拉取最新 review JSON */
export async function fetchLocalAquaReview(): Promise<{
  items: AquaReviewItem[];
  meta: { file?: string; generatedAt?: string; count?: number };
}> {
  const res = await fetch('/__vh_aqua_review', { cache: 'no-store' });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `同步失败（HTTP ${res.status}）`);
  }
  const body = (await res.json()) as {
    file?: string;
    generatedAt?: string;
    count?: number;
    drafts?: unknown;
  };
  return {
    items: normalizeAquaImportPayload(body.drafts ?? body),
    meta: {
      file: body.file,
      generatedAt: body.generatedAt,
      count: body.count,
    },
  };
}
