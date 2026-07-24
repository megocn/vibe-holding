import type { Edge, Entry } from '@vh/core';
import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  type ContentOverlay,
  applyOverlayToRaw,
  clearOverlayEdge,
  clearOverlayEntry,
  emptyOverlay,
  exportOverlayJson,
  loadOverlay,
  overlayStats,
  removeOverlayEdge,
  saveOverlay,
  upsertOverlayEdge,
  upsertOverlayEntry,
} from './content-overlay.ts';
import { type ContentStore, assembleContent, loadContent, loadRawContent } from './data.ts';

interface ContentContextValue {
  store: ContentStore | null;
  error: string | null;
  loading: boolean;
  overlay: ContentOverlay;
  isOverridden: (id: string) => boolean;
  isEdgeOverridden: (id: string) => boolean;
  saveEntry: (entry: Entry) => void;
  revertEntry: (id: string) => void;
  saveEdge: (edge: Edge) => void;
  revertEdge: (id: string) => void;
  deleteEdge: (id: string) => void;
  clearAllOverlay: () => void;
  exportOverlay: () => string;
  overlaySummary: ReturnType<typeof overlayStats>;
}

const ContentContext = createContext<ContentContextValue | null>(null);

export function ContentProvider({ children }: { children: ReactNode }) {
  const [store, setStore] = useState<ContentStore | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [overlay, setOverlay] = useState<ContentOverlay>(() => loadOverlay());
  const [baseRaw, setBaseRaw] = useState<Awaited<ReturnType<typeof loadRawContent>> | null>(null);

  const rebuild = useCallback(
    (rawPack: Awaited<ReturnType<typeof loadRawContent>>, ov: ContentOverlay) => {
      const merged = applyOverlayToRaw(rawPack.raw, ov);
      const touchesEntries = Object.keys(ov.entries).length > 0 || ov.removedEntryIds.length > 0;
      const precomputed = touchesEntries ? undefined : rawPack.raw.searchDocs;
      setStore(assembleContent(merged, rawPack.source, precomputed));
    },
    [],
  );

  useEffect(() => {
    let cancelled = false;
    loadRawContent()
      .then((pack) => {
        if (cancelled) return;
        setBaseRaw(pack);
        const ov = loadOverlay();
        setOverlay(ov);
        rebuild(pack, ov);
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e));
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [rebuild]);

  const commitOverlay = useCallback(
    (next: ContentOverlay) => {
      setOverlay(next);
      saveOverlay(next);
      if (baseRaw) rebuild(baseRaw, next);
    },
    [baseRaw, rebuild],
  );

  const value = useMemo<ContentContextValue>(
    () => ({
      store,
      error,
      loading,
      overlay,
      isOverridden: (id) => overlay.entries[id] != null,
      isEdgeOverridden: (id) => overlay.edges[id] != null || overlay.removedEdgeIds.includes(id),
      saveEntry: (entry) => commitOverlay(upsertOverlayEntry(overlay, entry)),
      revertEntry: (id) => commitOverlay(clearOverlayEntry(overlay, id)),
      saveEdge: (edge) => commitOverlay(upsertOverlayEdge(overlay, edge)),
      revertEdge: (id) => commitOverlay(clearOverlayEdge(overlay, id)),
      deleteEdge: (id) => commitOverlay(removeOverlayEdge(overlay, id)),
      clearAllOverlay: () => commitOverlay(emptyOverlay()),
      exportOverlay: () => exportOverlayJson(overlay),
      overlaySummary: overlayStats(overlay),
    }),
    [store, error, loading, overlay, commitOverlay],
  );

  return <ContentContext.Provider value={value}>{children}</ContentContext.Provider>;
}

export function useContent(): ContentStore {
  const ctx = useContext(ContentContext);
  if (!ctx?.store) throw new Error('useContent 须在 ContentGate 内且内容已加载时调用');
  return ctx.store;
}

export function useContentStatus(): Pick<ContentContextValue, 'store' | 'error' | 'loading'> {
  const ctx = useContext(ContentContext);
  if (!ctx) throw new Error('useContentStatus 须在 ContentProvider 内');
  return { store: ctx.store, error: ctx.error, loading: ctx.loading };
}

export function useContentEditor(): Pick<
  ContentContextValue,
  | 'overlay'
  | 'isOverridden'
  | 'isEdgeOverridden'
  | 'saveEntry'
  | 'revertEntry'
  | 'saveEdge'
  | 'revertEdge'
  | 'deleteEdge'
  | 'clearAllOverlay'
  | 'exportOverlay'
  | 'overlaySummary'
> {
  const ctx = useContext(ContentContext);
  if (!ctx) throw new Error('useContentEditor 须在 ContentProvider 内');
  return {
    overlay: ctx.overlay,
    isOverridden: ctx.isOverridden,
    isEdgeOverridden: ctx.isEdgeOverridden,
    saveEntry: ctx.saveEntry,
    revertEntry: ctx.revertEntry,
    saveEdge: ctx.saveEdge,
    revertEdge: ctx.revertEdge,
    deleteEdge: ctx.deleteEdge,
    clearAllOverlay: ctx.clearAllOverlay,
    exportOverlay: ctx.exportOverlay,
    overlaySummary: ctx.overlaySummary,
  };
}

export { loadContent };
