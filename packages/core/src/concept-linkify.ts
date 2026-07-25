/** 文内概念点选：按 name/aliases 最长优先匹配。 */

export type ConceptTerm = {
  id: string;
  name: string;
  aliases?: readonly string[];
};

export type LinkifySegment =
  | { type: 'text'; value: string }
  | { type: 'concept'; value: string; conceptId: string };

type TermRule = {
  conceptId: string;
  term: string;
  /** 是否按拉丁词边界匹配（纯 ASCII 字母数字/./+/- 术语） */
  wordBoundary: boolean;
};

function isLatinTerm(term: string): boolean {
  return /^[A-Za-z0-9][A-Za-z0-9+./_-]*$/.test(term);
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** 从概念列表构建匹配规则（按术语长度降序）。 */
export function buildConceptTermRules(concepts: readonly ConceptTerm[]): TermRule[] {
  const seen = new Map<string, TermRule>();
  for (const c of concepts) {
    const terms = [c.name, ...(c.aliases ?? [])];
    for (const raw of terms) {
      const term = raw.trim();
      if (!term) continue;
      const key = term.toLowerCase();
      // 同名冲突时保留先登记的概念（内容侧应避免重复）
      if (seen.has(key)) continue;
      seen.set(key, {
        conceptId: c.id,
        term,
        wordBoundary: isLatinTerm(term),
      });
    }
  }
  return [...seen.values()].sort((a, b) => b.term.length - a.term.length);
}

function matchAt(text: string, i: number, rule: TermRule): boolean {
  const slice = text.slice(i, i + rule.term.length);
  if (rule.wordBoundary) {
    if (slice.toLowerCase() !== rule.term.toLowerCase()) return false;
    const before = i === 0 ? '' : text[i - 1]!;
    const after = text[i + rule.term.length] ?? '';
    const wordChar = /[A-Za-z0-9]/;
    if (wordChar.test(before) || wordChar.test(after)) return false;
    return true;
  }
  return slice === rule.term;
}

/**
 * 将正文切成 text / concept 片段。
 * 规则：最长优先、无重叠；拉丁词用词边界；含中文等非纯拉丁术语用字面匹配。
 */
export function linkifyConcepts(
  text: string,
  concepts: readonly ConceptTerm[],
  rules?: readonly TermRule[],
): LinkifySegment[] {
  if (!text) return [];
  const termRules = rules ?? buildConceptTermRules(concepts);
  if (termRules.length === 0) return [{ type: 'text', value: text }];

  const out: LinkifySegment[] = [];
  let i = 0;
  let buf = '';

  const flush = () => {
    if (buf) {
      out.push({ type: 'text', value: buf });
      buf = '';
    }
  };

  while (i < text.length) {
    let hit: TermRule | undefined;
    for (const rule of termRules) {
      if (i + rule.term.length > text.length) continue;
      if (matchAt(text, i, rule)) {
        hit = rule;
        break;
      }
    }
    if (hit) {
      flush();
      out.push({
        type: 'concept',
        value: text.slice(i, i + hit.term.length),
        conceptId: hit.conceptId,
      });
      i += hit.term.length;
    } else {
      buf += text[i];
      i += 1;
    }
  }
  flush();
  return out;
}

/** 供测试或调试：转义后的词边界模式（不用于主路径）。 */
export function latinTermPattern(term: string): RegExp {
  return new RegExp(`\\b${escapeRegExp(term)}\\b`, 'i');
}
