import type { Category, Entry, Id, RankingSystem } from '@vh/core';
import {
  entryRankingForSystem,
  formatRankingPrimary,
  leavesOfSection,
  primaryRankingSystem,
} from '@vh/core';
import { CATEGORY_LAYERS, layerOfCategory } from '@vh/ui';
import { useEffect, useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import type { KbNav } from './CategoryBrowser.tsx';

interface LeafJourneyStripProps {
  leaf: Category;
  categories: Category[];
  /** 当前叶条目（已按主榜/流行度排好）；图上名录快跳，中栏完整扫阅 */
  entries: Entry[];
  /** 如「按 LMArena 排序」；与中栏同源逻辑 */
  rankSortHint?: string;
  onNav?: (nav: KbNav) => void;
  onSelectEntry?: (id: Id) => void;
  /** 与中栏列表双向 hover */
  hoverId?: Id | null;
  onHoverEntry?: (id: Id | null) => void;
}

type Dim = 'ghost' | 'far' | 'near' | 'focus';

/**
 * 上线路程：前后图廓阶段 → 同卷兄弟叶 → 本叶基建落点名录。
 * 条目层是「排名名录/快跳」，中栏仍是完整扫阅（榜、筛选、对比）。
 */
export function LeafJourneyStrip({
  leaf,
  categories,
  entries,
  rankSortHint,
  onNav,
  onSelectEntry,
  hoverId = null,
  onHoverEntry,
}: LeafJourneyStripProps) {
  const { bundle } = useContent();
  const rankingSystems = useMemo(
    () => [...bundle.rankingSystems.values()],
    [bundle.rankingSystems],
  );
  const primarySys = useMemo(
    () => primaryRankingSystem(rankingSystems, leaf.id),
    [rankingSystems, leaf.id],
  );

  // 从中栏 hover 过来时滚到对应落点
  useEffect(() => {
    if (!hoverId) return;
    const el = document.querySelector<HTMLElement>(
      `.vh-journey-spots [data-entry-id="${CSS.escape(hoverId)}"]`,
    );
    el?.scrollIntoView({ block: 'nearest', behavior: 'smooth', inline: 'nearest' });
  }, [hoverId]);

  const sectionId = leaf.parent;
  if (!sectionId) return null;

  const sections = categories
    .filter((c) => c.kind === 'section')
    .sort((a, b) => a.order - b.order);

  const idx = sections.findIndex((s) => s.id === sectionId);
  if (idx < 0) return null;

  const layer = layerOfCategory(leaf.id, categories);
  const siblingLeaves = leavesOfSection(categories, sectionId);
  const focus = sections[idx]!;

  const windowStart = Math.max(0, idx - 2);
  const windowEnd = Math.min(sections.length - 1, idx + 2);
  const showLeftEllipsis = windowStart > 0;
  const showRightEllipsis = windowEnd < sections.length - 1;
  const visible = sections.slice(windowStart, windowEnd + 1);

  const dimFor = (i: number): Dim => {
    const d = Math.abs(i - idx);
    if (d === 0) return 'focus';
    if (d === 1) return 'near';
    if (d === 2) return 'far';
    return 'ghost';
  };

  const go = (id: Id) => {
    onNav?.({ kind: 'category', categoryId: id });
  };

  const goSection = (secId: string) => {
    const leaves = leavesOfSection(categories, secId);
    const target = leaves.find((l) => l.usageMd)?.id ?? leaves[0]?.id ?? secId;
    go(target as Id);
  };

  return (
    <div className="vh-journey" aria-label="你在整条上线路上的位置">
      <section className="vh-kb-section" data-level="1">
        <h2 className="vh-kb-section-title">
          <span className="vh-kb-section-index">二</span>
          <span>路上位置</span>
        </h2>
        <div className="vh-kb-section-body">
          <p className="vh-journey-lede vh-text-xs">
            {layer?.label ?? '大阶段'}
            {focus.code ? ` · ${focus.code}` : ''}
            {' · '}
            {focus.name}
            {' → '}
            <em>{leaf.name}</em>
          </p>

          <div className="vh-journey-level vh-journey-level-stages">
            <span className="vh-journey-level-tag">前后阶段</span>
            <div className="vh-journey-track" role="list">
              {showLeftEllipsis && (
                <span className="vh-journey-ellipsis" data-dim="ghost" aria-hidden>
                  ···
                </span>
              )}
              {visible.map((sec, vi) => {
                const abs = windowStart + vi;
                const dim = dimFor(abs);
                const isFocus = abs === idx;
                return (
                  <div
                    key={sec.id}
                    className="vh-journey-step"
                    data-dim={dim}
                    data-focus={isFocus ? 'true' : undefined}
                    role="listitem"
                  >
                    <button
                      type="button"
                      className="vh-journey-node"
                      data-dim={dim}
                      data-focus={isFocus ? 'true' : undefined}
                      disabled={!onNav || isFocus}
                      onClick={() => {
                        if (!isFocus) goSection(sec.id);
                      }}
                      title={isFocus ? sec.name : `看看：${sec.name}`}
                    >
                      <span className="vh-journey-code">{sec.code ?? '·'}</span>
                      <span className="vh-journey-pin" aria-hidden />
                      <span className="vh-journey-name">{shortName(sec.name, dim)}</span>
                    </button>
                  </div>
                );
              })}
              {showRightEllipsis && (
                <span className="vh-journey-ellipsis" data-dim="ghost" aria-hidden>
                  ···
                </span>
              )}
            </div>
          </div>

          {siblingLeaves.length > 0 && (
            <div className="vh-journey-level">
              <span className="vh-journey-level-tag">同一大类下的小类</span>
              <div className="vh-journey-leaves" role="list">
                {siblingLeaves.map((sib) => {
                  const on = sib.id === leaf.id;
                  return (
                    <button
                      key={sib.id}
                      type="button"
                      role="listitem"
                      className="vh-journey-leaf"
                      data-on={on ? 'true' : undefined}
                      disabled={on || !onNav}
                      onClick={() => go(sib.id as Id)}
                      title={on ? sib.name : `切到：${sib.name}`}
                    >
                      <span className="vh-journey-leaf-dot" aria-hidden />
                      <span className="vh-journey-leaf-label">{sib.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          <div className="vh-journey-spine" aria-hidden>
            {CATEGORY_LAYERS.map((L) => {
              const active = L.id === layer?.id;
              return (
                <span
                  key={L.id}
                  className="vh-journey-spine-seg"
                  data-active={active ? 'true' : undefined}
                  title={L.label}
                />
              );
            })}
          </div>
        </div>
      </section>

      <section className="vh-kb-section vh-journey-section-entries" data-level="1">
        <h2 className="vh-kb-section-title">
          <span className="vh-kb-section-index">三</span>
          <span>基建落点</span>
          {entries.length > 0 && (
            <span className="vh-journey-spot-count vh-mono">{entries.length}</span>
          )}
        </h2>
        <div className="vh-kb-section-body">
          <div className="vh-journey-entries-head">
            <span className="vh-journey-entries-cue">
              {rankSortHint ? (
                <span className="vh-journey-entries-sort">{rankSortHint}</span>
              ) : (
                '按序排列'
              )}
              <span className="vh-journey-entries-sep" aria-hidden>
                ·
              </span>
              领读前三 · 余名流水 · 说明在中栏
            </span>
          </div>

          {entries.length === 0 ? (
            <p className="vh-journey-entries-empty">这一类暂时还没有收录产品</p>
          ) : (
            <div className="vh-journey-spots" aria-label="本叶基建落点（已排序）">
              {entries.length >= 1 && (
                <div className="vh-journey-podium" role="list">
                  {/* 视觉 2 · 1 · 3，数据仍按排名序 */}
                  {[1, 0, 2]
                    .filter((i) => i < entries.length)
                    .map((i) => {
                      const e = entries[i]!;
                      return (
                        <LeafSpot
                          key={e.id}
                          entry={e}
                          ord={i + 1}
                          variant="podium"
                          primarySys={primarySys}
                          hoverSync={e.id === hoverId}
                          onSelect={onSelectEntry}
                          onHover={onHoverEntry}
                        />
                      );
                    })}
                </div>
              )}
              {entries.length > 3 && (
                <ol className="vh-journey-flow" role="list">
                  {entries.slice(3).map((e, j) => (
                    <LeafSpot
                      key={e.id}
                      entry={e}
                      ord={j + 4}
                      variant="flow"
                      primarySys={primarySys}
                      hoverSync={e.id === hoverId}
                      onSelect={onSelectEntry}
                      onHover={onHoverEntry}
                    />
                  ))}
                </ol>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function LeafSpot({
  entry,
  ord,
  variant,
  primarySys,
  hoverSync,
  onSelect,
  onHover,
}: {
  entry: Entry;
  ord: number;
  variant: 'podium' | 'flow';
  primarySys?: RankingSystem;
  hoverSync: boolean;
  onSelect?: (id: Id) => void;
  onHover?: (id: Id | null) => void;
}) {
  const snap = primarySys
    ? entryRankingForSystem(entry.rankings, primarySys.id)
    : undefined;
  const rankLabel =
    primarySys && snap ? formatRankingPrimary(snap, primarySys) : undefined;
  const regionHint =
    entry.region === 'domestic' ? '国内' : entry.region === 'overseas' ? '国外' : '国内外';
  const title = [
    entry.name,
    rankLabel ? `${primarySys?.shortName ?? ''} ${rankLabel}`.trim() : null,
    entry.oneLiner || null,
  ]
    .filter(Boolean)
    .join(' — ');

  if (variant === 'podium') {
    return (
      <button
        type="button"
        role="listitem"
        className="vh-journey-podium-spot"
        data-place={ord}
        data-region={entry.region}
        data-hover-sync={hoverSync ? 'true' : undefined}
        data-entry-id={entry.id}
        title={title}
        aria-label={`${ord}. ${entry.name}${rankLabel ? `，${rankLabel}` : ''}，${regionHint}`}
        onClick={() => onSelect?.(entry.id)}
        onMouseEnter={() => onHover?.(entry.id)}
        onMouseLeave={() => onHover?.(null)}
      >
        <span className="vh-journey-podium-place vh-mono" aria-hidden>
          {ord}
        </span>
        <span className="vh-journey-podium-name">{entry.name}</span>
        {rankLabel && (
          <span className="vh-journey-podium-rank vh-mono" aria-hidden>
            {rankLabel}
          </span>
        )}
      </button>
    );
  }

  return (
    <li className="vh-journey-flow-item">
      <button
        type="button"
        className="vh-journey-flow-spot"
        data-region={entry.region}
        data-hover-sync={hoverSync ? 'true' : undefined}
        data-entry-id={entry.id}
        title={title}
        aria-label={`${ord}. ${entry.name}${rankLabel ? `，${rankLabel}` : ''}，${regionHint}`}
        onClick={() => onSelect?.(entry.id)}
        onMouseEnter={() => onHover?.(entry.id)}
        onMouseLeave={() => onHover?.(null)}
      >
        <span className="vh-journey-flow-ord vh-mono" aria-hidden>
          {ord}
        </span>
        <span className="vh-journey-flow-name">{entry.name}</span>
      </button>
    </li>
  );
}

function shortName(name: string, dim: Dim): string {
  // 全宽均分后可多显示字；远端阶段仍压短降低噪声
  if (dim === 'focus' || dim === 'near') return name;
  if (dim === 'far') return name.length > 12 ? `${name.slice(0, 11)}…` : name;
  const head = name.split(/[／/·]/)[0] ?? name;
  return head.length > 8 ? `${head.slice(0, 7)}…` : head;
}
