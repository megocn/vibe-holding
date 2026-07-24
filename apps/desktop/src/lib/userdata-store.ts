import {
  type Id,
  type PersonalPitfall,
  type StackRecipe,
  type UserData,
  UserData as UserDataSchema,
  buildPersonalEdgesFromStacks,
} from '@vh/core';

const STORAGE_KEY = 'vh-userdata';

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function newPitfallId(): string {
  return `pit-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
}

/** 根据 myStacks 重建 personalEdges。 */
export function withRebuiltPersonalEdges(data: UserData): UserData {
  return {
    ...data,
    personalEdges: buildPersonalEdgesFromStacks(data.myStacks),
  };
}

export function emptyUserData(): UserData {
  return UserDataSchema.parse({});
}

/** 从 localStorage 读取并校验；损坏则回退空数据。 */
export function loadUserData(): UserData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyUserData();
    const parsed = UserDataSchema.parse(JSON.parse(raw));
    // 迁移：有栈但无个人边时补生成
    if (parsed.myStacks.length > 0 && parsed.personalEdges.length === 0) {
      return withRebuiltPersonalEdges(parsed);
    }
    return parsed;
  } catch (err) {
    console.warn('[vh] UserData 读取失败，已重置', err);
    return emptyUserData();
  }
}

/** 写入 localStorage（M1 浏览器/桌面 WebView 持久化）。
 * 后续 T-SHELL-5 可改为经 Rust IPC 写入加密 SQLite，接口保持不变。 */
export function saveUserData(data: UserData): void {
  const parsed = UserDataSchema.parse(data);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
}

export function isFavorite(data: UserData, id: Id): boolean {
  return data.favorites.includes(id);
}

export function toggleFavoriteIn(data: UserData, id: Id): UserData {
  const favorites = data.favorites.includes(id)
    ? data.favorites.filter((x) => x !== id)
    : [...data.favorites, id];
  return { ...data, favorites };
}

export function isFollowing(data: UserData, id: Id): boolean {
  return data.follows.includes(id);
}

export function toggleFollowIn(data: UserData, id: Id): UserData {
  const follows = data.follows.includes(id)
    ? data.follows.filter((x) => x !== id)
    : [...data.follows, id];
  return { ...data, follows };
}

export function setNoteIn(data: UserData, id: Id, note: string): UserData {
  const notes = { ...data.notes };
  const trimmed = note.trim();
  if (trimmed === '') delete notes[id];
  else notes[id] = note;
  return { ...data, notes };
}

/** 评分 1–5；传 0 或 undefined 清除。 */
export function setRatingIn(data: UserData, id: Id, rating: number | null): UserData {
  const ratings = { ...data.ratings };
  if (rating == null || rating < 1) delete ratings[id];
  else ratings[id] = Math.min(5, Math.max(1, Math.round(rating)));
  return { ...data, ratings };
}

/** 采用方案为我的技术栈（同 id 则覆盖）。 */
export function adoptStackIn(data: UserData, recipe: StackRecipe): UserData {
  const copy: StackRecipe = {
    ...recipe,
    layers: { ...recipe.layers },
    caveats: [...(recipe.caveats ?? [])],
  };
  const rest = data.myStacks.filter((s) => s.id !== recipe.id);
  return withRebuiltPersonalEdges({ ...data, myStacks: [...rest, copy] });
}

/** 更新已保存技术栈的字段（名称/目标/理由/注意事项等）。 */
export function updateStackIn(
  data: UserData,
  recipeId: string,
  patch: Partial<StackRecipe>,
): UserData {
  const myStacks = data.myStacks.map((s) => {
    if (s.id !== recipeId) return s;
    const next = { ...s, ...patch };
    if (patch.layers) next.layers = { ...patch.layers };
    if (patch.caveats) next.caveats = [...patch.caveats];
    return next;
  });
  const layersChanged = patch.layers != null;
  const next = { ...data, myStacks };
  return layersChanged ? withRebuiltPersonalEdges(next) : next;
}

export function removeStackIn(data: UserData, recipeId: string): UserData {
  const notes = { ...data.notes };
  const ratings = { ...data.ratings };
  delete notes[recipeId];
  delete ratings[recipeId];
  return withRebuiltPersonalEdges({
    ...data,
    myStacks: data.myStacks.filter((s) => s.id !== recipeId),
    notes,
    ratings,
  });
}

export function hasAdoptedStack(data: UserData, recipeId: string): boolean {
  return data.myStacks.some((s) => s.id === recipeId);
}

export function addPitfallIn(data: UserData, entryId: Id, text: string): UserData {
  const trimmed = text.trim();
  if (!trimmed) return data;
  const item: PersonalPitfall = {
    id: newPitfallId(),
    entryId,
    text: trimmed.slice(0, 500),
    createdAt: today(),
  };
  return { ...data, myPitfalls: [...data.myPitfalls, item] };
}

export function removePitfallIn(data: UserData, pitfallId: string): UserData {
  return {
    ...data,
    myPitfalls: data.myPitfalls.filter((p) => p.id !== pitfallId),
  };
}

export function markPitfallContributedIn(data: UserData, pitfallId: string): UserData {
  return {
    ...data,
    myPitfalls: data.myPitfalls.map((p) =>
      p.id === pitfallId ? { ...p, contributedAt: today() } : p,
    ),
  };
}

export function pitfallsForEntry(data: UserData, entryId: Id): PersonalPitfall[] {
  return data.myPitfalls.filter((p) => p.entryId === entryId);
}
