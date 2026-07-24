/** 关系类型（含反向标签）-> 中文标签 + Phosphor 图标名。见设计规范 §5.3。
 *
 * 标签描述的是「当前条目视角下，目标条目是什么」，与边类型英文名（描述 from 相对 to）对齐：
 * - `domestic_equivalent_of`（国内 → 国外）：目标是国外原版 →「国外对应」
 * - `overseas_equivalent_of`（国外 → 国内，常为上者的反向视图）：目标是国内平替 →「国内平替」
 * - `open_source_alternative_to`（开源 → 商业）：目标是商业产品 →「商业对应」
 * - `proprietary_counterpart_of`（反向）：目标是开源平替 →「开源平替」
 */
export const REL_META: Record<string, { label: string; icon: string }> = {
  alternative_to: { label: '替代品', icon: 'ArrowsLeftRight' },
  open_source_alternative_to: { label: '商业对应', icon: 'GitFork' },
  proprietary_counterpart_of: { label: '开源平替', icon: 'GitFork' },
  domestic_equivalent_of: { label: '国外对应', icon: 'GlobeSimple' },
  overseas_equivalent_of: { label: '国内平替', icon: 'MapPin' },
  succeeds: { label: '取代', icon: 'ArrowUUpRight' },
  succeeded_by: { label: '被取代', icon: 'ArrowUUpLeft' },
  deprecated_by: { label: '已被取代为', icon: 'Prohibit' },
  deprecates: { label: '取代了', icon: 'ArrowUUpRight' },
  conflicts_with: { label: '冲突', icon: 'Warning' },
  integrates_with: { label: '集成', icon: 'PuzzlePiece' },
  compatible_with: { label: '兼容', icon: 'PuzzlePiece' },
  commonly_used_with: { label: '常搭配', icon: 'LinkSimple' },
  depends_on: { label: '依赖', icon: 'TreeStructure' },
  dependency_of: { label: '被依赖', icon: 'TreeStructure' },
  powered_by: { label: '由…驱动', icon: 'Lightning' },
  powers: { label: '驱动', icon: 'Lightning' },
  built_on: { label: '构建于', icon: 'Cube' },
  foundation_of: { label: '作为基础', icon: 'Cube' },
  hosts: { label: '托管', icon: 'Cloud' },
  hosted_on: { label: '托管于', icon: 'Cloud' },
  provides_access_to: { label: '提供访问', icon: 'Plugs' },
  accessible_via: { label: '可经由', icon: 'Plugs' },
  wraps: { label: '封装', icon: 'Package' },
  wrapped_by: { label: '被封装', icon: 'Package' },
  part_of: { label: '属于', icon: 'PuzzlePiece' },
  has_part: { label: '包含', icon: 'PuzzlePiece' },
  owned_by: { label: '隶属厂商', icon: 'Buildings' },
  owns: { label: '拥有', icon: 'Buildings' },
  belongs_to_category: { label: '分类', icon: 'FolderSimple' },
  has_member: { label: '含成员', icon: 'FolderSimple' },
  bundled_in: { label: '打包于', icon: 'Package' },
  bundles: { label: '打包', icon: 'Package' },
  implements: { label: '实现', icon: 'PlugsConnected' },
  implemented_by: { label: '被实现', icon: 'PlugsConnected' },
  supports: { label: '支持', icon: 'PlugsConnected' },
  supported_by: { label: '被支持', icon: 'PlugsConnected' },
  uses_concept: { label: '涉及概念', icon: 'Lightbulb' },
  concept_used_by: { label: '概念被用于', icon: 'Lightbulb' },
  related_concept: { label: '相关概念', icon: 'Lightbulb' },
  prerequisite_of: { label: '前置于', icon: 'GraduationCap' },
  requires_knowledge: { label: '需要前置', icon: 'GraduationCap' },
  migration_path_to: { label: '迁移到', icon: 'ArrowBendUpRight' },
  migration_source_of: { label: '迁移自', icon: 'ArrowBendUpLeft' },
};

export function relMeta(key: string): { label: string; icon: string } {
  return REL_META[key] ?? { label: key, icon: 'LinkSimple' };
}
