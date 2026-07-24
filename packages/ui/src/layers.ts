/**
 * 全链路基建地图的「卷」分层（图廓分区之上的拓扑层）。
 * 对应 PRD §4.1：把 A–V **section** 收束为可导航的七卷；条目挂在 section 下的 leaf。
 */

import type { Category } from '@vh/core';
import { sectionIdOf } from '@vh/core';

export interface CategoryLayer {
  id: string;
  /** 卷名（短，侧栏分组标题） */
  label: string;
  /** 一句副题 */
  subtitle: string;
  /** Phosphor 图标名 */
  icon: string;
  /** 所属图廓 section id（顺序即卷内顺序） */
  categories: readonly string[];
}

export const CATEGORY_LAYERS: readonly CategoryLayer[] = [
  {
    id: 'intelligence',
    label: 'AI 编码',
    subtitle: '代理 · 模型 · 接入',
    icon: 'Brain',
    categories: ['coding-agent', 'llm', 'model-gateway', 'ai-infra'],
  },
  {
    id: 'craft',
    label: '应用开发',
    subtitle: '语言 · 框架 · 界面',
    icon: 'Stack',
    categories: ['language-runtime', 'framework', 'ui-library', 'oss-ecosystem'],
  },
  {
    id: 'studio',
    label: '设计',
    subtitle: '工具 · 素材 · 生成',
    icon: 'PenNib',
    categories: ['design-assets'],
  },
  {
    id: 'infra',
    label: '云与数据',
    subtitle: '部署 · 存储 · 鉴权',
    icon: 'Cloud',
    categories: ['cloud-deploy', 'database-storage', 'baas-auth'],
  },
  {
    id: 'ops',
    label: '运维安全',
    subtitle: '监控 · CI · 网络 · 合规',
    icon: 'Pulse',
    categories: ['observability', 'cicd-devops', 'domain-dns-cdn', 'security-compliance'],
  },
  {
    id: 'commerce',
    label: '商业增长',
    subtitle: '支付 · 分发 · 消息 · 分析 · 出海',
    icon: 'Storefront',
    categories: ['payment', 'app-distribution', 'messaging', 'analytics-growth', 'globalization'],
  },
  {
    id: 'collab',
    label: '协作',
    subtitle: '项目 · 文档 · 套件',
    icon: 'Kanban',
    categories: ['collaboration'],
  },
] as const;

const categoryToLayer = new Map<string, CategoryLayer>();
for (const layer of CATEGORY_LAYERS) {
  for (const cat of layer.categories) {
    categoryToLayer.set(cat, layer);
  }
}

/**
 * 由分类 id 反查所属卷。
 * 支持 leaf（先解析到 section）与 section。
 */
export function layerOfCategory(
  categoryId: string,
  categories?: Iterable<Pick<Category, 'id' | 'kind' | 'parent'>>,
): CategoryLayer | undefined {
  const sectionId = categories ? sectionIdOf(categories, categoryId) : categoryId;
  return categoryToLayer.get(sectionId) ?? categoryToLayer.get(categoryId);
}

/** 卷内 section id 集合 */
export function layerCategorySet(layerId: string): Set<string> | null {
  const layer = CATEGORY_LAYERS.find((l) => l.id === layerId);
  return layer ? new Set(layer.categories) : null;
}
