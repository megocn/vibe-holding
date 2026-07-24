import type { ContentBundle, Id } from '@vh/core';
import { familyIdOf } from '@vh/core';
import type { KbNav } from '../components/Sidebar.tsx';

/** 由条目推导左侧图廓应选中的导航位置（跨页跳转详情时同步侧栏）。 */
export function kbNavForEntry(bundle: ContentBundle, entryId: Id): KbNav | null {
  const entry = bundle.entries.get(entryId);
  if (!entry) return null;

  if (entry.category === 'llm-family') {
    return { kind: 'family', familyId: entry.id };
  }
  if (entry.category === 'llm-line') {
    const familyId = familyIdOf(bundle.edges, entry.id);
    if (familyId) return { kind: 'family', familyId };
    return { kind: 'category', categoryId: 'llm' };
  }

  return { kind: 'category', categoryId: entry.category };
}
