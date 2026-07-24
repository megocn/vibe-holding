import type { Id, PersonalPitfall, StackRecipe, UserData } from '@vh/core';
import { type ReactNode, createContext, useCallback, useContext, useMemo, useState } from 'react';
import {
  addPitfallIn,
  adoptStackIn,
  isFavorite as checkFavorite,
  isFollowing as checkFollowing,
  emptyUserData,
  hasAdoptedStack,
  loadUserData,
  markPitfallContributedIn,
  pitfallsForEntry,
  removePitfallIn,
  removeStackIn,
  saveUserData,
  setNoteIn,
  setRatingIn,
  toggleFavoriteIn,
  toggleFollowIn,
  updateStackIn,
  withRebuiltPersonalEdges,
} from './userdata-store.ts';

interface UserDataContextValue {
  data: UserData;
  isFavorite: (id: Id) => boolean;
  isFollowing: (id: Id) => boolean;
  getNote: (id: Id) => string;
  getRating: (id: Id) => number | null;
  toggleFavorite: (id: Id) => void;
  toggleFollow: (id: Id) => void;
  setNote: (id: Id, note: string) => void;
  setRating: (id: Id, rating: number | null) => void;
  hasAdopted: (recipeId: string) => boolean;
  adoptStack: (recipe: StackRecipe) => void;
  updateStack: (recipeId: string, patch: Partial<StackRecipe>) => void;
  removeStack: (recipeId: string) => void;
  getPitfalls: (entryId: Id) => PersonalPitfall[];
  addPitfall: (entryId: Id, text: string) => void;
  removePitfall: (pitfallId: string) => void;
  markPitfallContributed: (pitfallId: string) => void;
  rebuildPersonalEdges: () => void;
}

const UserDataContext = createContext<UserDataContextValue | null>(null);

export function UserDataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<UserData>(() => {
    try {
      return loadUserData();
    } catch {
      return emptyUserData();
    }
  });

  const commit = useCallback((next: UserData) => {
    setData(next);
    saveUserData(next);
  }, []);

  const value = useMemo<UserDataContextValue>(
    () => ({
      data,
      isFavorite: (id) => checkFavorite(data, id),
      isFollowing: (id) => checkFollowing(data, id),
      getNote: (id) => data.notes[id] ?? '',
      getRating: (id) => (data.ratings[id] != null ? Number(data.ratings[id]) : null),
      toggleFavorite: (id) => commit(toggleFavoriteIn(data, id)),
      toggleFollow: (id) => commit(toggleFollowIn(data, id)),
      setNote: (id, note) => commit(setNoteIn(data, id, note)),
      setRating: (id, rating) => commit(setRatingIn(data, id, rating)),
      hasAdopted: (recipeId) => hasAdoptedStack(data, recipeId),
      adoptStack: (recipe) => commit(adoptStackIn(data, recipe)),
      updateStack: (recipeId, patch) => commit(updateStackIn(data, recipeId, patch)),
      removeStack: (recipeId) => commit(removeStackIn(data, recipeId)),
      getPitfalls: (entryId) => pitfallsForEntry(data, entryId),
      addPitfall: (entryId, text) => commit(addPitfallIn(data, entryId, text)),
      removePitfall: (pitfallId) => commit(removePitfallIn(data, pitfallId)),
      markPitfallContributed: (pitfallId) => commit(markPitfallContributedIn(data, pitfallId)),
      rebuildPersonalEdges: () => commit(withRebuiltPersonalEdges(data)),
    }),
    [data, commit],
  );

  return <UserDataContext.Provider value={value}>{children}</UserDataContext.Provider>;
}

export function useUserData(): UserDataContextValue {
  const ctx = useContext(UserDataContext);
  if (!ctx) throw new Error('useUserData 须在 UserDataProvider 内使用');
  return ctx;
}
