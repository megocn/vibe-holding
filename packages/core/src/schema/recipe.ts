import { z } from 'zod';
import { Id } from './common.ts';

export const StackRecipe = z.object({
  id: Id,
  name: z.string(),
  target: z.string(),
  /** 层名 -> 条目 id，例如 { "coding-agent": "cursor" } */
  layers: z.record(z.string(), Id),
  rationaleMd: z.string(),
  estimatedCost: z.string().optional(),
  caveats: z.array(z.string()).default([]),
});
export type StackRecipe = z.infer<typeof StackRecipe>;
