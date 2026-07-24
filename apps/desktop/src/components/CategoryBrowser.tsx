import type { Category, Id } from '@vh/core';
import { leavesOfSection, sectionIdOf } from '@vh/core';
import { CATEGORY_ICONS, CATEGORY_LAYERS, layerOfCategory } from '@vh/ui';
import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { useContent } from '../lib/content.tsx';
import { buildLlmFamilyTree } from '../lib/llm-tree.ts';
import { Icon } from './Icon.tsx';

export type KbNav =
  | { kind: 'all' }
  | { kind: 'layer'; layerId: string }
  | { kind: 'category'; categoryId: Id }
  | { kind: 'family'; familyId: Id };

interface CategoryBrowserProps {
  nav: KbNav;
  onNav: (nav: KbNav) => void;
  onOpenEntry?: (id: Id) => void;
  width: number;
  mode: 'dock' | 'drawer';
  open: boolean;
  onClose: () => void;
  pinned: boolean;
  onPinChange?: (pinned: boolean) => void;
  closeOnNavigate?: boolean;
}

/**
 * 图廓浏览器：卷 → section → 叶类 列表树（固定侧栏与浮层抽屉均用列表，不用导图）。
 */
export function CategoryBrowser({
  nav,
  onNav,
  onOpenEntry,
  width,
  mode,
  open,
  onClose,
  pinned,
  onPinChange,
  closeOnNavigate = true,
}: CategoryBrowserProps) {
  const { categories, categoryCount, bundle } = useContent();
  const catById = useMemo(() => new Map(categories.map((c) => [c.id, c])), [categories]);
  const llmTree = useMemo(() => buildLlmFamilyTree(bundle), [bundle]);
  const [query, setQuery] = useState('');
  /** null = 全图概览（七卷），非 null = 某卷的 section 列表 */
  const [browseLayerId, setBrowseLayerId] = useState<string | null>(() =>
    resolveLayerId(nav, categories),
  );
  const [llmOpen, setLlmOpen] = useState(true);
  /** 全图模式下已展开的卷（默认全开，露出 section 一级） */
  const [openVolumes, setOpenVolumes] = useState<ReadonlySet<string>>(
    () => new Set(CATEGORY_LAYERS.map((l) => l.id)),
  );

  useEffect(() => {
    setBrowseLayerId(resolveLayerId(nav, categories));
  }, [nav, categories]);

  useEffect(() => {
    if (mode !== 'drawer' || !open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [mode, open, onClose]);

  const isAllBrowse = browseLayerId == null;
  const activeLayer = isAllBrowse
    ? null
    : (CATEGORY_LAYERS.find((l) => l.id === browseLayerId) ?? null);
  const q = query.trim().toLowerCase();

  const volumeRows = useMemo(() => {
    return CATEGORY_LAYERS.map((layer) => {
      const sections = layer.categories
        .map((sid) => {
          const section = catById.get(sid);
          if (!section || section.kind !== 'section') return null;
          const count =
            sid === 'llm'
              ? llmTree.reduce((n, node) => n + 1 + node.lineIds.length, 0)
              : (categoryCount[sid] ?? 0);
          return { sid, section, count };
        })
        .filter((x): x is NonNullable<typeof x> => x != null);

      const filteredSections = q
        ? sections.filter(({ sid, section }) => {
            const hay = `${section.code ?? ''} ${section.name}`.toLowerCase();
            if (hay.includes(q)) return true;
            if (sid === 'llm') {
              return llmTree.some(
                (n) =>
                  n.familyName.toLowerCase().includes(q) ||
                  n.lineIds.some((id) =>
                    (bundle.entries.get(id)?.name ?? '').toLowerCase().includes(q),
                  ),
              );
            }
            return false;
          })
        : sections;

      const layerHit = !q || `${layer.label} ${layer.subtitle}`.toLowerCase().includes(q);
      if (!layerHit && filteredSections.length === 0) return null;

      const count = sections.reduce((n, s) => n + s.count, 0);
      return {
        layer,
        count,
        sections: layerHit && !q ? sections : filteredSections.length ? filteredSections : sections,
      };
    }).filter((x): x is NonNullable<typeof x> => x != null);
  }, [bundle.entries, categoryCount, catById, llmTree, q]);

  const sectionRows = useMemo(() => {
    if (!activeLayer) return [];
    return activeLayer.categories
      .map((sid) => {
        const section = catById.get(sid);
        if (!section || section.kind !== 'section') return null;
        if (q) {
          const hay = `${section.code ?? ''} ${section.name}`.toLowerCase();
          if (!hay.includes(q)) {
            if (sid === 'llm') {
              const hit = llmTree.some(
                (n) =>
                  n.familyName.toLowerCase().includes(q) ||
                  n.lineIds.some((id) =>
                    (bundle.entries.get(id)?.name ?? '').toLowerCase().includes(q),
                  ),
              );
              if (!hit) return null;
            } else return null;
          }
        }
        const leaves = leavesOfSection(categories, sid);
        const count =
          sid === 'llm'
            ? llmTree.reduce((n, node) => n + 1 + node.lineIds.length, 0)
            : (categoryCount[sid] ?? 0);
        return { section, leaves, count, sid };
      })
      .filter((x): x is NonNullable<typeof x> => x != null);
  }, [activeLayer, bundle.entries, catById, categories, categoryCount, llmTree, q]);

  if (mode === 'drawer' && !open) return null;
  if (mode === 'dock' && !open) return null;

  function navigate(next: KbNav) {
    onNav(next);
    if (mode === 'drawer' && closeOnNavigate && !pinned) onClose();
  }

  const listBody = (
    <div className="vh-kb-atlas-body">
      <nav className="vh-kb-atlas-volumes" aria-label="卷">
        <button
          type="button"
          className="vh-kb-atlas-vol"
          data-active={nav.kind === 'all' ? 'true' : 'false'}
          onClick={() => {
            setBrowseLayerId(null);
            navigate({ kind: 'all' });
          }}
        >
          <Icon name="Books" size={16} weight={nav.kind === 'all' ? 'fill' : 'regular'} />
          <span className="vh-kb-atlas-vol-label">全图</span>
        </button>
        {CATEGORY_LAYERS.map((layer) => {
          const volActive =
            nav.kind !== 'all' &&
            (browseLayerId === layer.id ||
              (nav.kind === 'layer' && nav.layerId === layer.id));
          return (
            <button
              key={layer.id}
              type="button"
              className="vh-kb-atlas-vol"
              data-active={volActive ? 'true' : 'false'}
              title={layer.subtitle}
              onClick={() => {
                setBrowseLayerId(layer.id);
                navigate({ kind: 'layer', layerId: layer.id });
              }}
            >
              <Icon
                name={layer.icon}
                size={16}
                weight={volActive ? 'fill' : 'regular'}
              />
              <span className="vh-kb-atlas-vol-label">{layer.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="vh-kb-atlas-sections">
        {isAllBrowse ? (
          <>
            <div className="vh-kb-atlas-sec-head">
              <span className="vh-kb-atlas-sec-layer">全图</span>
              <span className="vh-kb-atlas-sec-sub">七卷 · 展开见分类</span>
              <button
                type="button"
                className="vh-kb-atlas-sec-toggle"
                onClick={() => {
                  const allOpen = CATEGORY_LAYERS.every((l) => openVolumes.has(l.id));
                  setOpenVolumes(
                    allOpen ? new Set() : new Set(CATEGORY_LAYERS.map((l) => l.id)),
                  );
                }}
              >
                {CATEGORY_LAYERS.every((l) => openVolumes.has(l.id)) ? '全部折叠' : '全部展开'}
              </button>
            </div>
            <ul className="vh-kb-atlas-sec-list">
              {volumeRows.length === 0 && <li className="vh-kb-atlas-empty">无匹配卷</li>}
              {volumeRows.map(({ layer, count, sections }) => {
                const volOpen = openVolumes.has(layer.id) || Boolean(q);
                return (
                  <li key={layer.id} className="vh-kb-atlas-sec">
                    <div className="vh-kb-atlas-sec-row">
                      <button
                        type="button"
                        className="vh-kb-atlas-sec-btn"
                        data-active="false"
                        title={layer.subtitle}
                        onClick={() => {
                          setBrowseLayerId(layer.id);
                          navigate({ kind: 'layer', layerId: layer.id });
                        }}
                      >
                        <Icon name={layer.icon} size={16} />
                        <span className="vh-kb-atlas-vol-name">{layer.label}</span>
                        <span className="vh-kb-atlas-vol-hint">{layer.subtitle}</span>
                        <span className="vh-mono vh-kb-atlas-n">{count}</span>
                      </button>
                      <button
                        type="button"
                        className="vh-kb-atlas-expand"
                        aria-expanded={volOpen}
                        aria-label={volOpen ? `折叠${layer.label}` : `展开${layer.label}`}
                        onClick={() => {
                          setOpenVolumes((prev) => {
                            const next = new Set(prev);
                            if (next.has(layer.id)) next.delete(layer.id);
                            else next.add(layer.id);
                            return next;
                          });
                        }}
                      >
                        <Icon name={volOpen ? 'CaretDown' : 'CaretRight'} size={12} />
                      </button>
                    </div>
                    {volOpen && sections.length > 0 && (
                      <ul className="vh-kb-atlas-leaves">
                        {sections.map(({ sid, section, count: secCount }) => (
                          <li key={sid}>
                            <button
                              type="button"
                              className="vh-kb-atlas-leaf"
                              data-active="false"
                              onClick={() =>
                                navigate({ kind: 'category', categoryId: sid })
                              }
                            >
                              <Icon name={CATEGORY_ICONS[sid] ?? 'Circle'} size={13} />
                              <span>
                                {section.code ? `${section.code} · ${section.name}` : section.name}
                              </span>
                              <span className="vh-mono vh-kb-atlas-n">{secCount}</span>
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                );
              })}
            </ul>
          </>
        ) : activeLayer ? (
          <>
            <div className="vh-kb-atlas-sec-head">
              <span className="vh-kb-atlas-sec-layer">{activeLayer.label}</span>
              <span className="vh-kb-atlas-sec-sub">{activeLayer.subtitle}</span>
            </div>

            <ul className="vh-kb-atlas-sec-list">
              {sectionRows.length === 0 && <li className="vh-kb-atlas-empty">无匹配分类</li>}
              {sectionRows.map(({ section, leaves, count, sid }) => {
                // 选中本 section / 其下 leaf / LLM 产品族 时，保持展开与高亮
                const sectionInPath =
                  (nav.kind === 'category' &&
                    (nav.categoryId === sid ||
                      sectionIdOf(categories, nav.categoryId) === sid)) ||
                  (nav.kind === 'family' && sid === 'llm');
                const isLlm = sid === 'llm';
                return (
                  <li key={sid} className="vh-kb-atlas-sec">
                    <div className="vh-kb-atlas-sec-row">
                      <button
                        type="button"
                        className="vh-kb-atlas-sec-btn"
                        data-active={sectionInPath ? 'true' : 'false'}
                        onClick={() => {
                          if (isLlm) setLlmOpen(true);
                          navigate({ kind: 'category', categoryId: sid });
                        }}
                      >
                        <Icon
                          name={CATEGORY_ICONS[sid] ?? 'Circle'}
                          size={16}
                          weight={sectionInPath ? 'fill' : 'regular'}
                        />
                        {section.code && (
                          <span className="vh-mono vh-kb-atlas-code">{section.code}</span>
                        )}
                        <span className="vh-kb-atlas-sec-name">{section.name}</span>
                        <span className="vh-mono vh-kb-atlas-n">{count}</span>
                      </button>
                      {isLlm && (
                        <button
                          type="button"
                          className="vh-kb-atlas-expand"
                          aria-expanded={llmOpen}
                          aria-label={llmOpen ? '折叠产品族' : '展开产品族'}
                          onClick={() => setLlmOpen((v) => !v)}
                        >
                          <Icon name={llmOpen ? 'CaretDown' : 'CaretRight'} size={12} />
                        </button>
                      )}
                    </div>

                    {!isLlm && leaves.length > 0 && sectionInPath && (
                      <ul className="vh-kb-atlas-leaves">
                        {leaves.map((leaf) => {
                          const leafActive =
                            nav.kind === 'category' && nav.categoryId === leaf.id;
                          return (
                            <li key={leaf.id}>
                              <button
                                type="button"
                                className="vh-kb-atlas-leaf"
                                data-active={leafActive ? 'true' : 'false'}
                                onClick={() =>
                                  navigate({ kind: 'category', categoryId: leaf.id })
                                }
                              >
                                <Icon
                                  name={CATEGORY_ICONS[leaf.id] ?? 'Circle'}
                                  size={13}
                                  weight={leafActive ? 'fill' : 'regular'}
                                />
                                <span>{leaf.name}</span>
                                <span className="vh-mono vh-kb-atlas-n">
                                  {categoryCount[leaf.id] ?? 0}
                                </span>
                              </button>
                            </li>
                          );
                        })}
                      </ul>
                    )}

                    {isLlm && llmOpen && (
                      <ul className="vh-kb-atlas-leaves">
                        {llmTree
                          .filter(
                            (n) =>
                              !q ||
                              n.familyName.toLowerCase().includes(q) ||
                              n.lineIds.some((id) =>
                                (bundle.entries.get(id)?.name ?? '').toLowerCase().includes(q),
                              ),
                          )
                          .map((n) => {
                            const famActive =
                              nav.kind === 'family' && nav.familyId === n.familyId;
                            return (
                              <li key={n.familyId}>
                                <button
                                  type="button"
                                  className="vh-kb-atlas-leaf"
                                  data-active={famActive ? 'true' : 'false'}
                                  onClick={() =>
                                    navigate({ kind: 'family', familyId: n.familyId })
                                  }
                                >
                                  <Icon
                                    name="TreeStructure"
                                    size={13}
                                    weight={famActive ? 'fill' : 'regular'}
                                  />
                                  <span>{n.familyName}</span>
                                  <span className="vh-mono vh-kb-atlas-n">
                                    {n.lineIds.length}
                                  </span>
                                </button>
                                {famActive &&
                                  n.lineIds.map((lid) => {
                                    const line = bundle.entries.get(lid);
                                    if (!line) return null;
                                    const label = line.currentVersion
                                      ? `${line.name} · ${line.currentVersion}`
                                      : line.name;
                                    return (
                                      <button
                                        key={lid}
                                        type="button"
                                        className="vh-kb-atlas-line"
                                        onClick={() => {
                                          navigate({
                                            kind: 'family',
                                            familyId: n.familyId,
                                          });
                                          onOpenEntry?.(lid);
                                        }}
                                      >
                                        <Icon name="GitBranch" size={12} />
                                        {label}
                                      </button>
                                    );
                                  })}
                              </li>
                            );
                          })}
                      </ul>
                    )}
                  </li>
                );
              })}
            </ul>
          </>
        ) : null}
      </div>
    </div>
  );

  const panel = (
    <aside
      className={`vh-kb-atlas vh-column${
        mode === 'drawer' ? ' vh-kb-atlas-drawer-panel' : ' vh-kb-atlas-dock'
      }`}
      style={{ width, flexShrink: 0 }}
      aria-label="图廓分区"
    >
      <header className="vh-kb-atlas-head">
        <div className="vh-kb-atlas-head-row">
          <div>
            <div className="vh-kb-eyebrow">墨台 · 图廓</div>
            <div className="vh-kb-atlas-title">按卷浏览</div>
          </div>
          <div className="vh-kb-atlas-modes" role="group" aria-label="分类栏模式">
            {onPinChange && (
              <>
                <button
                  type="button"
                  className="vh-kb-atlas-mode"
                  data-active={pinned ? 'true' : 'false'}
                  title="固定侧栏（列表树）"
                  onClick={() => onPinChange(true)}
                >
                  <Icon name="Sidebar" size={13} weight={pinned ? 'fill' : 'regular'} />
                  固定
                </button>
                <button
                  type="button"
                  className="vh-kb-atlas-mode"
                  data-active={!pinned ? 'true' : 'false'}
                  title="浮层抽屉（列表树）"
                  onClick={() => onPinChange(false)}
                >
                  <Icon name="Browsers" size={13} weight={!pinned ? 'fill' : 'regular'} />
                  抽屉
                </button>
              </>
            )}
            {mode === 'drawer' && (
              <button type="button" className="vh-btn" title="关闭 (Esc)" onClick={onClose}>
                <Icon name="X" size={14} />
              </button>
            )}
          </div>
        </div>

        <div className="vh-kb-atlas-search">
          <Icon name="MagnifyingGlass" size={14} color="var(--ink-3)" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="筛选分类、产品族…"
            aria-label="筛选分类"
          />
        </div>
      </header>

      {listBody}
    </aside>
  );

  if (mode === 'drawer') {
    return createPortal(
      <div className="vh-kb-drawer" role="dialog" aria-modal="true" aria-label="图廓分区">
        <button
          type="button"
          className="vh-kb-drawer-mask"
          aria-label="关闭分类抽屉"
          onClick={onClose}
        />
        {panel}
      </div>,
      document.body,
    );
  }

  return panel;
}

/** 全图 → null（七卷概览）；其余 → 所属卷 id */
function resolveLayerId(nav: KbNav, categories: readonly Category[]): string | null {
  const fallback = CATEGORY_LAYERS[0]?.id ?? 'intelligence';
  if (nav.kind === 'all') return null;
  if (nav.kind === 'layer') return nav.layerId;
  if (nav.kind === 'family') return 'intelligence';
  if (nav.kind === 'category') {
    return layerOfCategory(nav.categoryId, categories)?.id ?? fallback;
  }
  return fallback;
}

/** @deprecated 使用 CategoryBrowser；保留类型导出兼容 */
export { CategoryBrowser as Sidebar };
