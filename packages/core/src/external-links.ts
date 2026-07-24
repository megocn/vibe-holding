import type { Region } from './schema/common.ts';
import type { Entry, ExternalLink, ExternalLinkKind } from './schema/entry.ts';

export type ExternalLinkMeta = {
  id: ExternalLinkKind;
  label: string;
  /** 无精选/一等字段时是否仍展示（走搜索页） */
  alwaysShow: boolean;
  /** 将搜索词拼成搜索页；仅 alwaysShow 种类需要 */
  searchUrl?: (query: string, region: Region) => string;
};

/** 一等 URL 字段 ↔ kind（精选覆盖优先于字段） */
const FIELD_BY_KIND: Partial<Record<ExternalLinkKind, keyof Entry>> = {
  github: 'githubUrl',
  pricing: 'pricingUrl',
  status: 'statusUrl',
  console: 'consoleUrl',
  playground: 'playgroundUrl',
  changelog: 'changelogUrl',
  login: 'loginUrl',
};

export const EXTERNAL_LINK_KINDS: readonly ExternalLinkMeta[] = [
  {
    id: 'what_is',
    label: '这是什么？',
    alwaysShow: true,
    searchUrl: (q, region) => {
      const term = region === 'overseas' ? `${q} what is` : `${q} 是什么`;
      return `https://www.bing.com/search?q=${encodeURIComponent(term)}`;
    },
  },
  {
    id: 'wiki',
    label: 'Wiki',
    alwaysShow: true,
    searchUrl: (q, region) => {
      const host = region === 'overseas' ? 'en.wikipedia.org' : 'zh.wikipedia.org';
      return `https://${host}/w/index.php?search=${encodeURIComponent(q)}`;
    },
  },
  { id: 'github', label: '源码', alwaysShow: false },
  { id: 'pricing', label: '定价', alwaysShow: false },
  { id: 'status', label: '状态', alwaysShow: false },
  { id: 'console', label: '控制台', alwaysShow: false },
  { id: 'playground', label: '沙箱', alwaysShow: false },
  { id: 'changelog', label: '更新日志', alwaysShow: false },
  { id: 'login', label: '登录', alwaysShow: false },
  { id: 'starter', label: '示例', alwaysShow: false },
  { id: 'community', label: '社区', alwaysShow: false },
  { id: 'spec', label: 'Spec', alwaysShow: false },
] as const;

const META_BY_ID = new Map(EXTERNAL_LINK_KINDS.map((m) => [m.id, m]));

export type ResolvedExternalLink = {
  kind: ExternalLinkKind;
  label: string;
  href: string;
  /** 精选直达或一等字段 */
  curated: boolean;
  note?: string;
};

function overrideFor(
  links: ExternalLink[] | undefined,
  kind: ExternalLinkKind,
): ExternalLink | undefined {
  return links?.find((l) => l.kind === kind);
}

function fieldUrl(
  entry: Entry,
  kind: ExternalLinkKind,
): string | undefined {
  const key = FIELD_BY_KIND[kind];
  if (!key) return undefined;
  const v = entry[key];
  return typeof v === 'string' && v.length > 0 ? v : undefined;
}

/**
 * 解析单条外链：精选 url → 一等字段 →（alwaysShow）搜索页；否则 null。
 */
export function resolveExternalHref(
  entry: Pick<
    Entry,
    | 'name'
    | 'region'
    | 'externalLinks'
    | 'githubUrl'
    | 'pricingUrl'
    | 'statusUrl'
    | 'consoleUrl'
    | 'playgroundUrl'
    | 'changelogUrl'
    | 'loginUrl'
  >,
  kind: ExternalLinkKind,
): ResolvedExternalLink | null {
  const meta = META_BY_ID.get(kind);
  if (!meta) return null;

  const override = overrideFor(entry.externalLinks, kind);
  if (override?.url) {
    return {
      kind,
      label: meta.label,
      href: override.url,
      curated: true,
      note: override.note,
    };
  }

  const fromField = fieldUrl(entry as Entry, kind);
  if (fromField) {
    return {
      kind,
      label: meta.label,
      href: fromField,
      curated: true,
      note: override?.note,
    };
  }

  if (meta.alwaysShow && meta.searchUrl) {
    const query = (override?.query?.trim() || entry.name).trim();
    return {
      kind,
      label: meta.label,
      href: meta.searchUrl(query, entry.region),
      curated: false,
      note: override?.note,
    };
  }

  return null;
}

/** 详情「延伸」chip 行：按固定顺序，跳过无链接的种类。 */
export function resolveExternalLinks(
  entry: Pick<
    Entry,
    | 'name'
    | 'region'
    | 'externalLinks'
    | 'githubUrl'
    | 'pricingUrl'
    | 'statusUrl'
    | 'consoleUrl'
    | 'playgroundUrl'
    | 'changelogUrl'
    | 'loginUrl'
  >,
): ResolvedExternalLink[] {
  const out: ResolvedExternalLink[] = [];
  for (const meta of EXTERNAL_LINK_KINDS) {
    const resolved = resolveExternalHref(entry, meta.id);
    if (resolved) out.push(resolved);
  }
  return out;
}
