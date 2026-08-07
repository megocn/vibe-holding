import type { Category, Entry, Id } from '@vh/core';
import {
  buildConceptTermRules,
  computeProminence,
  entryRankingForSystem,
  linkifyConcepts,
  primaryRankingSystem,
  resolveExternalLinks,
  resolveTutorialLinks,
  sortIdsByPrimaryRanking,
} from '@vh/core';
import { CATEGORY_ICONS, layerOfCategory } from '@vh/ui';
import { AnimatePresence, motion } from 'motion/react';
import { type ReactNode, useEffect, useMemo, useRef, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { useContentEditor } from '../lib/content.tsx';
import { STALE_DAYS, formatReviewedLabel, isStale } from '../lib/intel.ts';
import { EASE_STANDARD, useMotionPrefs } from '../lib/motion.ts';
import { useIsMobile } from '../lib/use-is-mobile.ts';
import type { KbNav } from './CategoryBrowser.tsx';
import { ConceptPopover } from './ConceptPopover.tsx';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';
import { LeafJourneyStrip } from './LeafJourneyStrip.tsx';
import { PersonalBar } from './PersonalBar.tsx';
import { PitfallsPanel } from './PitfallsPanel.tsx';
import { RankingBadges, RankingsPanel } from './RankingsPanel.tsx';
import { RelationPanel } from './RelationPanel.tsx';
import { EntryUpdatesList } from './UpdatesTimeline.tsx';
import { LineageBar } from './LineageBar.tsx';

/** 下滚超过此值收起 hero（仅收起，回顶不自动展开） */
const HERO_COLLAPSE_Y = 56;

interface DetailProps {
  id: Id | null;
  /** 无选中条目时用于展示叶级 usageMd */
  scopeNav?: KbNav;
  onScopeNav?: (nav: KbNav) => void;
  onSelect: (id: Id) => void;
  /** 与中栏列表双向 hover 的当前 id */
  hoverEntryId?: Id | null;
  onHoverEntry?: (id: Id | null) => void;
  onEdit?: (id: Id) => void;
  onEditEdge?: (edgeId: Id) => void;
  onAddEdge?: (fromId: Id) => void;
  inCompare?: boolean;
  onToggleCompare?: (id: Id) => void;
}

export function Detail({
  id,
  scopeNav,
  onScopeNav,
  onSelect,
  hoverEntryId,
  onHoverEntry,
  onEdit,
  onEditEdge,
  onAddEdge,
  inCompare,
  onToggleCompare,
}: DetailProps) {
  const { bundle, categories } = useContent();
  const { isOverridden } = useContentEditor();
  const entry = id ? bundle.entries.get(id) : undefined;
  if (!entry) {
    const leafGuide = resolveLeafGuide(scopeNav, categories);
    if (leafGuide?.usageMd) {
      return (
        <LeafUsagePanel
          category={leafGuide}
          categories={categories}
          onScopeNav={onScopeNav}
          onSelect={onSelect}
          hoverEntryId={hoverEntryId}
          onHoverEntry={onHoverEntry}
        />
      );
    }
    return (
      <EmptyState
        seal
        title="选一枚墨点"
        hint="从左侧列表点开条目，或 ⌘K 直达——详情即舆图上的一处注记。"
      />
    );
  }

  return (
    <DetailLoaded
      entry={entry}
      categories={categories}
      overridden={isOverridden(entry.id)}
      vendorName={entry.vendorId ? bundle.vendors.get(entry.vendorId)?.name : undefined}
      onSelect={onSelect}
      onEdit={onEdit}
      onEditEdge={onEditEdge}
      onAddEdge={onAddEdge}
      inCompare={inCompare}
      onToggleCompare={onToggleCompare}
    />
  );
}

/** 从 kbNav 解析可展示说明的 leaf（leaf 直接命中；section 回落该卷首叶） */
function resolveLeafGuide(
  scopeNav: KbNav | undefined,
  categories: Category[],
): Category | undefined {
  if (scopeNav?.kind !== 'category') return undefined;
  const hit = categories.find((c) => c.id === scopeNav.categoryId);
  if (!hit) return undefined;
  if (hit.kind === 'leaf' && hit.usageMd) return hit;
  if (hit.kind === 'section') {
    const leaves = categories
      .filter((c) => c.kind === 'leaf' && c.parent === hit.id)
      .sort((a, b) => a.order - b.order);
    return leaves.find((l) => l.usageMd) ?? leaves[0];
  }
  return undefined;
}

/** 选中叶、未选条目：舆图注记 + 用法 + 位置轨；落点快跳，完整扫阅仍在中栏 */
function LeafUsagePanel({
  category,
  categories,
  onScopeNav,
  onSelect,
  hoverEntryId,
  onHoverEntry,
}: {
  category: Category;
  categories: Category[];
  onScopeNav?: (nav: KbNav) => void;
  onSelect: (id: Id) => void;
  hoverEntryId?: Id | null;
  onHoverEntry?: (id: Id | null) => void;
}) {
  const { bundle, categoryCount } = useContent();
  const icon = CATEGORY_ICONS[category.id] ?? 'CirclesFour';
  const parentId = category.parent;
  const parent = parentId ? categories.find((c) => c.id === parentId) : undefined;
  const layer = layerOfCategory(category.id, categories);
  const entryCount = categoryCount[category.id] ?? 0;

  const rankingSystems = useMemo(
    () => [...bundle.rankingSystems.values()],
    [bundle.rankingSystems],
  );
  const prominence = useMemo(
    () => computeProminence(bundle.entries.values(), bundle.popularity),
    [bundle.entries, bundle.popularity],
  );

  /** 与中栏 EntryList 同源：主榜名次 → 流行度 → 成熟度 → 名称 */
  const entries = useMemo(() => {
    const inLeaf = [...bundle.entries.values()].filter((e) => e.category === category.id);
    const ordered = sortIdsByPrimaryRanking(
      inLeaf.map((e) => e.id),
      (id) => {
        const e = bundle.entries.get(id);
        if (!e) return undefined;
        return {
          category: e.category,
          name: e.name,
          rankings: e.rankings,
          maturity: e.maturity,
        };
      },
      rankingSystems,
      { prominenceOf: (id) => prominence.get(id) },
    );
    return ordered
      .map((id) => bundle.entries.get(id))
      .filter((e): e is Entry => e != null);
  }, [bundle.entries, category.id, rankingSystems, prominence]);

  const rankSortHint = useMemo(() => {
    const sys = primaryRankingSystem(rankingSystems, category.id);
    const hasSnap =
      !!sys &&
      entries.some((e) => entryRankingForSystem(e.rankings, sys.id) != null);
    if (hasSnap && sys) return `按 ${sys.shortName} 排序`;
    return '按流行度排序';
  }, [rankingSystems, category.id, entries]);

  return (
    <div className="vh-kb-detail vh-kb-leaf-usage" data-scroll-mode="unified">
      <header className="vh-kb-leaf-plate">
        <div className="vh-kb-leaf-plate-spine" aria-hidden>
          <span className="vh-kb-leaf-plate-seal">廓</span>
        </div>
        <div className="vh-kb-leaf-plate-main">
          <nav className="vh-kb-leaf-plate-path vh-text-xs" aria-label="图廓路径">
            {layer?.label && <span className="vh-kb-leaf-plate-path-seg">{layer.label}</span>}
            {parent && (
              <>
                <span className="vh-kb-leaf-plate-path-slash" aria-hidden>
                  /
                </span>
                {parent.code && (
                  <span className="vh-kb-leaf-plate-path-code vh-mono">{parent.code}</span>
                )}
                <span className="vh-kb-leaf-plate-path-seg">{parent.name}</span>
              </>
            )}
            <span className="vh-kb-leaf-plate-path-slash" aria-hidden>
              /
            </span>
            <span className="vh-kb-leaf-plate-path-here">本叶</span>
          </nav>

          <div className="vh-kb-leaf-plate-title-row">
            <span className="vh-kb-leaf-plate-icon" aria-hidden>
              <Icon name={icon} size={28} weight="duotone" />
            </span>
            <h1 className="vh-kb-leaf-plate-title">{category.name}</h1>
          </div>

          <p className="vh-kb-leaf-plate-lede">
            何时用 · 做什么 · 一般怎么用
            {entryCount > 0 ? (
              <span className="vh-kb-leaf-plate-stat">
                <strong className="vh-mono">{entryCount}</strong>
                个基建落点
              </span>
            ) : (
              <span className="vh-kb-leaf-plate-stat vh-kb-leaf-plate-stat-empty">暂无落点</span>
            )}
          </p>
        </div>
      </header>

      <section className="vh-kb-section" data-level="1">
        <h2 className="vh-kb-section-title">
          <span className="vh-kb-section-index">一</span>
          <span>这类怎么用</span>
        </h2>
        <div className="vh-kb-section-body vh-kb-leaf-usage-prose">
          <Prose text={category.usageMd ?? ''} />
        </div>
      </section>

      <LeafJourneyStrip
        leaf={category}
        categories={categories}
        entries={entries}
        rankSortHint={rankSortHint}
        onNav={onScopeNav}
        onSelectEntry={onSelect}
        hoverId={hoverEntryId}
        onHoverEntry={onHoverEntry}
      />
    </div>
  );
}

function DetailLoaded({
  entry,
  categories,
  overridden,
  vendorName,
  onSelect,
  onEdit,
  onEditEdge,
  onAddEdge,
  inCompare,
  onToggleCompare,
}: {
  entry: Entry;
  categories: ReturnType<typeof useContent>['categories'];
  overridden: boolean;
  vendorName?: string;
  onSelect: (id: Id) => void;
  onEdit?: (id: Id) => void;
  onEditEdge?: (edgeId: Id) => void;
  onAddEdge?: (fromId: Id) => void;
  inCompare?: boolean;
  onToggleCompare?: (id: Id) => void;
}) {
  const stale = isStale(entry.lastReviewed);
  const leaf = categories.find((c) => c.id === entry.category);
  const section =
    leaf?.kind === 'leaf' && leaf.parent
      ? categories.find((c) => c.id === leaf.parent)
      : leaf?.kind === 'section'
        ? leaf
        : undefined;
  const layer = layerOfCategory(entry.category, categories);
  const mobile = useIsMobile();
  const { phase, open, toggle, detailRef, bodyRef, primaryRef } = useDetailHeroScroll(
    entry.id,
    mobile,
  );

  return (
    <div
      className="vh-kb-detail"
      key={entry.id}
      ref={detailRef}
      data-scroll-mode={mobile ? 'unified' : 'split'}
    >
      <DetailHero
        entry={entry}
        layerLabel={layer?.label}
        section={section}
        leaf={leaf}
        stale={stale}
        overridden={overridden}
        phase={phase}
        open={open}
        onToggle={toggle}
        onSelect={onSelect}
        onEdit={onEdit}
        inCompare={inCompare}
        onToggleCompare={onToggleCompare}
      />

      <div className="vh-kb-detail-body" ref={bodyRef}>
        <div className="vh-kb-detail-primary" ref={primaryRef}>
         <div className="vh-kb-primary-inner">
          <PersonalBar entryId={entry.id} />

          <Section level={1} title="说明" index="一">
            <Prose text={entry.descriptionMd} protectTexts={[entry.name]} />
          </Section>

          {entry.rankings.length > 0 && (
            <Section level={2} title="权威排行" index="榜">
              <RankingsPanel categoryId={entry.category} rankings={entry.rankings} />
            </Section>
          )}

          {entry.pricing.notes && (
            <Section level={2} title="定价" index="二">
              <div style={{ color: 'var(--ink-2)' }}>{entry.pricing.notes}</div>
            </Section>
          )}

          {entry.usageGuideMd && (
            <Section level={2} title="使用方式" index="三">
              <Prose text={entry.usageGuideMd} protectTexts={[entry.name]} />
            </Section>
          )}

          {entry.pitfalls.length > 0 && (
            <Section level={2} title="坑点（公共）" index="四" tone="warning">
              <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--ink-2)' }}>
                {entry.pitfalls.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </Section>
          )}

          <Section level={2} title="我踩过的坑" index="五">
            <PitfallsPanel entryId={entry.id} />
          </Section>

          {entry.updates.length > 0 && (
            <Section level={2} title="最近更新" index="六">
              <EntryUpdatesList updates={entry.updates} />
            </Section>
          )}
         </div>
        </div>

        <aside className="vh-kb-detail-aside">
          <Section level={1} title="属性" index="录" compact>
            <AttrList entry={entry} vendorName={vendorName} stale={stale} />
          </Section>
          <Section level={1} title="关联" index="联" compact>
            <RelationPanel
              id={entry.id}
              onSelect={onSelect}
              onEditEdge={onEditEdge}
              onAddEdge={onAddEdge}
            />
          </Section>
        </aside>
      </div>
    </div>
  );
}

type HeroPhase = 'compact' | 'expanded';

type CatLike = {
  id: string;
  name: string;
  kind: string;
  code?: string;
  parent?: string;
};

/**
 * 打开条目时展开；下滚收起后保持紧凑（回顶不自动展开）。
 * 换条目才重置为展开；仍可用按钮手动展开/收起。
 * 窄屏整栏统一滚动，桌面听正文区滚动。
 */
function useDetailHeroScroll(entryId: Id, mobile: boolean) {
  const [phase, setPhase] = useState<HeroPhase>('expanded');
  const phaseRef = useRef<HeroPhase>('expanded');
  const ignoreScrollRef = useRef(false);
  const detailRef = useRef<HTMLDivElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  const primaryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ignoreScrollRef.current = false;
    phaseRef.current = 'expanded';
    setPhase('expanded');
    const detail = detailRef.current;
    const body = bodyRef.current;
    const primary = primaryRef.current;
    if (detail) detail.scrollTop = 0;
    if (body) body.scrollTop = 0;
    if (primary) primary.scrollTop = 0;
  }, [entryId, mobile]);

  useEffect(() => {
    const sync = (el: HTMLElement) => {
      if (ignoreScrollRef.current) return;
      if (el.scrollTop <= HERO_COLLAPSE_Y) return;
      if (phaseRef.current === 'compact') return;

      ignoreScrollRef.current = true;
      phaseRef.current = 'compact';
      setPhase('compact');
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          ignoreScrollRef.current = false;
        });
      });
    };

    const onScroll = (ev: Event) => {
      sync(ev.currentTarget as HTMLElement);
    };

    const nodes = (
      mobile ? [detailRef.current] : [primaryRef.current, bodyRef.current]
    ).filter((n): n is HTMLDivElement => n != null);
    for (const el of nodes) el.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      for (const el of nodes) el.removeEventListener('scroll', onScroll);
    };
  }, [entryId, mobile]);

  const toggle = () => {
    setPhase((p) => {
      const next = p === 'compact' ? 'expanded' : 'compact';
      phaseRef.current = next;
      return next;
    });
  };

  return {
    phase,
    open: phase === 'expanded',
    toggle,
    detailRef,
    bodyRef,
    primaryRef,
  };
}

