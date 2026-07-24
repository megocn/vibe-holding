export type SectionId =
  | 'dashboard'
  | 'knowledge'
  | 'graph'
  | 'recipes'
  | 'compare'
  | 'intel'
  | 'credentials'
  | 'settings'
  | 'kitchen';

export interface Section {
  id: Exclude<SectionId, 'kitchen'>;
  label: string;
  icon: string;
  ready: boolean;
}

export const SECTIONS: Section[] = [
  { id: 'dashboard', label: '首页', icon: 'House', ready: true },
  { id: 'knowledge', label: '知识库', icon: 'Books', ready: true },
  { id: 'graph', label: '图谱', icon: 'Graph', ready: true },
  { id: 'recipes', label: '方案', icon: 'Stack', ready: true },
  { id: 'compare', label: '对比', icon: 'Columns', ready: true },
  { id: 'intel', label: '情报', icon: 'Newspaper', ready: true },
  { id: 'credentials', label: '凭据', icon: 'Key', ready: true },
  { id: 'settings', label: '设置', icon: 'Gear', ready: true },
];

/** Web / 窄屏隐藏凭据入口。 */
export function navSections(includeCredentials: boolean): Section[] {
  if (includeCredentials) return SECTIONS;
  return SECTIONS.filter((s) => s.id !== 'credentials');
}
