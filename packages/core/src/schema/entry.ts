import { z } from 'zod';
import { Id, IsoDate, Maturity, PricingModel, Region } from './common.ts';
import { EntryRanking } from './ranking.ts';

/** 事件流类型；`release` 表示有选型意义的大版本节点。 */
export const UpdateType = z.enum([
  'release',
  'feature',
  'pricing',
  'policy',
  'deprecation',
  'other',
]);
export type UpdateType = z.infer<typeof UpdateType>;

/** 详情时间线默认展示上限（超出仍可存库，UI 截断）。 */
export const ENTRY_UPDATES_DISPLAY_LIMIT = 5;

export const EntryUpdate = z.object({
  date: IsoDate,
  type: UpdateType,
  summary: z.string(),
  /** 版本号或版本名，如 `15.0`、`Opus 4.1`；`release` 建议填写 */
  version: z.string().min(1).max(40).optional(),
  source: z.string().url().optional(),
});
export type EntryUpdate = z.infer<typeof EntryUpdate>;

/** 教程平台直达入口（详情页固定展示；缺省走搜索页）。 */
export const TutorialPlatform = z.enum([
  'bilibili',
  'youtube',
  'geekbang',
  'imooc',
  'coursera',
]);
export type TutorialPlatform = z.infer<typeof TutorialPlatform>;

export const TutorialLink = z.object({
  platform: TutorialPlatform,
  /** 精选课/专栏直达；有则优先于搜索页 */
  url: z.string().url().optional(),
  /** 覆盖搜索词；缺省用 entry.name */
  query: z.string().min(1).max(80).optional(),
  /** 如「官方频道」 */
  note: z.string().max(40).optional(),
});
export type TutorialLink = z.infer<typeof TutorialLink>;

/**
 * 认知/决策类外链种类（详情「延伸」chip 行）。
 * - `what_is` / `wiki`：始终展示；无 url 时走搜索页
 * - 其余：有一等字段或精选 url 才展示（不强制搜索）
 */
export const ExternalLinkKind = z.enum([
  'what_is',
  'wiki',
  'github',
  'pricing',
  'status',
  'console',
  'playground',
  'changelog',
  'login',
  'starter',
  'community',
  'spec',
]);
export type ExternalLinkKind = z.infer<typeof ExternalLinkKind>;

export const ExternalLink = z.object({
  kind: ExternalLinkKind,
  /** 精选直达；有则优先于一等字段与搜索页 */
  url: z.string().url().optional(),
  /** 覆盖搜索词（仅 what_is / wiki）；缺省用 entry.name */
  query: z.string().min(1).max(80).optional(),
  note: z.string().max(40).optional(),
});
export type ExternalLink = z.infer<typeof ExternalLink>;

export const Entry = z.object({
  id: Id,
  name: z.string().min(1),
  category: Id,
  subcategory: z.string().optional(),
  vendorId: Id.optional(),
  region: Region,
  /** 选型一句话：同层差异 / 何时选，供列表扫读；勿只写品类标签 */
  oneLiner: z.string().max(80),
  descriptionMd: z.string(),
  officialUrl: z.string().url(),
  docsUrl: z.string().url().optional(),
  /** 源码仓（开源/公开仓库） */
  githubUrl: z.string().url().optional(),
  /** 独立定价页（常与官网/文档分离） */
  pricingUrl: z.string().url().optional(),
  /** 服务状态页 */
  statusUrl: z.string().url().optional(),
  /** 控制台 / Dashboard */
  consoleUrl: z.string().url().optional(),
  /** Playground / 沙箱 / Storybook */
  playgroundUrl: z.string().url().optional(),
  /** Changelog / Release Notes 入口 */
  changelogUrl: z.string().url().optional(),
  /** 登录页（快捷登录 Deep link） */
  loginUrl: z.string().url().optional(),
  /** 当前对外推荐版本（标量速查；谱系细节放 updates） */
  currentVersion: z.string().min(1).max(40).optional(),
  pricing: z.object({
    model: PricingModel,
    notes: z.string().optional(),
    currency: z.string().optional(),
  }),
  availability: z.object({
    chinaAccessible: z.boolean(),
    needsCompany: z.boolean().default(false),
    needsIcp: z.boolean().default(false),
    regions: z.array(z.string()).default([]),
  }),
  tags: z.array(z.string()).default([]),
  maturity: Maturity,
  usageGuideMd: z.string().optional(),
  /**
   * 教程平台可选覆盖（精选 URL / 搜索词）。
   * 详情页始终展示五大平台；无覆盖时用条目名拼搜索页。
   */
  tutorialLinks: z.array(TutorialLink).default([]),
  /**
   * 认知/决策外链可选覆盖（精选 URL / 搜索词）。
   * 与 githubUrl 等一等字段配合；详见 resolveExternalLinks。
   */
  externalLinks: z.array(ExternalLink).default([]),
  pitfalls: z.array(z.string()).default([]),
  updates: z.array(EntryUpdate).default([]),
  /**
   * 多套权威排行快照（每分类通常对应 1–2 套体系，见 RankingSystem）。
   * 无公开名次时可省略；勿编造。
   */
  rankings: z.array(EntryRanking).default([]),
  sources: z.array(z.string().url()).default([]),
  lastReviewed: IsoDate,
});
export type Entry = z.infer<typeof Entry>;
