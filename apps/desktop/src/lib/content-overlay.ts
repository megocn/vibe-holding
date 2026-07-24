import type { Edge, Entry, RawContent } from '@vh/core';
import { Edge as EdgeSchema, Entry as EntrySchema } from '@vh/core';

const KEY = 'vh-content-overlay';

export interface ContentOverlay {
  version: 1;
  /** 完整条目覆盖（新建或修改），key = entry id */
  entries: Record<string, Entry>;
  /** 从本机视图隐藏的基础库条目 id（不改磁盘） */
  removedEntryIds: string[];
  /** 完整边覆盖（新建或修改），key = edge id */
  edges: Record<string, Edge>;
  /** 从本机视图隐藏的基础库边 id */
  removedEdgeIds: string[];
}

export function emptyOverlay(): ContentOverlay {
  return { version: 1, entries: {}, removedEntryIds: [], edges: {}, removedEdgeIds: [] };
}

export function loadOverlay(): ContentOverlay {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return emptyOverlay();
    const parsed = JSON.parse(raw) as Partial<ContentOverlay>;
    if (parsed.version !== 1) return emptyOverlay();
    const entries: Record<string, Entry> = {};
    for (const [id, value] of Object.entries(parsed.entries ?? {})) {
      const r = EntrySchema.safeParse(value);
      if (r.success) entries[id] = r.data;
    }
    const edges: Record<string, Edge> = {};
    for (const [id, value] of Object.entries(parsed.edges ?? {})) {
      const r = EdgeSchema.safeParse(value);
      if (r.success) edges[id] = r.data;
    }
    return {
      version: 1,
      entries,
      removedEntryIds: Array.isArray(parsed.removedEntryIds) ? parsed.removedEntryIds : [],
      edges,
      removedEdgeIds: Array.isArray(parsed.removedEdgeIds) ? parsed.removedEdgeIds : [],
    };
  } catch {
    return emptyOverlay();
  }
}

export function saveOverlay(overlay: ContentOverlay): void {
  localStorage.setItem(KEY, JSON.stringify(overlay));
}

export function overlayStats(overlay: ContentOverlay): {
  entryOverrides: number;
  edgeOverrides: number;
  removed: number;
} {
  return {
    entryOverrides: Object.keys(overlay.entries).length,
    edgeOverrides: Object.keys(overlay.edges).length,
    removed: overlay.removedEntryIds.length + overlay.removedEdgeIds.length,
  };
}

/** 将覆盖层合并进原始内容（再交给 buildBundle 校验装配）。 */
export function applyOverlayToRaw(raw: RawContent, overlay: ContentOverlay): RawContent {
  const removedEntries = new Set(overlay.removedEntryIds);
  const entryById = new Map<string, unknown>();
  for (const e of raw.entries) {
    const id = (e as { id?: string }).id;
    if (id && !removedEntries.has(id)) entryById.set(id, e);
  }
  for (const [id, entry] of Object.entries(overlay.entries)) {
    if (!removedEntries.has(id)) entryById.set(id, entry);
  }

  const removedEdges = new Set(overlay.removedEdgeIds);
  const edgeById = new Map<string, unknown>();
  for (const e of raw.edges) {
    const id = (e as { id?: string }).id;
    if (id && !removedEdges.has(id)) edgeById.set(id, e);
  }
  for (const [id, edge] of Object.entries(overlay.edges)) {
    if (!removedEdges.has(id)) edgeById.set(id, edge);
  }

  return {
    ...raw,
    entries: [...entryById.values()],
    edges: [...edgeById.values()],
  };
}

export function upsertOverlayEntry(overlay: ContentOverlay, entry: Entry): ContentOverlay {
  return {
    ...overlay,
    entries: { ...overlay.entries, [entry.id]: entry },
    removedEntryIds: overlay.removedEntryIds.filter((x) => x !== entry.id),
  };
}

export function clearOverlayEntry(overlay: ContentOverlay, id: string): ContentOverlay {
  const entries = { ...overlay.entries };
  delete entries[id];
  return { ...overlay, entries };
}

export function upsertOverlayEdge(overlay: ContentOverlay, edge: Edge): ContentOverlay {
  return {
    ...overlay,
    edges: { ...overlay.edges, [edge.id]: edge },
    removedEdgeIds: overlay.removedEdgeIds.filter((x) => x !== edge.id),
  };
}

export function clearOverlayEdge(overlay: ContentOverlay, id: string): ContentOverlay {
  const edges = { ...overlay.edges };
  delete edges[id];
  return { ...overlay, edges };
}

/** 隐藏基础库边（若仅是覆盖层边则直接删除覆盖）。 */
export function removeOverlayEdge(overlay: ContentOverlay, id: string): ContentOverlay {
  const edges = { ...overlay.edges };
  const wasLocalOnly = edges[id] != null;
  delete edges[id];
  const removedEdgeIds = wasLocalOnly
    ? overlay.removedEdgeIds.filter((x) => x !== id)
    : overlay.removedEdgeIds.includes(id)
      ? overlay.removedEdgeIds
      : [...overlay.removedEdgeIds, id];
  return { ...overlay, edges, removedEdgeIds };
}

export function exportOverlayJson(overlay: ContentOverlay): string {
  return `${JSON.stringify(overlay, null, 2)}\n`;
}
