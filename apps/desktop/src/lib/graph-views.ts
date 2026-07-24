/** 图谱多视图（PRD §7.6） */

export type GraphLens =
  | 'ecosystem'
  | 'alternatives'
  | 'dependency'
  | 'recipe'
  | 'vendor'
  | 'mirror'
  | 'compat'
  | 'learning'
  | 'personal';

export interface GraphLensMeta {
  id: GraphLens;
  label: string;
  hint: string;
  /** 布局策略 */
  layout: 'force' | 'dag' | 'mirror' | 'cose';
  /** 是否强烈依赖焦点 */
  needsFocus?: boolean;
}

export const GRAPH_LENSES: GraphLensMeta[] = [
  { id: 'ecosystem', label: '生态全景', hint: '按分类鸟瞰全图或焦点邻域', layout: 'force' },
  {
    id: 'alternatives',
    label: '替代簇',
    hint: 'alternative / 开源平替竞争簇',
    layout: 'force',
    needsFocus: true,
  },
  {
    id: 'dependency',
    label: '依赖 DAG',
    hint: 'depends_on / built_on / powered_by / hosts',
    layout: 'dag',
  },
  { id: 'recipe', label: '方案子图', hint: '高亮选定 Recipe 各层', layout: 'force' },
  { id: 'vendor', label: '厂商', hint: '按 vendorId 聚类（供应商锁定）', layout: 'cose' },
  {
    id: 'mirror',
    label: '国内外镜像',
    hint: 'domestic / overseas 左右对照',
    layout: 'mirror',
  },
  {
    id: 'compat',
    label: '兼容/冲突',
    hint: '绿：兼容搭配 · 红：冲突',
    layout: 'force',
  },
  {
    id: 'learning',
    label: '学习路径',
    hint: 'prerequisite_of DAG（边较少时近空）',
    layout: 'dag',
  },
  {
    id: 'personal',
    label: '个人',
    hint: '收藏 · 关注 · 我的技术栈',
    layout: 'force',
  },
];

/** 各视图允许的边类型；null = 不过滤类型（仍可走通用 filter） */
export const LENS_EDGE_TYPES: Record<GraphLens, Set<string> | null> = {
  ecosystem: null,
  alternatives: new Set([
    'alternative_to',
    'open_source_alternative_to',
    'succeeds',
    'deprecated_by',
  ]),
  dependency: new Set([
    'depends_on',
    'built_on',
    'powered_by',
    'hosts',
    'wraps',
    'provides_access_to',
  ]),
  recipe: null,
  vendor: null,
  mirror: new Set(['domestic_equivalent_of', 'overseas_equivalent_of']),
  compat: new Set(['integrates_with', 'compatible_with', 'commonly_used_with', 'conflicts_with']),
  learning: new Set(['prerequisite_of']),
  personal: null,
};

export function lensMeta(id: GraphLens): GraphLensMeta {
  return (
    GRAPH_LENSES.find((l) => l.id === id) ??
    GRAPH_LENSES[0] ?? {
      id: 'ecosystem',
      label: '生态全景',
      hint: '',
      layout: 'force',
    }
  );
}
