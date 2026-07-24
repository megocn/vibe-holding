import type { EdgeType } from '@vh/core';
import { colors } from '@vh/ui';

/** 关系四大分组（设计规范 §6.3 / §11.2） */
export type RelationGroup = 'substitution' | 'composition' | 'structure' | 'concept';

export type GraphThemeMode = 'light' | 'dark';

const SUBSTITUTION = new Set<string>([
  'alternative_to',
  'open_source_alternative_to',
  'domestic_equivalent_of',
  'overseas_equivalent_of',
  'succeeds',
  'deprecated_by',
  'conflicts_with',
]);
const COMPOSITION = new Set<string>([
  'integrates_with',
  'compatible_with',
  'commonly_used_with',
  'depends_on',
  'powered_by',
  'built_on',
  'hosts',
  'provides_access_to',
  'wraps',
]);
const STRUCTURE = new Set<string>(['part_of', 'owned_by', 'belongs_to_category', 'bundled_in']);
const CONCEPT = new Set<string>([
  'implements',
  'supports',
  'uses_concept',
  'related_concept',
  'prerequisite_of',
  'migration_path_to',
]);

export function relationGroup(type: EdgeType | string): RelationGroup {
  if (SUBSTITUTION.has(type)) return 'substitution';
  if (COMPOSITION.has(type)) return 'composition';
  if (STRUCTURE.has(type)) return 'structure';
  if (CONCEPT.has(type)) return 'concept';
  return 'composition';
}

export const EDGE_GROUP_LABEL: Record<RelationGroup, string> = {
  substitution: '替代',
  composition: '组合',
  structure: '归属',
  concept: '概念',
};

/** 分类色相（仅角度；明度/彩度由主题决定） */
export const CATEGORY_HUE: Record<string, number> = {
  'coding-agent': 250,
  llm: 290,
  'model-gateway': 210,
  'language-runtime': 145,
  framework: 200,
  'ui-library': 330,
  'cloud-deploy': 230,
  'database-storage': 180,
  'baas-auth': 40,
  'ai-infra': 280,
  payment: 155,
  'app-distribution': 70,
  'oss-ecosystem': 100,
  observability: 20,
  'cicd-devops': 260,
  messaging: 310,
  'analytics-growth': 130,
  'domain-dns-cdn': 220,
  'security-compliance': 25,
  'design-assets': 350,
  collaboration: 90,
  globalization: 195,
};

/**
 * 边分组色相（须彼此拉开 ≥40°，避免 composition≈structure 撞色）
 * 替代=朱赭 / 组合=石青 / 归属=墨紫 / 概念=藤黄茶
 */
export const EDGE_GROUP_HUE: Record<RelationGroup, number> = {
  substitution: 35,
  composition: 230,
  structure: 285,
  concept: 95,
};

/** 图例用：七卷各取一个代表分类色相 */
export const LEGEND_SAMPLE_CATEGORIES: readonly { id: string; label: string }[] = [
  { id: 'coding-agent', label: 'AI 编码' },
  { id: 'framework', label: '应用开发' },
  { id: 'design-assets', label: '设计' },
  { id: 'cloud-deploy', label: '云与数据' },
  { id: 'observability', label: '运维安全' },
  { id: 'payment', label: '商业增长' },
  { id: 'collaboration', label: '协作' },
];

export interface GraphPalette {
  mode: GraphThemeMode;
  /** 标签字色 */
  label: string;
  /** 标签衬底（纸色胶囊） */
  labelBg: string;
  /** 次要标签 */
  labelMuted: string;
  focus: string;
  favorite: string;
  personal: string;
  selected: string;
  clusterBorder: string;
  clusterFill: string;
  conflict: string;
  compat: string;
  mirror: string;
  region: { domestic: string; overseas: string; both: string };
  edgeGroup: Record<RelationGroup, string>;
  /** 边默认透明度（画布侧再乘） */
  edgeOpacity: number;
  maturityAlpha: Record<string, number>;
  categoryFill: (categoryId: string) => string;
  /** 分类簇色块：更浅/更透，避免灰块糊字 */
  categoryClusterFill: (categoryId: string) => string;
  fallbackFill: string;
}

