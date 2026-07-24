import { z } from 'zod';
import { Confidence, Id, IsoDate } from './common.ts';

export const EdgeType = z.enum([
  // 竞争 / 替代
  'alternative_to',
  'open_source_alternative_to',
  'domestic_equivalent_of',
  'overseas_equivalent_of',
  'succeeds',
  'deprecated_by',
  'conflicts_with',
  // 组合 / 协作
  'integrates_with',
  'compatible_with',
  'commonly_used_with',
  'depends_on',
  'powered_by',
  'built_on',
  'hosts',
  'provides_access_to',
  'wraps',
  // 归属 / 结构
  'part_of',
  'owned_by',
  'belongs_to_category',
  'bundled_in',
  // 概念 / 学习
  'implements',
  'supports',
  'uses_concept',
  'related_concept',
  'prerequisite_of',
  'migration_path_to',
]);
export type EdgeType = z.infer<typeof EdgeType>;

export const Edge = z.object({
  id: Id,
  from: Id,
  to: Id,
  type: EdgeType,
  weight: z.number().min(0).max(1).default(0.5),
  note: z.string().optional(),
  confidence: Confidence.default('verified'),
  sources: z.array(z.string().url()).default([]),
  createdAt: IsoDate,
  lastReviewed: IsoDate.optional(),
});
export type Edge = z.infer<typeof Edge>;
