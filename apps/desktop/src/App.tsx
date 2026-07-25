import type { Id } from '@vh/core';
import { sectionIdOf } from '@vh/core';
import { CATEGORY_ICONS, CATEGORY_LAYERS, layerCategorySet, layerOfCategory } from '@vh/ui';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { BottomNav } from './components/BottomNav.tsx';
import { BrandSeal } from './components/BrandSeal.tsx';
import { type Command, CommandPalette } from './components/CommandPalette.tsx';
import { CompareView, MAX_COMPARE } from './components/CompareView.tsx';
import { CredentialsView } from './components/CredentialsView.tsx';
import { DashboardView } from './components/DashboardView.tsx';
import { Detail } from './components/Detail.tsx';
import { type EdgeEditTarget, EdgeEditor } from './components/EdgeEditor.tsx';
import { EntryEditor } from './components/EntryEditor.tsx';
import { EntryList } from './components/EntryList.tsx';
import { FilterBar } from './components/FilterBar.tsx';
import { GraphView } from './components/GraphView.tsx';
import { Icon } from './components/Icon.tsx';
import { IntelView } from './components/IntelView.tsx';
import { KbScopeHeader } from './components/KbScopeHeader.tsx';
import { KitchenSinkView } from './components/KitchenSinkView.tsx';
import { MobileRelationsView } from './components/MobileRelationsView.tsx';
import { PageFade } from './components/PageFade.tsx';
import { Placeholder } from './components/Placeholder.tsx';
import { Rail } from './components/Rail.tsx';
import { type RecipesMode, RecipesView } from './components/RecipesView.tsx';
import { RelationPanel } from './components/RelationPanel.tsx';
import { ResizeHandle } from './components/ResizeHandle.tsx';
import { SettingsView } from './components/SettingsView.tsx';
import { type KbNav, Sidebar } from './components/Sidebar.tsx';
import { WindowControls } from './components/WindowControls.tsx';
import { useContent, useContentStatus } from './lib/content.tsx';
import type { Filters } from './lib/filters.ts';
import {
  LIST_MAX,
  LIST_MIN,
  type LayoutPrefs,
  SIDEBAR_MAX,
  SIDEBAR_MIN,
  loadLayout,
  saveLayout,
} from './lib/layout.ts';
import { kbNavForEntry } from './lib/kb-nav.ts';
import { llmScopeIds } from './lib/llm-tree.ts';
import { isTauri } from './lib/platform.ts';
import {
  type Density,
  type Theme,
  applyDensity,
  applyTheme,
  initialDensity,
  initialTheme,
} from './lib/prefs.ts';
import { pushRecent } from './lib/recent.ts';
import {
  applyThemeWithTransition,
  defaultThemeOrigin,
  originFromEvent,
} from './lib/theme-transition.ts';
import { SECTIONS, type SectionId } from './lib/sections.ts';
import { useIsMobile } from './lib/use-is-mobile.ts';
import { useUserData } from './lib/userdata.tsx';

export function App() {
  const { store, loading, error } = useContentStatus();

  if (loading) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-4"
        style={{ height: '100%', color: 'var(--ink-3)', padding: 32 }}
      >
        <BrandSeal size={36} />
        <div className="vh-display" style={{ fontSize: 18, color: 'var(--ink-2)' }}>
          墨台展开中…
        </div>
        <div className="flex flex-col gap-2" style={{ width: 'min(280px, 80%)' }}>
          <div className="vh-skeleton" style={{ height: 12 }} />
          <div className="vh-skeleton" style={{ height: 12, width: '72%' }} />
          <div className="vh-skeleton" style={{ height: 12, width: '88%' }} />
        </div>
      </div>
    );
  }
  if (error || !store) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-3"
        style={{ height: '100%', color: 'var(--pigment-danger)', padding: 24 }}
      >
        <Icon name="Warning" size={32} />
        <div>内容库加载失败</div>
        <div style={{ fontSize: 13, color: 'var(--ink-3)' }}>{error ?? '未知错误'}</div>
      </div>
    );
  }

  return <AppShell />;
}

