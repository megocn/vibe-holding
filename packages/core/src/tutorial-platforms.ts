import type { Region } from './schema/common.ts';
import type { Entry, TutorialLink, TutorialPlatform } from './schema/entry.ts';

export type TutorialPlatformMeta = {
  id: TutorialPlatform;
  label: string;
  /** 将搜索词拼成该平台搜索页 URL */
  searchUrl: (query: string) => string;
};

export const TUTORIAL_PLATFORMS: readonly TutorialPlatformMeta[] = [
  {
    id: 'bilibili',
    label: 'B站',
    searchUrl: (q) => `https://search.bilibili.com/all?keyword=${encodeURIComponent(q)}`,
  },
  {
    id: 'youtube',
    label: 'YouTube',
    searchUrl: (q) => `https://www.youtube.com/results?search_query=${encodeURIComponent(q)}`,
  },
  {
    id: 'geekbang',
    label: '极客时间',
    searchUrl: (q) => `https://time.geekbang.org/search?q=${encodeURIComponent(q)}`,
  },
  {
    id: 'imooc',
    label: '慕课网',
    searchUrl: (q) => `https://www.imooc.com/search/?words=${encodeURIComponent(q)}`,
  },
  {
    id: 'coursera',
    label: 'Coursera',
    searchUrl: (q) => `https://www.coursera.org/search?query=${encodeURIComponent(q)}`,
  },
] as const;

const PLATFORM_BY_ID = new Map(TUTORIAL_PLATFORMS.map((p) => [p.id, p]));

/** 国内/both：中文平台优先；海外：英文平台优先。 */
const ORDER_DOMESTIC: TutorialPlatform[] = [
  'bilibili',
  'geekbang',
  'imooc',
  'youtube',
  'coursera',
];
const ORDER_OVERSEAS: TutorialPlatform[] = [
  'youtube',
  'coursera',
  'bilibili',
  'geekbang',
  'imooc',
];

export function orderedTutorialPlatforms(region: Region): TutorialPlatformMeta[] {
  const order = region === 'overseas' ? ORDER_OVERSEAS : ORDER_DOMESTIC;
  return order.map((id) => PLATFORM_BY_ID.get(id)!);
}

export type ResolvedTutorialLink = {
  platform: TutorialPlatform;
  label: string;
  href: string;
  /** 是否精选直达（有 url） */
  curated: boolean;
  note?: string;
};

function linkFor(
  links: TutorialLink[] | undefined,
  platform: TutorialPlatform,
): TutorialLink | undefined {
  return links?.find((l) => l.platform === platform);
}

/** 优先精选 url；否则用 query ?? name 拼搜索页。 */
export function resolveTutorialHref(
  entry: Pick<Entry, 'name' | 'tutorialLinks'>,
  platform: TutorialPlatform,
): ResolvedTutorialLink {
  const meta = PLATFORM_BY_ID.get(platform)!;
  const override = linkFor(entry.tutorialLinks, platform);
  const query = (override?.query?.trim() || entry.name).trim();
  if (override?.url) {
    return {
      platform,
      label: meta.label,
      href: override.url,
      curated: true,
      note: override.note,
    };
  }
  return {
    platform,
    label: meta.label,
    href: meta.searchUrl(query),
    curated: false,
    note: override?.note,
  };
}

export function resolveTutorialLinks(
  entry: Pick<Entry, 'name' | 'region' | 'tutorialLinks'>,
): ResolvedTutorialLink[] {
  return orderedTutorialPlatforms(entry.region).map((p) => resolveTutorialHref(entry, p.id));
}
