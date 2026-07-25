/** 文内概念点选：按 name/aliases 最长优先匹配，并过滤过泛噪声。 */

export type ConceptTerm = {
  id: string;
  name: string;
  aliases?: readonly string[];
};

export type LinkifySegment =
  | { type: 'text'; value: string }
  | { type: 'concept'; value: string; conceptId: string };

export type LinkifyOptions = {
  /**
   * 保护区间原文（如条目名「Muse Image」）：落在这些子串内的命中会被跳过，
   * 避免产品名里的普通词（Image）被当成容器镜像等概念。
   */
  protectTexts?: readonly string[];
};

type TermRule = {
  conceptId: string;
  term: string;
  /** 拉丁/多词拉丁：大小写不敏感 + 词边界；中文等：字面匹配 */
  kind: 'latin' | 'literal';
};

const WORD_CHAR = /[A-Za-z0-9]/;

/** 纯拉丁单 token（无空格）。 */
function isLatinToken(term: string): boolean {
  return /^[A-Za-z0-9][A-Za-z0-9+./_-]*$/.test(term);
}

/** 多词拉丁（空格分隔的 ASCII 术语，如 function calling）。 */
function isLatinPhrase(term: string): boolean {
  return /^[A-Za-z0-9][A-Za-z0-9+./_-]*(?:\s+[A-Za-z0-9][A-Za-z0-9+./_-]*)+$/.test(term);
}

function hasCjk(term: string): boolean {
  return /[\u4e00-\u9fff]/.test(term);
}

function cjkLen(term: string): number {
  return [...term].filter((ch) => /[\u4e00-\u9fff]/.test(ch)).length;
}

/**
 * 过泛、易误点的术语：即使写在概念 aliases 里也不参与文内匹配。
 * 展示名仍可在 Popover / 关系面板使用。
 */
const DENY_TERMS = new Set(
  [
    // 截图像素例：Muse Image / Meta 生态 / 图像工作流
    'image',
    '镜像',
    '生态',
    '工作流',
    // 过短/过泛中文（日常义远大于术语义）
    '托管',
    '编排',
    '延迟',
    '并行',
    '并发',
    '缓存',
    '备份',
    '快照',
    '计费',
    '推理',
    '评测',
    '嵌入',
    '接地',
    '绿地',
    '护栏',
    '降级',
    '热点',
    '弃用',
    '归档',
    '带宽',
    '网关',
    '全栈',
    '自建',
    '容器',
    '会话',
    '重试',
    '配额',
    '发票',
    '专票',
    '普票',
    '气隙',
    '备案',
    '灰度',
    // 过噪拉丁短词 / 日常词（缩写如 GPU/CDN/RAG 不在此列）
    'indie',
    'blob',
    'eval',
    'cache',
    'ui',
    'ux',
    'dx',
    'ga',
    'ha',
    'az',
    'kv',
  ].map((t) => t.toLowerCase()),
);

/**
 * 允许参与匹配的短中文（≤2 字）白名单——其余 ≤2 字中文一律跳过。
 * 这些在选型语境里术语义足够稳。
 */
const ALLOW_SHORT_ZH = new Set(['开源', '微调', '限流', '幂等', '幻觉']);

/** 术语是否具备足够区分度，可参与文内 linkify。 */
export function isLinkableTerm(term: string): boolean {
  const t = term.trim();
  if (!t) return false;
  if (DENY_TERMS.has(t.toLowerCase())) return false;

  if (hasCjk(t)) {
    const n = cjkLen(t);
    if (n <= 2 && !ALLOW_SHORT_ZH.has(t)) return false;
    // 纯标点/过短
    if (t.length < 2) return false;
    return true;
  }

  if (isLatinToken(t) || isLatinPhrase(t)) {
    // 单字母不链；2 字母仅允许常见大写缩写（由内容侧写 DI/RL 等，仍受 DENY 约束）
    const compact = t.replace(/\s+/g, '');
    if (compact.length < 2) return false;
    if (compact.length === 2 && compact !== compact.toUpperCase()) return false;
    return true;
  }

  // 中英混合（如「开源权重」已在 CJK 分支；「GPT-4」走拉丁）
  return t.length >= 3;
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** 从概念列表构建匹配规则（过滤噪声后按术语长度降序）。 */
export function buildConceptTermRules(concepts: readonly ConceptTerm[]): TermRule[] {
  const seen = new Map<string, TermRule>();
  for (const c of concepts) {
    const terms = [c.name, ...(c.aliases ?? [])];
    for (const raw of terms) {
      const term = raw.trim();
      if (!isLinkableTerm(term)) continue;
      const key = term.toLowerCase();
      // 同名冲突时保留先登记的概念（内容侧应避免重复）
      if (seen.has(key)) continue;
      const kind: TermRule['kind'] =
        isLatinToken(term) || isLatinPhrase(term) ? 'latin' : 'literal';
      seen.set(key, { conceptId: c.id, term, kind });
    }
  }
  return [...seen.values()].sort((a, b) => b.term.length - a.term.length);
}

function buildProtectedRanges(text: string, protectTexts: readonly string[] | undefined): [number, number][] {
  if (!protectTexts?.length) return [];
  const ranges: [number, number][] = [];
  for (const raw of protectTexts) {
    const p = raw.trim();
    if (p.length < 2) continue;
    const hay = text.toLowerCase();
    const needle = p.toLowerCase();
    let from = 0;
    while (from <= hay.length - needle.length) {
      const at = hay.indexOf(needle, from);
      if (at < 0) break;
      ranges.push([at, at + needle.length]);
      from = at + needle.length;
    }
  }
  return ranges;
}

function overlapsProtected(start: number, end: number, ranges: readonly [number, number][]): boolean {
  for (const [a, b] of ranges) {
    if (start < b && end > a) return true;
  }
  return false;
}

function matchAt(text: string, i: number, rule: TermRule): boolean {
  const end = i + rule.term.length;
  if (end > text.length) return false;
  const slice = text.slice(i, end);

  if (rule.kind === 'latin') {
    if (slice.toLowerCase() !== rule.term.toLowerCase()) return false;
    const before = i === 0 ? '' : text[i - 1]!;
    const after = text[end] ?? '';
    if (WORD_CHAR.test(before) || WORD_CHAR.test(after)) return false;
    return true;
  }

  return slice === rule.term;
}

/**
 * 将正文切成 text / concept 片段。
 * 规则：最长优先、无重叠；过滤过泛词；可保护产品名区间。
 */
export function linkifyConcepts(
  text: string,
  concepts: readonly ConceptTerm[],
  rules?: readonly TermRule[],
  options: LinkifyOptions = {},
): LinkifySegment[] {
  if (!text) return [];
  const termRules = rules ?? buildConceptTermRules(concepts);
  if (termRules.length === 0) return [{ type: 'text', value: text }];

  const protectedRanges = buildProtectedRanges(text, options.protectTexts);
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
      if (!matchAt(text, i, rule)) continue;
      const end = i + rule.term.length;
      if (overlapsProtected(i, end, protectedRanges)) continue;
      hit = rule;
      break;
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