function AppShell() {
  const { bundle, index, categories } = useContent();
  const { data: userData, toggleFavorite, isFavorite, toggleFollow, isFollowing } = useUserData();
  const isMobile = useIsMobile();
  /** Web 或窄屏：隐藏凭据；内容写操作仅桌面 Tauri */
  const includeCredentials = isTauri && !isMobile;
  const canWriteContent = isTauri;
  const [view, setView] = useState<SectionId>('dashboard');
  const [query, setQuery] = useState('');
  const [kbNav, setKbNav] = useState<KbNav>({ kind: 'all' });
  const [filters, setFilters] = useState<Filters>({});
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [selectedId, setSelectedId] = useState<Id | null>(null);
  const [compareIds, setCompareIds] = useState<Id[]>([]);
  const [recipesMode, setRecipesMode] = useState<RecipesMode>('templates');
  const [editingId, setEditingId] = useState<Id | null>(null);
  const [edgeEdit, setEdgeEdit] = useState<EdgeEditTarget | null>(null);
  const [theme, setTheme] = useState<Theme>('dark');
  const [density, setDensity] = useState<Density>('comfortable');
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [layout, setLayout] = useState<LayoutPrefs>(() => loadLayout());
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [detailMode, setDetailMode] = useState<'detail' | 'graph'>('detail');
  const dragBase = useRef({ sidebar: layout.sidebarWidth, list: layout.listWidth });

  /** 固定侧栏模式（窄屏强制抽屉） */
  const sidebarDocked = !isMobile && layout.sidebarPinned;
  /** 窄屏知识库：列表与详情二选一 */
  const mobileShowDetail = isMobile && selectedId != null;

  const toggleCompare = useCallback((id: Id) => {
    setCompareIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= MAX_COMPARE) return prev;
      return [...prev, id];
    });
  }, []);

  /** 跨页打开条目：切知识库 + 同步左侧分类选中 */
  const openEntry = useCallback(
    (id: Id) => {
      const nav = kbNavForEntry(bundle, id);
      if (nav) setKbNav(nav);
      setSelectedId(id);
      setDetailMode('detail');
      setView('knowledge');
    },
    [bundle],
  );

  useEffect(() => {
    if (selectedId) pushRecent(selectedId);
  }, [selectedId]);

  useEffect(() => {
    const t = initialTheme();
    const d = initialDensity();
    setTheme(t);
    setDensity(d);
    applyTheme(t);
    applyDensity(d);
  }, []);

  const persistLayout = useCallback((next: LayoutPrefs) => {
    setLayout(next);
    saveLayout(next);
  }, []);

  const patchLayout = useCallback((partial: Partial<LayoutPrefs>) => {
    setLayout((prev) => {
      const next = { ...prev, ...partial };
      saveLayout(next);
      return next;
    });
  }, []);

  /** 窄屏强制分类抽屉，避免 dock 占宽 */
  useEffect(() => {
    if (isMobile && layout.sidebarPinned) {
      patchLayout({ sidebarPinned: false });
    }
  }, [isMobile, layout.sidebarPinned, patchLayout]);

  /** 无凭据权限时离开凭据页 */
  useEffect(() => {
    if (!includeCredentials && view === 'credentials') {
      setView('dashboard');
    }
  }, [includeCredentials, view]);

  /** Web 只读：关闭进行中的内容编辑 */
  useEffect(() => {
    if (!canWriteContent) {
      setEditingId(null);
      setEdgeEdit(null);
    }
  }, [canWriteContent]);

  const setCategoryPinned = useCallback(
    (pinned: boolean) => {
      patchLayout({ sidebarPinned: pinned });
      if (pinned) setDrawerOpen(false);
    },
    [patchLayout],
  );

  const toggleCategoryDrawer = useCallback(() => {
    if (layout.sidebarPinned) {
      patchLayout({ sidebarPinned: false });
      setDrawerOpen(true);
      return;
    }
    setDrawerOpen((o) => !o);
  }, [layout.sidebarPinned, patchLayout]);

  const setThemePref = useCallback((t: Theme, origin?: { x: number; y: number } | null) => {
    setTheme(t);
    applyThemeWithTransition(t, origin);
  }, []);
  const setDensityPref = useCallback((d: Density) => {
    setDensity(d);
    applyDensity(d);
  }, []);
  const toggleTheme = useCallback(
    (origin?: { x: number; y: number } | null) => {
      setThemePref(theme === 'dark' ? 'light' : 'dark', origin ?? defaultThemeOrigin());
    },
    [theme, setThemePref],
  );

  const results = useMemo(() => {
    // LLM 旧叶类导航统一回落到 section `llm`（侧栏已改为族›档上下层）
    let categoryFilter: Id | undefined;
    if (kbNav.kind === 'category') {
      categoryFilter =
        kbNav.categoryId === 'llm-family' || kbNav.categoryId === 'llm-line'
          ? 'llm'
          : kbNav.categoryId;
    }
    let ids = index
      .query(query, { ...filters, ...(categoryFilter ? { category: categoryFilter } : {}) })
      .map((r) => r.id);
    if (kbNav.kind === 'layer') {
      const set = layerCategorySet(kbNav.layerId);
      if (set) {
        ids = ids.filter((id) => {
          const e = bundle.entries.get(id);
          if (!e) return false;
          return set.has(sectionIdOf(categories, e.category));
        });
      }
    }
    if (kbNav.kind === 'family') {
      const scope = llmScopeIds(bundle, kbNav.familyId);
      ids = ids.filter((id) => scope.has(id));
    }
    if (favoritesOnly) ids = ids.filter((id) => userData.favorites.includes(id));
    return ids;
  }, [
    index,
    query,
    kbNav,
    filters,
    favoritesOnly,
    userData.favorites,
    bundle,
    categories,
  ]);

  const kbContext = useMemo(() => {
    if (kbNav.kind === 'all') {
      return { eyebrow: '全图', title: '全部条目', subtitle: `${results.length} 条` };
    }
    if (kbNav.kind === 'layer') {
      const layer = CATEGORY_LAYERS.find((l) => l.id === kbNav.layerId);
      return {
        eyebrow: '卷',
        title: layer?.label ?? kbNav.layerId,
        subtitle: layer ? `${layer.subtitle} · ${results.length} 条` : `${results.length} 条`,
      };
    }
    if (kbNav.kind === 'family') {
      const fam = bundle.entries.get(kbNav.familyId);
      return {
        eyebrow: '智能层 › B · LLM › 产品族',
        title: fam?.name ?? kbNav.familyId,
        subtitle: `${results.length} 条 · 族 › 档`,
      };
    }
    const cat = categories.find((c) => c.id === kbNav.categoryId);
    const layer = layerOfCategory(kbNav.categoryId, categories);
    const section =
      cat?.kind === 'leaf' && cat.parent
        ? categories.find((c) => c.id === cat.parent)
        : undefined;
    const title =
      cat?.kind === 'section' && cat.code
        ? `${cat.code} · ${cat.name}`
        : cat
          ? cat.name
          : kbNav.categoryId;
    return {
      eyebrow: section
        ? `${layer?.label ?? ''} › ${section.code ?? ''} ${section.name}`.trim()
        : layer
          ? `${layer.label} ›`
          : '分类',
      title,
      subtitle: `${results.length} 条`,
    };
  }, [kbNav, results.length, categories, bundle.entries]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((o) => !o);
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        if (view === 'knowledge') toggleCategoryDrawer();
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === '\\') {
        e.preventDefault();
        setLayout((prev) => {
          const next = { ...prev, listCollapsed: !prev.listCollapsed };
          saveLayout(next);
          return next;
        });
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [view, toggleCategoryDrawer]);

  const commands = useMemo<Command[]>(() => {
    const catName = new Map(categories.map((c) => [c.id, c.name]));
    const sectionCommands: Command[] = SECTIONS.filter(
      (s) => includeCredentials || s.id !== 'credentials',
    ).map((s) => ({
      id: `nav:${s.id}`,
      label: `前往 · ${s.label}`,
      icon: s.icon,
      keywords: `nav goto ${s.id}`,
      run: () => {
        if (s.id === 'recipes') setRecipesMode('templates');
        setView(s.id);
      },
    }));
    const entryCommands: Command[] = [...bundle.entries.values()].map((e) => ({
      id: `entry:${e.id}`,
      label: e.name,
      icon: CATEGORY_ICONS[e.category] ?? 'Circle',
      hint: catName.get(e.category),
      keywords: `${e.oneLiner} ${e.tags.join(' ')} ${e.id}`,
      run: () => {
        openEntry(e.id);
      },
    }));
    const actions: Command[] = [
      {
        id: 'action:wizard',
        label: '启动选型向导',
        icon: 'MagicWand',
        keywords: 'wizard 选型 向导 stack',
        run: () => {
          setRecipesMode('wizard');
          setView('recipes');
        },
      },
      {
        id: 'action:my-stacks',
        label: '打开我的技术栈',
        icon: 'BookmarkSimple',
        keywords: 'mystack 技术栈 my stacks',
        run: () => {
          setRecipesMode('mystacks');
          setView('recipes');
        },
      },
      {
        id: 'action:intel',
        label: '打开情报更新流',
        icon: 'Newspaper',
        keywords: 'intel 情报 更新 关注 follow',
        run: () => setView('intel'),
      },
      {
        id: 'action:kitchen',
        label: '打开组件预览（厨房水槽）',
        icon: 'PaintBrush',
        keywords: 'kitchen sink design tokens 设计 组件预览',
        run: () => setView('kitchen'),
      },
      {
        id: 'action:theme',
        label: '切换明暗主题',
        icon: theme === 'dark' ? 'Sun' : 'Moon',
        keywords: 'theme dark light 主题',
        run: () => toggleTheme(defaultThemeOrigin()),
      },
      {
        id: 'action:clear',
        label: '清除筛选与搜索',
        icon: 'X',
        keywords: 'reset clear 清除',
        run: () => {
          setQuery('');
          setKbNav({ kind: 'all' });
          setFilters({});
          setFavoritesOnly(false);
        },
      },
      {
        id: 'action:favorites',
        label: favoritesOnly ? '显示全部条目' : '只看收藏',
        icon: 'Star',
        keywords: 'favorite 收藏',
        run: () => {
          setView('knowledge');
          setFavoritesOnly((v) => !v);
        },
      },
      ...(selectedId
        ? [
            {
              id: 'action:toggle-fav-current',
              label: isFavorite(selectedId) ? '取消收藏当前条目' : '收藏当前条目',
              icon: 'Star',
              keywords: 'favorite star',
              run: () => toggleFavorite(selectedId),
            } satisfies Command,
            {
              id: 'action:toggle-follow-current',
              label: isFollowing(selectedId) ? '取消关注当前条目更新' : '关注当前条目更新',
              icon: 'Bell',
              keywords: 'follow 关注 更新',
              run: () => toggleFollow(selectedId),
            } satisfies Command,
            {
              id: 'action:toggle-compare-current',
              label: compareIds.includes(selectedId)
                ? '从对比中移除当前条目'
                : compareIds.length >= MAX_COMPARE
                  ? '对比已满（最多 4 个）'
                  : '加入对比',
              icon: 'Columns',
              keywords: 'compare 对比',
              run: () => {
                if (compareIds.includes(selectedId) || compareIds.length < MAX_COMPARE) {
                  toggleCompare(selectedId);
                }
              },
            } satisfies Command,
          ]
        : []),
      ...(compareIds.length > 0
        ? [
            {
              id: 'action:open-compare',
              label: `打开对比（已选 ${compareIds.length}）`,
              icon: 'Columns',
              keywords: 'compare 对比',
              run: () => setView('compare'),
            } satisfies Command,
            {
              id: 'action:clear-compare',
              label: '清空对比列表',
              icon: 'X',
              keywords: 'compare clear 对比',
              run: () => setCompareIds([]),
            } satisfies Command,
          ]
        : []),
      {
        id: 'action:toggle-sidebar',
        label: drawerOpen || sidebarDocked ? '关闭分类抽屉' : '打开分类抽屉',
        icon: 'TreeStructure',
        keywords: 'sidebar drawer category 分类 ⌘B',
        hint: '⌘B',
        run: () => {
          setView('knowledge');
          toggleCategoryDrawer();
        },
      },
      ...(!isMobile
        ? [
            {
              id: 'action:toggle-list',
              label: layout.listCollapsed ? '展开列表栏' : '折叠列表栏',
              icon: 'Columns',
              keywords: 'list collapse',
              hint: '⌘\\',
              run: () => patchLayout({ listCollapsed: !layout.listCollapsed }),
            } satisfies Command,
            {
              id: 'action:reset-layout',
              label: '重置布局宽度',
              icon: 'ArrowCounterClockwise',
              keywords: 'layout reset',
              run: () =>
                persistLayout({
                  sidebarWidth: 300,
                  listWidth: 340,
                  sidebarPinned: true,
                  listCollapsed: false,
                }),
            } satisfies Command,
          ]
        : []),
    ];
    return [...actions, ...sectionCommands, ...entryCommands];
  }, [
    theme,
    toggleTheme,
    bundle,
    categories,
    layout,
    patchLayout,
    persistLayout,
    favoritesOnly,
    selectedId,
    isFavorite,
    toggleFavorite,
    isFollowing,
    toggleFollow,
    compareIds,
    toggleCompare,
    drawerOpen,
    sidebarDocked,
    toggleCategoryDrawer,
    openEntry,
    includeCredentials,
    isMobile,
  ]);

  const dragProps = isTauri ? { 'data-tauri-drag-region': true } : {};

  function clamp(n: number, min: number, max: number) {
    return Math.min(max, Math.max(min, n));
  }

  return (
    <div
      className="vh-app-shell flex flex-col"
      data-mobile={isMobile ? 'true' : 'false'}
      style={{ height: '100%' }}
    >
      <header
        {...dragProps}
        className="vh-shell-header flex items-center gap-3"
        data-view={view}
        style={{
          height: 52,
          padding: '0 12px 0 16px',
          paddingTop: 'env(safe-area-inset-top, 0px)',
          flexShrink: 0,
        }}
      >
        {/* 首页 hero 已承担品牌，顶栏避免再放 logo+名称 */}
        <div className="vh-shell-brand flex items-center gap-2.5" style={{ pointerEvents: 'none' }}>
          <BrandSeal size={28} />
          <span
            className="vh-display vh-shell-brand-label"
            style={{ fontSize: 18, color: 'var(--ink-1)', letterSpacing: '0.18em' }}
          >
            墨台
          </span>
        </div>
        <div
          className="vh-shell-search"
          style={{ flex: 1, maxWidth: 520, marginLeft: view === 'dashboard' ? 0 : 16 }}
        >
          <div className="flex items-center gap-2 vh-input" style={{ padding: '6px 12px' }}>
            <Icon name="MagnifyingGlass" size={16} color="var(--ink-3)" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setView('knowledge')}
              placeholder="搜索条目、标签、说明…"
              style={{
                border: 'none',
                outline: 'none',
                background: 'transparent',
                color: 'var(--ink-1)',
                flex: 1,
                fontFamily: 'var(--font-body)',
                fontSize: 14,
              }}
            />
          </div>
        </div>
        <div className="vh-shell-header-spacer" style={{ flex: 1 }} />
        <span className="vh-mono vh-text-caption vh-shell-result-count" style={{ color: 'var(--ink-3)' }}>
          {results.length} 项
        </span>
        <button
          type="button"
          className="vh-btn"
          title={
            view === 'knowledge'
              ? drawerOpen || sidebarDocked
                ? '关闭分类抽屉 (⌘B)'
                : '打开分类抽屉 (⌘B)'
              : '分类抽屉 (⌘B)'
          }
          onClick={() => {
            setView('knowledge');
            toggleCategoryDrawer();
          }}
        >
          <Icon name="TreeStructure" size={16} />
        </button>
        <button
          type="button"
          className="vh-btn flex items-center gap-1.5"
          onClick={() => setPaletteOpen(true)}
          title="命令面板"
        >
          <Icon name="Command" size={14} />
          <span className="vh-mono vh-text-caption vh-shell-cmdk-hint">⌘K</span>
        </button>
        <button
          type="button"
          className="vh-btn"
          onClick={(e) => toggleTheme(originFromEvent(e))}
          title="切换主题"
        >
          <Icon name={theme === 'dark' ? 'Sun' : 'Moon'} size={16} />
        </button>
        {isTauri && <WindowControls />}
      </header>

      <div className="vh-shell-body flex" style={{ flex: 1, minHeight: 0 }}>
        {!isMobile && (
          <Rail
            active={view === 'kitchen' ? 'settings' : view}
            includeCredentials={includeCredentials}
            onSelect={(id) => {
              setView(id);
              if (id === 'recipes') setRecipesMode('templates');
            }}
          />
        )}

        <PageFade viewKey={view}>
          {view === 'dashboard' ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              <DashboardView
                onOpenEntry={openEntry}
                onOpenRecipes={() => {
                  setRecipesMode('templates');
                  setView('recipes');
                }}
                onOpenMyStacks={() => {
                  setRecipesMode('mystacks');
                  setView('recipes');
                }}
                onOpenKnowledge={() => setView('knowledge')}
                onOpenGraph={() => setView('graph')}
                onOpenSettings={() => setView('settings')}
                onOpenCredentials={
                  includeCredentials ? () => setView('credentials') : undefined
                }
                onOpenIntel={() => setView('intel')}
              />
            </main>
          ) : view === 'knowledge' ? (
            <>
              {sidebarDocked && (
                <>
                  <Sidebar
                    nav={kbNav}
                    onNav={setKbNav}
                    onOpenEntry={(id) => {
                      setSelectedId(id);
                      pushRecent(id);
                    }}
                    width={layout.sidebarWidth}
                    mode="dock"
                    open
                    onClose={() => setDrawerOpen(false)}
                    pinned
                    onPinChange={setCategoryPinned}
                    closeOnNavigate={false}
                  />
                  <ResizeHandle
                    title="拖拽调整分类栏宽度"
                    onResizeStart={() => {
                      dragBase.current.sidebar = layout.sidebarWidth;
                    }}
                    onResize={(dx) =>
                      setLayout((prev) => ({
                        ...prev,
                        sidebarWidth: clamp(
                          dragBase.current.sidebar + dx,
                          SIDEBAR_MIN,
                          SIDEBAR_MAX,
                        ),
                      }))
                    }
                    onResizeEnd={() =>
                      setLayout((prev) => {
                        saveLayout(prev);
                        return prev;
                      })
                    }
                  />
                </>
              )}
              {!sidebarDocked && (
                <Sidebar
                  nav={kbNav}
                  onNav={setKbNav}
                  onOpenEntry={(id) => {
                    setSelectedId(id);
                    pushRecent(id);
                  }}
                  width={
                    isMobile
                      ? Math.min(
                          typeof window !== 'undefined' ? window.innerWidth : 360,
                          360,
                        )
                      : Math.max(layout.sidebarWidth, 320)
                  }
                  mode="drawer"
                  open={drawerOpen}
                  onClose={() => setDrawerOpen(false)}
                  pinned={false}
                  onPinChange={isMobile ? undefined : setCategoryPinned}
                />
              )}
              {(!layout.listCollapsed || isMobile) && !mobileShowDetail && (
                <>
                  <div
                    className="vh-column vh-kb-list-col flex flex-col"
                    style={{
                      width: isMobile ? undefined : layout.listWidth,
                      flex: isMobile ? 1 : undefined,
                      flexShrink: isMobile ? 1 : 0,
                      minHeight: 0,
                      minWidth: 0,
                    }}
                  >
                    <div className="vh-kb-list-head">
                      <KbScopeHeader
                        nav={kbNav}
                        onNav={setKbNav}
                        countLabel={kbContext.subtitle}
                        drawerOpen={drawerOpen}
                        pinned={sidebarDocked}
                        onOpenDrawer={() => setDrawerOpen((o) => !o)}
                        onPinChange={isMobile ? undefined : setCategoryPinned}
                      />
                    </div>
                    <FilterBar
                      filters={filters}
                      onChange={setFilters}
                      favoritesOnly={favoritesOnly}
                      onFavoritesOnly={setFavoritesOnly}
                      favoriteCount={userData.favorites.length}
                    />
                    <EntryList
                      ids={results}
                      selectedId={selectedId}
                      onSelect={setSelectedId}
                      compareIds={compareIds}
                      onToggleCompare={toggleCompare}
                      nav={kbNav}
                    />
                  </div>
                  {!isMobile && (
                    <ResizeHandle
                      title="拖拽调整列表栏宽度"
                      onResizeStart={() => {
                        dragBase.current.list = layout.listWidth;
                      }}
                      onResize={(dx) =>
                        setLayout((prev) => ({
                          ...prev,
                          listWidth: clamp(dragBase.current.list + dx, LIST_MIN, LIST_MAX),
                        }))
                      }
                      onResizeEnd={() =>
                        setLayout((prev) => {
                          saveLayout(prev);
                          return prev;
                        })
                      }
                    />
                  )}
                </>
              )}
              {(!isMobile || mobileShowDetail) && (
                <main className="vh-kb-detail-col" style={{ flex: 1, minWidth: 0 }}>
                  <div className="vh-kb-detail-modebar" role="tablist" aria-label="详情视图">
                    {isMobile && (
                      <button
                        type="button"
                        className="vh-kb-detail-back vh-btn"
                        onClick={() => {
                          setSelectedId(null);
                          setDetailMode('detail');
                          setEditingId(null);
                          setEdgeEdit(null);
                        }}
                      >
                        <Icon name="ArrowLeft" size={16} />
                        返回
                      </button>
                    )}
                    <button
                      type="button"
                      role="tab"
                      aria-selected={detailMode === 'detail'}
                      className="vh-kb-detail-mode"
                      data-active={detailMode === 'detail'}
                      onClick={() => setDetailMode('detail')}
                    >
                      <Icon name="Article" size={14} />
                      详情
                    </button>
                    <button
                      type="button"
                      role="tab"
                      aria-selected={detailMode === 'graph'}
                      className="vh-kb-detail-mode"
                      data-active={detailMode === 'graph'}
                      onClick={() => setDetailMode('graph')}
                    >
                      <Icon name="Graph" size={14} />
                      {isMobile ? '关联' : '关系图'}
                    </button>
                  </div>
                  <div className="vh-kb-detail-mode-body">
                    {edgeEdit && canWriteContent ? (
                      <EdgeEditor
                        target={edgeEdit}
                        onClose={() => setEdgeEdit(null)}
                        onSaved={() => {
                          /* 保持编辑器打开以便继续调整；用户可点返回 */
                        }}
                      />
                    ) : editingId && canWriteContent ? (
                      <EntryEditor
                        entryId={editingId}
                        onClose={() => setEditingId(null)}
                        onSaved={(id) => {
                          setSelectedId(id);
                        }}
                      />
                    ) : detailMode === 'graph' ? (
                      isMobile ? (
                        selectedId ? (
                          <div className="vh-mobile-detail-relations">
                            <RelationPanel
                              id={selectedId}
                              onSelect={setSelectedId}
                            />
                          </div>
                        ) : (
                          <div style={{ padding: 24, color: 'var(--ink-3)' }}>请先选择条目</div>
                        )
                      ) : (
                        <GraphView
                          focusId={selectedId}
                          onFocus={setSelectedId}
                          onOpenInKnowledge={openEntry}
                          onCreateEdge={
                            canWriteContent
                              ? (from, to) => {
                                  setEditingId(null);
                                  setEdgeEdit({ mode: 'create', from, to });
                                }
                              : undefined
                          }
                        />
                      )
                    ) : (
                      <Detail
                        id={selectedId}
                        onSelect={setSelectedId}
                        onEdit={
                          canWriteContent
                            ? (id) => {
                                setEdgeEdit(null);
                                setEditingId(id);
                              }
                            : undefined
                        }
                        onEditEdge={
                          canWriteContent
                            ? (edgeId) => {
                                setEditingId(null);
                                setEdgeEdit({ mode: 'edit', edgeId });
                              }
                            : undefined
                        }
                        onAddEdge={
                          canWriteContent
                            ? (fromId) => {
                                setEditingId(null);
                                setEdgeEdit({ mode: 'create', from: fromId });
                              }
                            : undefined
                        }
                        inCompare={selectedId ? compareIds.includes(selectedId) : false}
                        onToggleCompare={toggleCompare}
                      />
                    )}
                  </div>
                </main>
              )}
            </>
          ) : view === 'graph' ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              {isMobile ? (
                <MobileRelationsView
                  focusId={selectedId}
                  onFocus={setSelectedId}
                  onOpenInKnowledge={openEntry}
                />
              ) : edgeEdit && canWriteContent ? (
                <EdgeEditor
                  target={edgeEdit}
                  onClose={() => setEdgeEdit(null)}
                  onSaved={() => {
                    setEdgeEdit(null);
                  }}
                />
              ) : (
                <GraphView
                  focusId={selectedId}
                  onFocus={setSelectedId}
                  onOpenInKnowledge={openEntry}
                  onCreateEdge={
                    canWriteContent
                      ? (from, to) => {
                          setEditingId(null);
                          setEdgeEdit({ mode: 'create', from, to });
                        }
                      : undefined
                  }
                />
              )}
            </main>
          ) : view === 'recipes' ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              <RecipesView
                initialMode={recipesMode}
                onOpenEntry={openEntry}
              />
            </main>
          ) : view === 'compare' ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              <CompareView
                ids={compareIds}
                onChange={setCompareIds}
                onOpenEntry={openEntry}
              />
            </main>
          ) : view === 'intel' ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              <IntelView
                onOpenEntry={openEntry}
              />
            </main>
          ) : view === 'credentials' && includeCredentials ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              <CredentialsView />
            </main>
          ) : view === 'settings' ? (
            <main style={{ flex: 1, minWidth: 0, overflowY: 'auto' }}>
              <SettingsView
                theme={theme}
                density={density}
                onTheme={setThemePref}
                onDensity={setDensityPref}
                onOpenKitchen={() => setView('kitchen')}
              />
            </main>
          ) : view === 'kitchen' ? (
            <main style={{ flex: 1, minWidth: 0 }}>
              <KitchenSinkView onBack={() => setView('settings')} />
            </main>
          ) : (
            <main style={{ flex: 1, minWidth: 0 }}>
              <Placeholder
                icon={SECTIONS.find((s) => s.id === view)?.icon ?? 'Circle'}
                title={SECTIONS.find((s) => s.id === view)?.label ?? ''}
              />
            </main>
          )}
        </PageFade>
      </div>

      {isMobile && (
        <BottomNav
          active={view === 'kitchen' ? 'settings' : view}
          includeCredentials={includeCredentials}
          onSelect={(id) => {
            setView(id);
            if (id === 'recipes') setRecipesMode('templates');
          }}
        />
      )}

      {compareIds.length > 0 && view !== 'compare' && (
        <div
          className="vh-compare-bar flex items-center gap-3"
          style={{
            position: 'fixed',
            bottom: isMobile ? 'calc(64px + env(safe-area-inset-bottom, 0px))' : 20,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 40,
            padding: '10px 16px',
            background: 'var(--paper-1)',
            border: '1px solid var(--line)',
            borderRadius: 10,
            boxShadow: '0 8px 24px color-mix(in oklch, var(--ink-1) 12%, transparent)',
            maxWidth: 'min(560px, calc(100vw - 32px))',
          }}
        >
          <Icon name="Columns" size={16} color="var(--pigment-primary)" />
          <span style={{ fontSize: 13, color: 'var(--ink-1)' }}>
            已选对比 {compareIds.length}/{MAX_COMPARE}
          </span>
          <div className="flex flex-wrap gap-1" style={{ flex: 1, minWidth: 0 }}>
            {compareIds.map((id) => {
              const name = bundle.entries.get(id)?.name ?? id;
              return (
                <button
                  key={id}
                  type="button"
                  className="vh-btn"
                  style={{ padding: '2px 8px', fontSize: 12 }}
                  onClick={() => toggleCompare(id)}
                  title="移出对比"
                >
                  {name} ×
                </button>
              );
            })}
          </div>
          <button type="button" className="vh-btn" onClick={() => setCompareIds([])}>
            清空
          </button>
          <button
            type="button"
            className="vh-btn"
            style={{
              background: 'var(--pigment-primary)',
              color: 'var(--paper-0)',
              borderColor: 'var(--pigment-primary)',
            }}
            onClick={() => setView('compare')}
          >
            查看对比
          </button>
        </div>
      )}

      <CommandPalette
        open={paletteOpen}
        commands={commands}
        onClose={() => setPaletteOpen(false)}
      />
    </div>
  );
}