function DetailHero({
  entry,
  layerLabel,
  section,
  leaf,
  stale,
  overridden,
  phase,
  open,
  onToggle,
  onSelect,
  onEdit,
  inCompare,
  onToggleCompare,
}: {
  entry: Entry;
  layerLabel?: string;
  section?: CatLike;
  leaf?: CatLike;
  stale: boolean;
  overridden: boolean;
  phase: HeroPhase;
  open: boolean;
  onToggle: () => void;
  onSelect: (id: Id) => void;
  onEdit?: (id: Id) => void;
  inCompare?: boolean;
  onToggleCompare?: (id: Id) => void;
}) {
  const { reduced } = useMotionPrefs();
  const settle = {
    duration: reduced ? 0 : 0.22,
    ease: EASE_STANDARD,
  };

  return (
    <header
      className="vh-kb-detail-hero"
      data-phase={phase}
      data-open={open ? 'true' : 'false'}
    >
      <div className="vh-kb-detail-hero-wash" aria-hidden>
        <img
          className="vh-kb-detail-hero-art"
          src="/illustrations/detail-hero.webp"
          alt=""
          width={1920}
          height={823}
          decoding="async"
        />
        <span className="vh-kb-detail-hero-veil" />
      </div>

      {(layerLabel || leaf) && (
        <div className="vh-kb-crumb">
          {layerLabel && <span>{layerLabel}</span>}
          {layerLabel && section && <span className="vh-kb-crumb-sep">›</span>}
          {section && (
            <span className="vh-kb-crumb-cat">
              {section.code ? <span className="vh-mono">{section.code}</span> : null}{' '}
              {section.name}
            </span>
          )}
          {leaf?.kind === 'leaf' && (
            <>
              <span className="vh-kb-crumb-sep">›</span>
              <span className="vh-kb-crumb-cat">{leaf.name}</span>
            </>
          )}
        </div>
      )}

      <div className="vh-kb-detail-hero-main">
        <div className="vh-kb-detail-icon">
          <Icon name={CATEGORY_ICONS[entry.category] ?? 'Circle'} size={open ? 28 : 20} weight="duotone" />
        </div>
        <div className="vh-kb-detail-hero-copy">
          <h1 className="vh-kb-detail-title">
            {entry.name}
            {overridden && (
              <span className="vh-tag" data-tone="warning" style={{ marginLeft: 8 }}>
                本地覆盖
              </span>
            )}
          </h1>
        </div>
        <div className="vh-kb-detail-actions flex gap-2">
          {onToggleCompare && (
            <button
              type="button"
              className="vh-btn flex items-center gap-1.5"
              onClick={() => onToggleCompare(entry.id)}
              style={{
                color: inCompare ? 'var(--pigment-primary)' : undefined,
                borderColor: inCompare ? 'var(--pigment-primary)' : undefined,
              }}
            >
              <Icon name="Columns" size={14} weight={inCompare ? 'fill' : 'regular'} />
              <span className="vh-kb-detail-action-label">{inCompare ? '已在对比' : '加入对比'}</span>
            </button>
          )}
          {onEdit && (
            <button
              type="button"
              className="vh-btn flex items-center gap-1.5"
              onClick={() => onEdit(entry.id)}
            >
              <Icon name="PencilSimple" size={14} />
              <span className="vh-kb-detail-action-label">编辑</span>
            </button>
          )}
          <button
            type="button"
            className="vh-btn vh-kb-detail-hero-toggle"
            onClick={onToggle}
            aria-expanded={open}
            title={open ? '收起标题区' : '展开标题区'}
          >
            <Icon name={open ? 'CaretUp' : 'CaretDown'} size={14} />
          </button>
        </div>
      </div>
      <div className="vh-kb-detail-oneliner">
        <ProseInline text={entry.oneLiner} protectTexts={[entry.name]} />
      </div>

      <div className="vh-kb-detail-tags flex flex-wrap items-center gap-2">
        <span
          className="vh-tag"
          data-tone={
            entry.region === 'domestic' ? 'seal' : entry.region === 'overseas' ? 'info' : undefined
          }
        >
          {entry.region === 'domestic' ? '国内' : entry.region === 'overseas' ? '国外' : '国内外'}
        </span>
        <span
          className="vh-tag"
          data-tone={
            entry.pricing.model === 'free' || entry.pricing.model === 'open-source'
              ? 'success'
              : entry.pricing.model === 'freemium'
                ? 'info'
                : entry.pricing.model === 'usage'
                  ? 'warning'
                  : undefined
          }
        >
          {entry.pricing.model}
        </span>
        <span
          className="vh-tag"
          data-tone={entry.availability.chinaAccessible ? 'success' : 'danger'}
        >
          {entry.availability.chinaAccessible ? '国内可访问' : '国内不可直接访问'}
        </span>
        {stale && (
          <span className="vh-tag" data-tone="warning">
            可能过时
          </span>
        )}
        {!open && (
          <span className="vh-kb-detail-links-inline">
            <a className="vh-link" href={entry.officialUrl} target="_blank" rel="noreferrer">
              官网 ↗
            </a>
            {entry.docsUrl && (
              <a className="vh-link" href={entry.docsUrl} target="_blank" rel="noreferrer">
                文档 ↗
              </a>
            )}
          </span>
        )}
      </div>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            className="vh-kb-detail-hero-extra"
            key="hero-extra"
            initial={reduced ? false : { height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={reduced ? { height: 0, opacity: 0 } : { height: 0, opacity: 0 }}
            transition={settle}
            style={{ overflow: 'hidden' }}
          >
            <LineageBar entryId={entry.id} onSelect={onSelect} />

            <div className="vh-kb-detail-links flex gap-4">
              <a className="vh-link" href={entry.officialUrl} target="_blank" rel="noreferrer">
                官网 ↗
              </a>
              {entry.docsUrl && (
                <a className="vh-link" href={entry.docsUrl} target="_blank" rel="noreferrer">
                  文档 ↗
                </a>
              )}
            </div>

            <div className="vh-kb-chip-row" aria-label="延伸">
              <span className="vh-kb-chip-label">延伸</span>
              <span className="vh-kb-chip-sep" aria-hidden>
                ·
              </span>
              {resolveExternalLinks(entry).map((x) => (
                <a
                  key={x.kind}
                  className="vh-kb-chip"
                  href={x.href}
                  target="_blank"
                  rel="noreferrer"
                  title={
                    x.note ??
                    (x.curated ? `精选 · ${x.label}` : `搜索「${entry.name}」· ${x.label}`)
                  }
                  data-curated={x.curated || undefined}
                >
                  {x.label}
                  {x.curated && <span className="vh-kb-chip-curated">精选</span>}
                </a>
              ))}
            </div>

            <div className="vh-kb-chip-row" aria-label="学教程">
              <span className="vh-kb-chip-label">学教程</span>
              <span className="vh-kb-chip-sep" aria-hidden>
                ·
              </span>
              {resolveTutorialLinks(entry).map((t) => (
                <a
                  key={t.platform}
                  className="vh-kb-chip"
                  href={t.href}
                  target="_blank"
                  rel="noreferrer"
                  title={t.note ?? (t.curated ? '精选教程' : `在${t.label}搜索「${entry.name}」`)}
                  data-curated={t.curated || undefined}
                >
                  {t.label}
                  {t.curated && <span className="vh-kb-chip-curated">精选</span>}
                </a>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

function Section({
  title,
  children,
  index,
  level = 2,
  tone,
  compact,
}: {
  title: string;
  children: ReactNode;
  index?: string;
  level?: 1 | 2;
  tone?: 'warning';
  compact?: boolean;
}) {
  return (
    <section
      className={`vh-kb-section${compact ? ' vh-kb-section-compact' : ''}`}
      data-level={level}
      data-tone={tone}
    >
      <h2 className="vh-kb-section-title">
        {index && <span className="vh-kb-section-index">{index}</span>}
        <span>{title}</span>
      </h2>
      <div className="vh-kb-section-body">{children}</div>
    </section>
  );
}

function AttrList({
  entry,
  vendorName,
  stale,
}: {
  entry: Entry;
  vendorName?: string;
  stale: boolean;
}) {
  const version = entry.currentVersion
    ? /^\d/.test(entry.currentVersion)
      ? `v${entry.currentVersion}`
      : entry.currentVersion
    : undefined;
  const gate =
    [entry.availability.needsCompany ? '需公司主体' : null, entry.availability.needsIcp ? '需备案' : null]
      .filter(Boolean) as string[];

  return (
    <dl className="vh-kb-attrs">
      {vendorName && (
        <div className="vh-kb-attr">
          <dt className="vh-kb-attr-k">厂商</dt>
          <dd className="vh-kb-attr-v">{vendorName}</dd>
        </div>
      )}
      <div className="vh-kb-attr">
        <dt className="vh-kb-attr-k">成熟度</dt>
        <dd className="vh-kb-attr-v">
          <span className="vh-tag">{entry.maturity}</span>
        </dd>
      </div>
      {version && (
        <div className="vh-kb-attr">
          <dt className="vh-kb-attr-k">版本</dt>
          <dd className="vh-kb-attr-v">
            <span className="vh-mono vh-tag" data-tone="info" title="当前推荐版本">
              {version}
            </span>
          </dd>
        </div>
      )}
      {gate.length > 0 && (
        <div className="vh-kb-attr">
          <dt className="vh-kb-attr-k">准入</dt>
          <dd className="vh-kb-attr-v">
            {gate.map((g) => (
              <span key={g} className="vh-tag">
                {g}
              </span>
            ))}
          </dd>
        </div>
      )}
      <div className="vh-kb-attr">
        <dt className="vh-kb-attr-k">复核</dt>
        <dd className="vh-kb-attr-v">
          <span
            className="vh-mono vh-tag"
            data-tone={stale ? 'warning' : undefined}
            title={`最近复核 · 超 ${STALE_DAYS} 天显示「可能过时」`}
          >
            {formatReviewedLabel(entry.lastReviewed)}
          </span>
        </dd>
      </div>
      {entry.rankings.length > 0 && (
        <div className="vh-kb-attr">
          <dt className="vh-kb-attr-k">榜单</dt>
          <dd className="vh-kb-attr-v">
            <RankingBadges rankings={entry.rankings} categoryId={entry.category} />
          </dd>
        </div>
      )}
    </dl>
  );
}

function useConceptRules() {
  const { bundle } = useContent();
  return useMemo(
    () =>
      buildConceptTermRules(
        [...bundle.concepts.values()].map((c) => ({
          id: c.id,
          name: c.name,
          aliases: c.aliases,
        })),
      ),
    [bundle.concepts],
  );
}

function linkifiedNodes(
  text: string,
  rules: ReturnType<typeof buildConceptTermRules>,
  protectTexts?: readonly string[],
) {
  return linkifyConcepts(text, [], rules, { protectTexts }).map((seg, j) =>
    seg.type === 'concept' ? (
      // biome-ignore lint/suspicious/noArrayIndexKey: 片段顺序稳定
      <ConceptPopover
        key={`${seg.conceptId}-${j}`}
        conceptId={seg.conceptId}
        className="vh-concept-term"
      >
        {seg.value}
      </ConceptPopover>
    ) : (
      // biome-ignore lint/suspicious/noArrayIndexKey: 片段顺序稳定
      <span key={j}>{seg.value}</span>
    ),
  );
}

/** 单行（如 oneLiner）内联点选，不包 prose 段落。 */
function ProseInline({
  text,
  protectTexts,
}: {
  text: string;
  protectTexts?: readonly string[];
}) {
  const rules = useConceptRules();
  if (!text) return null;
  return <>{linkifiedNodes(text, rules, protectTexts)}</>;
}

function Prose({ text, protectTexts }: { text: string; protectTexts?: readonly string[] }) {
  const rules = useConceptRules();

  return (
    <div className="vh-prose">
      {text.split('\n').map((line, i) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 纯文本行渲染
        <p key={i}>{line ? linkifiedNodes(line, rules, protectTexts) : null}</p>
      ))}
    </div>
  );
}
