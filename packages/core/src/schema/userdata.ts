import { z } from 'zod';
import { Id, IsoDate } from './common.ts';
import { Edge } from './edge.ts';
import { StackRecipe } from './recipe.ts';

/** 个人踩坑记录（私有；可显式贡献到本地条目覆盖）。 */
export const PersonalPitfall = z.object({
  id: Id,
  entryId: Id,
  text: z.string().min(1).max(500),
  createdAt: IsoDate,
  /** 已写入本地内容覆盖的日期 */
  contributedAt: IsoDate.optional(),
});
export type PersonalPitfall = z.infer<typeof PersonalPitfall>;

/** 个人数据（本地/可 E2EE 同步）。 */
export const UserData = z.object({
  favorites: z.array(Id).default([]),
  notes: z.record(Id, z.string()).default({}),
  ratings: z.record(Id, z.number()).default({}),
  myStacks: z.array(StackRecipe.partial()).default([]),
  follows: z.array(Id).default([]),
  /** 私有推导边，不入公共内容库 */
  personalEdges: z.array(Edge).default([]),
  /** 我踩过的坑 */
  myPitfalls: z.array(PersonalPitfall).default([]),
});
export type UserData = z.infer<typeof UserData>;
