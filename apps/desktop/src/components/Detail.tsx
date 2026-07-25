import type { Entry, Id } from '@vh/core';
import {
  buildConceptTermRules,
  linkifyConcepts,
  resolveExternalLinks,
  resolveTutorialLinks,
} from '@vh/core';
import { CATEGORY_ICONS, layerOfCategory } from '@vh/ui';
import { AnimatePresence, motion } from 'motion/react';
import { type ReactNode, useEffect, useMemo, useRef, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { useContentEditor } from '../lib/content.tsx';
import { STALE_DAYS, formatReviewedLabel, isStale } from '../lib/intel.ts';
import { EASE_STANDARD, useMotionPrefs } from '../lib/motion.ts';
import { useIsMobile } from '../lib/use-is-mobile.ts';
import { ConceptPopover } from './ConceptPopover.tsx';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';
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
  onSelect: (id: Id) => void;
  onEdit?: (id: Id) => void;
  onEditEdge?: (edgeId: Id) => void;
  onAddEdge?: (fromId: Id) => void;
  inCompare?: boolean;
  onToggleCompare?: (id: Id) => void;
}

export function Detail({
  id,
  onSelect,
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
            <Prose text={entry.descriptionMd} />
          </Section>

          <Section level={2} title="权威排行" index="榜">
            <RankingsPanel categoryId={entry.category} rankings={entry.rankings} />
          </Section>

          {entry.pricing.notes && (
            <Section level={2} title="定价" index="二">
              <div style={{ color: 'var(--ink-2)' }}>{entry.pricing.notes}</div>
            </Section>
          )}

          {entry.usageGuideMd && (
            <Section level={2} title="使用方式" index="三">
              <Prose text={entry.usageGuideMd} />
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
      <div className="vh-kb-detail-oneliner">{entry.oneLiner}</div>

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

function Prose({ text }: { text: string }) {
  const { bundle } = useContent();
  const rules = useMemo(
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

  return (
    <div className="vh-prose">
      {text.split('\n').map((line, i) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 纯文本行渲染
        <p key={i}>
          {line
            ? linkifyConcepts(line, [], rules).map((seg, j) =>
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
              )
            : null}
        </p>
      ))}
    </div>
  );
}