/**
 * Cytoscape 自带色解析只认 hex / rgb(a) / hsl(a) / 色名，不认 oklch。
 * 传入 oklch 会静默失败变成黑，导致黑底黑字、色块发灰。
 * 此处统一转成 #rrggbb / rgba()。
 */
function oklabToSrgb(L: number, a: number, b: number): [number, number, number] {
  const l_ = L + 0.3963377774 * a + 0.2150060484 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.291485548 * b;
  const l = l_ * l_ * l_;
  const m = m_ * m_ * m_;
  const s = s_ * s_ * s_;
  let r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
  let g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
  let bl = -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s;
  const toSrgb = (x: number) => {
    const c = Math.min(1, Math.max(0, x));
    return c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
  };
  return [toSrgb(r), toSrgb(g), toSrgb(bl)];
}

/** OKLCH → Cytoscape 可用的 #rrggbb / rgba() */
export function cyOklch(l: number, c: number, h: number, alpha?: number): string {
  const hr = (h * Math.PI) / 180;
  const [r, g, b] = oklabToSrgb(l, c * Math.cos(hr), c * Math.sin(hr));
  const R = Math.round(r * 255);
  const G = Math.round(g * 255);
  const B = Math.round(b * 255);
  if (alpha != null && alpha < 1) return `rgba(${R},${G},${B},${alpha})`;
  return `#${[R, G, B].map((x) => x.toString(16).padStart(2, '0')).join('')}`;
}

const oklch = cyOklch;

/** 把 tokens 里的 oklch(...) 转成 Cytoscape 可用色；已是 hex/rgb 则原样返回。 */
export function toCyColor(color: string): string {
  const m = color
    .trim()
    .match(/^oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\s*\)$/i);
  if (!m) return color;
  const l = Number(m[1]);
  const c = Number(m[2]);
  const h = Number(m[3]);
  const a = m[4] != null ? Number(m[4]) : undefined;
  return oklch(l, c, h, a);
}

export function readDocumentTheme(): GraphThemeMode {
  if (typeof document === 'undefined') return 'light';
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
}

/**
 * 墨图图谱色板：矿物色实心点 + 纸色标签板。
 * 输出 hex/rgba，供 Cytoscape canvas 使用。
 * 暗色夜砚提高明度/彩度；边四分组色相分离且可读。
 */
