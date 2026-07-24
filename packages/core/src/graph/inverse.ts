import type { EdgeType } from '../schema/edge.ts';

/**
 * 关系反向映射（SPEC 附录 B）。
 * 'self' 表示对称关系（无需反向标签）；否则为反向关系的语义标签，
 * 反向标签仅用于「从 to 端看关系」的视图，不一定出现在 EdgeType 枚举中。
 *
 * 约定（写入方向）：
 * - `domestic_equivalent_of`：国内条目 → 国外原版（如 trae → cursor）
 * - `open_source_alternative_to`：开源平替 → 商业产品（如 appwrite → firebase）
 * 展示中文标签时描述的是「目标相对当前条目」，见桌面端 `relations.ts`。
 */
export const INVERSE: Record<EdgeType, string> = {
  // 对称
  alternative_to: 'self',
  commonly_used_with: 'self',
  conflicts_with: 'self',
  integrates_with: 'self',
  compatible_with: 'self',
  related_concept: 'self',
  // 有向（互逆）
  open_source_alternative_to: 'proprietary_counterpart_of',
  domestic_equivalent_of: 'overseas_equivalent_of',
  overseas_equivalent_of: 'domestic_equivalent_of',
  succeeds: 'succeeded_by',
  deprecated_by: 'deprecates',
  depends_on: 'dependency_of',
  powered_by: 'powers',
  built_on: 'foundation_of',
  hosts: 'hosted_on',
  provides_access_to: 'accessible_via',
  wraps: 'wrapped_by',
  part_of: 'has_part',
  owned_by: 'owns',
  belongs_to_category: 'has_member',
  bundled_in: 'bundles',
  implements: 'implemented_by',
  supports: 'supported_by',
  uses_concept: 'concept_used_by',
  prerequisite_of: 'requires_knowledge',
  migration_path_to: 'migration_source_of',
};

export function isSymmetric(type: EdgeType): boolean {
  return INVERSE[type] === 'self';
}
