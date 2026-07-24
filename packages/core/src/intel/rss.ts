import type { EntryUpdate, UpdateType } from '../schema/entry.ts';

export interface FeedItem {
  title: string;
  link?: string;
  /** ISO 日期 YYYY-MM-DD（尽力解析） */
  date?: string;
  summary?: string;
  id?: string;
}

export interface FeedSource {
  entryId: string;
  url: string;
  label?: string;
}

function decodeEntities(s: string): string {
  return s
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCharCode(Number.parseInt(h, 16)));
}

function stripTags(s: string): string {
  return decodeEntities(s)
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function firstTag(block: string, names: string[]): string | undefined {
  for (const name of names) {
    const re = new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${name}>`, 'i');
    const m = block.match(re);
    if (m?.[1]?.trim()) return decodeEntities(m[1].trim());
    // self-closing / attr href for atom link
    if (name === 'link') {
      const href = block.match(/<link[^>]*\bhref=["']([^"']+)["'][^>]*\/?>/i);
      if (href?.[1]) return href[1];
      const plain = block.match(/<link>([^<]+)<\/link>/i);
      if (plain?.[1]) return plain[1].trim();
    }
  }
  return undefined;
}

function toIsoDate(raw: string | undefined): string | undefined {
  if (!raw) return undefined;
  const t = Date.parse(raw.trim());
  if (Number.isNaN(t)) {
    const m = raw.match(/(\d{4}-\d{2}-\d{2})/);
    return m?.[1];
  }
  return new Date(t).toISOString().slice(0, 10);
}

function parseBlocks(xml: string, tag: 'item' | 'entry'): string[] {
  const re = new RegExp(`<${tag}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${tag}>`, 'gi');
  const out: string[] = [];
  let m: RegExpExecArray | null = re.exec(xml);
  while (m) {
    out.push(m[1] ?? '');
    m = re.exec(xml);
  }
  return out;
}

/** 解析 RSS 2.0 / Atom XML（无 DOM 依赖，浏览器与 Node 可用）。 */
export function parseFeedXml(xml: string): FeedItem[] {
  const trimmed = xml.replace(/^\uFEFF/, '').trim();
  if (!trimmed) return [];

  const isAtom =
    /<feed[\s>]/i.test(trimmed) ||
    /xmlns=["']https?:\/\/www\.w3\.org\/2005\/Atom["']/i.test(trimmed);
  const blocks = isAtom ? parseBlocks(trimmed, 'entry') : parseBlocks(trimmed, 'item');
  // 若误判，尝试另一种
  const useBlocks =
    blocks.length > 0
      ? { blocks, atom: isAtom }
      : {
          blocks: isAtom ? parseBlocks(trimmed, 'item') : parseBlocks(trimmed, 'entry'),
          atom: !isAtom,
        };

  const items: FeedItem[] = [];
  for (const block of useBlocks.blocks) {
    const titleRaw = firstTag(block, ['title']);
    if (!titleRaw) continue;
    const title = stripTags(titleRaw);
    if (!title) continue;

    let link: string | undefined;
    if (useBlocks.atom) {
      const alt = block.match(
        /<link[^>]*rel=["']alternate["'][^>]*href=["']([^"']+)["'][^>]*\/?>/i,
      );
      const any = block.match(/<link[^>]*href=["']([^"']+)["'][^>]*\/?>/i);
      link = alt?.[1] ?? any?.[1] ?? firstTag(block, ['link']);
    } else {
      link = firstTag(block, ['link', 'guid']);
    }

    const dateRaw = firstTag(block, ['pubDate', 'updated', 'published', 'dc:date', 'date']);
    const summaryRaw = firstTag(block, ['description', 'summary', 'content:encoded', 'content']);
    const id = firstTag(block, ['guid', 'id']);

    items.push({
      title,
      link: link ? stripTags(link) : undefined,
      date: toIsoDate(dateRaw),
      summary: summaryRaw ? stripTags(summaryRaw).slice(0, 280) : undefined,
      id: id ? stripTags(id) : undefined,
    });
  }
  return items;
}

/** 根据标题/摘要猜测更新类型（无 LLM）。 */
export function guessUpdateType(text: string): UpdateType {
  const t = text.toLowerCase();
  if (/\b(deprecat|sunset|end of life|\beol\b|remov(e|ing)|discontinu)/.test(t))
    return 'deprecation';
  if (/\b(pric(e|ing)|plan|billing|quota|cost|收费|定价|套餐)/.test(t)) return 'pricing';
  if (/\b(policy|terms|privacy|kyc|合规|条款|隐私|security release)/.test(t)) return 'policy';
  // 大版本优先于泛 feature（避免 "release notes" 误判为 release）
  if (
    /\b(v?\d+\.\d+(?:\.\d+)?)\b/.test(t) ||
    /\b(major\s+release|version\s+\d|大版本|正式版|ga\s+release)\b/.test(t)
  ) {
    return 'release';
  }
  if (/\b(feature|launch|introduc|announce|release|beta|ga\b|新功能)/.test(t)) return 'feature';
  return 'feature';
}

/** 从标题中抽出版本号（尽力而为）。 */
export function extractVersion(text: string): string | undefined {
  const semver = text.match(/\bv?(\d+\.\d+(?:\.\d+)?(?:[-.][\w]+)?)\b/i);
  if (semver?.[1]) return semver[1];
  const named = text.match(
    /\b((?:Opus|Sonnet|Haiku|GPT|Claude|Gemini|DeepSeek)[\s-]?\d+(?:\.\d+)?[a-z]?)\b/i,
  );
  if (named?.[1]) return named[1].replace(/\s+/g, ' ').trim();
  return undefined;
}

export function feedItemToUpdate(item: FeedItem, opts?: { today?: string }): EntryUpdate {
  const today = opts?.today ?? new Date().toISOString().slice(0, 10);
  const date = item.date && /^\d{4}-\d{2}-\d{2}$/.test(item.date) ? item.date : today;
  const blob = `${item.title} ${item.summary ?? ''}`;
  const summary = item.summary ? `${item.title} — ${item.summary}` : item.title;
  const type = guessUpdateType(blob);
  const update: EntryUpdate = {
    date,
    type,
    summary: summary.slice(0, 240),
  };
  const version = extractVersion(blob);
  if (version) update.version = version;
  if (item.link) {
    try {
      new URL(item.link);
      update.source = item.link;
    } catch {
      // ignore invalid link
    }
  }
  return update;
}