export function resolveGraphPalette(mode: GraphThemeMode = readDocumentTheme()): GraphPalette {
  const t = colors[mode];
  const dark = mode === 'dark';

  // 地区环：高对比描边，一眼可辨
  const region = {
    domestic: dark ? oklch(0.8, 0.16, 28) : oklch(0.48, 0.16, 28),
    overseas: dark ? oklch(0.8, 0.11, 215) : oklch(0.48, 0.1, 215),
    both: dark ? oklch(0.78, 0.1, 232) : oklch(0.4, 0.09, 232),
  };

  // 边：色相分离 + 足够彩度（告别近灰 / composition≈structure）
  const edgeGroup: Record<RelationGroup, string> = {
    substitution: dark
      ? oklch(0.74, 0.14, EDGE_GROUP_HUE.substitution)
      : oklch(0.52, 0.14, EDGE_GROUP_HUE.substitution),
    composition: dark
      ? oklch(0.72, 0.12, EDGE_GROUP_HUE.composition)
      : oklch(0.5, 0.11, EDGE_GROUP_HUE.composition),
    structure: dark
      ? oklch(0.72, 0.12, EDGE_GROUP_HUE.structure)
      : oklch(0.48, 0.12, EDGE_GROUP_HUE.structure),
    concept: dark
      ? oklch(0.74, 0.13, EDGE_GROUP_HUE.concept)
      : oklch(0.52, 0.12, EDGE_GROUP_HUE.concept),
  };

  // 叶子节点：暗色抬高明度与彩度，避免「彩虹灰」
  const fillL = dark ? 0.7 : 0.58;
  const fillC = dark ? 0.15 : 0.13;
  // 分类簇：与叶子拉开（更深/更透）
  const clusterFillL = dark ? 0.3 : 0.9;
  const clusterFillC = dark ? 0.07 : 0.06;

  return {
    mode,
    label: dark ? oklch(0.96, 0.01, 88) : oklch(0.22, 0.015, 55),
    labelBg: dark ? oklch(0.17, 0.012, 60) : oklch(0.995, 0.002, 95),
    labelMuted: dark ? oklch(0.72, 0.01, 85) : oklch(0.42, 0.01, 58),
    focus: toCyColor(t.seal),
    favorite: toCyColor(t.warning),
    personal: toCyColor(t.success),
    selected: toCyColor(t.primary),
    clusterBorder: dark ? oklch(0.72, 0.09, 232) : oklch(0.45, 0.08, 232),
    clusterFill: dark ? oklch(0.26, 0.05, 232) : oklch(0.94, 0.04, 232),
    conflict: dark ? oklch(0.74, 0.17, 25) : oklch(0.52, 0.18, 25),
    compat: dark ? oklch(0.76, 0.13, 155) : oklch(0.52, 0.12, 155),
    mirror: dark ? oklch(0.74, 0.11, 232) : oklch(0.48, 0.1, 232),
    region,
    edgeGroup,
    edgeOpacity: dark ? 0.7 : 0.55,
    // 成熟度阶梯拉开：experimental 明显更淡
    maturityAlpha: dark
      ? { experimental: 0.45, beta: 0.65, stable: 0.85, mature: 1 }
      : { experimental: 0.5, beta: 0.7, stable: 0.88, mature: 1 },
    fallbackFill: oklch(fillL, 0.05, 90),
    categoryFill: (categoryId: string) => {
      const h = CATEGORY_HUE[categoryId] ?? 90;
      return oklch(fillL, fillC, h);
    },
    categoryClusterFill: (categoryId: string) => {
      const h = CATEGORY_HUE[categoryId] ?? 90;
      return oklch(clusterFillL, clusterFillC, h);
    },
  };
}

/** @deprecated 使用 resolveGraphPalette().edgeGroup；保留浅色默认供图例兜底 */
export const EDGE_GROUP_COLOR: Record<RelationGroup, string> =
  resolveGraphPalette('light').edgeGroup;

/** @deprecated 使用 palette.categoryFill */
export const CATEGORY_FILL: Record<string, string> = Object.fromEntries(
  Object.keys(CATEGORY_HUE).map((id) => [id, resolveGraphPalette('light').categoryFill(id)]),
);

/** @deprecated 使用 palette.region */
export const REGION_STROKE = resolveGraphPalette('light').region;

/** @deprecated 使用 palette.maturityAlpha */
export const MATURITY_ALPHA: Record<string, number> = resolveGraphPalette('light').maturityAlpha;

export function confidenceLineStyle(confidence: string): number[] {
  if (confidence === 'community') return [10, 6];
  if (confidence === 'inferred') return [3, 5];
  return [];
}

/** 厂商视图：按 vendorId 稳定取色相 */
export function vendorFill(vendorId: string, mode: GraphThemeMode): string {
  let h = 0;
  for (let i = 0; i < vendorId.length; i++) h = (h * 31 + vendorId.charCodeAt(i)) % 360;
  return mode === 'dark' ? oklch(0.7, 0.14, h) : oklch(0.58, 0.12, h);
}

/** 焦点 / 度 / 跳数 → 节点像素尺寸 */
export function nodeVisualSize(opts: {
  degree: number;
  isFocus: boolean;
  hop: number | null;
}): number {
  if (opts.isFocus) return 80;
  let size = 28 + Math.min(opts.degree, 12) * 5;
  if (opts.hop != null && opts.hop >= 2) size *= 0.8;
  return Math.round(size);
}
