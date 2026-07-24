import {
  type ContentBundle,
  type GraphEngine,
  type Id,
  type RawContent,
  type SearchDoc,
  type SearchIndex,
  buildBundle,
  buildGraph,
  buildIndex,
  indexFromDocs,
} from '@vh/core';
import fallbackRaw from '../generated/content.json';
import {
  type ContentOverlay,
  applyOverlayToRaw,
  emptyOverlay,
  loadOverlay,
} from './content-overlay.ts';
import { ipcContentLoad } from './platform.ts';

export type ContentSource = 'ipc' | 'static';

export interface ContentStore {
  bundle: ContentBundle;
  index: SearchIndex;
  graph: GraphEngine;
  categories: ContentBundle['categories'];
  categoryCount: Record<string, number>;
  source: ContentSource;
  resolveName(id: string): string;
  isEntry(id: string): boolean;
}

/** 覆盖层是否改动了条目集合（增/改/删）；仅此时才需重建检索索引。 */
function overlayTouchesEntries(ov: ContentOverlay): boolean {
  return Object.keys(ov.entries).length > 0 || ov.removedEntryIds.length > 0;
}

/**
 * 从原始 JSON 装配完整内容库（检索索引 + 图引擎）。
 * 传入 `precomputedDocs` 时直接装配检索索引，省去重建 haystack。
 */
export function assembleContent(
  raw: RawContent,
  source: ContentSource,
  precomputedDocs?: SearchDoc[],
): ContentStore {
  const bundle = buildBundle(raw);
  const index =
    precomputedDocs && precomputedDocs.length > 0
      ? indexFromDocs(precomputedDocs, bundle.categories)
      : buildIndex(bundle);
  const graph = buildGraph(bundle);
  const categories = [...bundle.categories].sort((a, b) => a.order - b.order);
  const categoryCount: Record<string, number> = {};
  for (const e of bundle.entries.values()) {
    categoryCount[e.category] = (categoryCount[e.category] ?? 0) + 1;
  }
  // section 计数 = 下属 leaf 之和（侧栏图廓用）
  for (const cat of categories) {
    if (cat.kind !== 'leaf' || !cat.parent) continue;
    categoryCount[cat.parent] = (categoryCount[cat.parent] ?? 0) + (categoryCount[cat.id] ?? 0);
  }
  return {
    bundle,
    index,
    graph,
    categories,
    categoryCount,
    source,
    resolveName(id: Id) {
      return (
        bundle.entries.get(id)?.name ??
        bundle.vendors.get(id)?.name ??
        bundle.concepts.get(id)?.name ??
        id
      );
    },
    isEntry(id: Id) {
      return bundle.entries.has(id);
    },
  };
}

export async function loadRawContent(): Promise<{ raw: RawContent; source: ContentSource }> {
  try {
    const viaIpc = await ipcContentLoad();
    if (viaIpc != null) {
      return { raw: viaIpc as RawContent, source: 'ipc' };
    }
  } catch (err) {
    console.warn('[vh] content_load IPC 失败，回退静态内容', err);
  }
  return { raw: fallbackRaw as unknown as RawContent, source: 'static' };
}

/**
 * 加载内容并合并本地覆盖层。
 * Tauri 优先 IPC；失败/浏览器回退静态 JSON。
 */
export async function loadContent(overlay?: ContentOverlay): Promise<ContentStore> {
  const { raw, source } = await loadRawContent();
  const ov = overlay ?? loadOverlay();
  const merged = applyOverlayToRaw(raw, ov.entries ? ov : emptyOverlay());
  const precomputed = !overlayTouchesEntries(ov) ? raw.searchDocs : undefined;
  return assembleContent(merged, source, precomputed);
}
