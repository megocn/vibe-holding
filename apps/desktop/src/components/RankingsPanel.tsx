import type { EntryRanking, Id, RankingSystem } from '@vh/core';
import {
  formatRankingChangePhrase,
  formatRankingPrimary,
  formatRankingScore,
  primaryRankingSystem,
} from '@vh/core';
import { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useContent } from '../lib/content.tsx';
import { Icon } from './Icon.tsx';

interface RankingsPanelProps {
  categoryId: Id;
  rankings: EntryRanking[];
  /** 紧凑：用于侧栏 */
  compact?: boolean;
}

const CADENCE_LABEL: Record<string, string> = {
  weekly: '约每周更新',
  monthly: '约每月更新',
  annual: '约每年更新',
  quarterly: '约每季度更新',
  daily: '近乎每日更新',
  'ad-hoc': '不定期更新',
};

function metricHowToRead(system: RankingSystem): string {
  const unit = system.metricUnit ? `（${system.metricUnit}）` : '';
  switch (system.metric) {
    case 'rank':
      return '读法：名次越小越好，#1 为最优。';
    case 'score':
      return `读法：分值越高通常越好${unit}。`;
    case 'share':
      return '读法：占比越高表示采用越广；热度不等于能力。';
    case 'tier':
      return '读法：看档位 / 象限标签（如 Leader），而非单一名次。';
    case 'mixed':
      return `读法：常同时参考名次与分值${unit}。`;
    default:
      return '';
  }
}

/**
 * 仅展示本条目已有快照的权威排行。
 * 分类下登记了、但本条目未上榜的体系不出现在主内容（避免「暂无」占位干扰）。
 */
export function RankingsPanel({ categoryId, rankings, compact }: RankingsPanelProps) {
  const { bundle } = useContent();

  const rows = useMemo(() => {
    if (!rankings.length) return [];

    const categorySystems = [...bundle.rankingSystems.values()]
      .filter((s) => s.categories.includes(categoryId))
      .sort((a, b) => a.order - b.order || a.id.localeCompare(b.id));

    const byId = new Map(rankings.map((r) => [r.systemId, r]));
    const rows: { system: RankingSystem; ranking: EntryRanking }[] = [];

    for (const sys of categorySystems) {
      const ranking = byId.get(sys.id);
      if (ranking) rows.push({ system: sys, ranking });
    }
    // 条目上有、但未挂到本分类的体系仍展示
    for (const r of rankings) {
      if (rows.some((row) => row.system.id === r.systemId)) continue;
      const sys = bundle.rankingSystems.get(r.systemId);
      if (sys) rows.push({ system: sys, ranking: r });
    }
    return rows;
  }, [bundle.rankingSystems, categoryId, rankings]);

  if (rows.length === 0) return null;

  return (
    <div className={`vh-rankings${compact ? ' vh-rankings-compact' : ''}`}>
      <ul className="vh-rankings-list">
        {rows.map(({ system, ranking }) => (
          <RankingRow key={system.id} system={system} ranking={ranking} compact={compact} />
        ))}
      </ul>
      {!compact && (
        <p className="vh-rankings-footnote vh-text-caption">
          名次来自第三方权威榜，非墨台
          主观评分；期次与快照日见各行。选型请交叉多榜并自建评测。外链在系统浏览器打开；若
          arena.ai 仍被 Cloudflare 拦截，需换网络/节点，应用内快照可继续用不影响选型。
        </p>
      )}
    </div>
  );
}

function RankingRow({
  system,
  ranking,
  compact,
}: {
  system: RankingSystem;
  ranking: EntryRanking;
  compact?: boolean;
}) {
  const score = formatRankingScore(ranking, system);
  const change = formatRankingChangePhrase(ranking);
  const isFirst = ranking.rank === 1;
  const isTop3 = ranking.rank != null && ranking.rank <= 3;

  let rankKind: 'rank' | 'share' | 'tier' | 'score' = 'score';
  let rankText = formatRankingPrimary(ranking, system);
  let primary: string | null = null;
  let secondary: string | null = null;

  if (ranking.rank != null) {
    rankKind = 'rank';
    rankText = String(ranking.rank);
    secondary = [ranking.tier, score, change].filter(Boolean).join(' · ') || null;
  } else if (ranking.share != null) {
    rankKind = 'share';
    rankText = String(ranking.share);
    secondary = [ranking.tier, score, change].filter(Boolean).join(' · ') || null;
  } else if (ranking.tier) {
    rankKind = 'tier';
    primary = ranking.tier;
    secondary = [score, change].filter(Boolean).join(' · ') || null;
  } else if (score) {
    rankKind = 'score';
    primary = score;
    secondary = change || null;
  } else {
    primary = rankText;
    secondary = change || null;
  }

  /** 仅短数字/占比适合左侧大字；档位与长分值放正文，避免挤爆卡片。 */
  const showSideRank = rankKind === 'rank' || rankKind === 'share';

  return (
    <li
      className="vh-ranking-row"
      data-place={isFirst ? '1' : isTop3 ? 'top' : undefined}
      data-kind={rankKind}
    >
      {showSideRank && (
        <div
          className="vh-ranking-rank"
          aria-label={rankKind === 'rank' ? `第 ${rankText} 名` : undefined}
        >
          <div className="vh-ranking-rank-value">
            {rankKind === 'rank' && !isFirst && <span className="vh-ranking-hash">#</span>}
            <span className="vh-ranking-num">{rankText}</span>
            {rankKind === 'share' && <span className="vh-ranking-hash">%</span>}
          </div>
          {isFirst && <span className="vh-ranking-first-mark">榜首</span>}
        </div>
      )}
      <div className="vh-ranking-body">
        <div className="vh-ranking-main">
          <span className="vh-ranking-name">{system.shortName}</span>
          <span className="vh-ranking-brief">{system.brief}</span>
          <RankingInfoTip system={system} />
          <a
            className="vh-ranking-ext"
            href={system.url}
            target="_blank"
            rel="noreferrer"
            title={`${system.name} · ${system.authority}`}
          >
            <Icon name="ArrowSquareOut" size={11} />
          </a>
        </div>
        {primary && <div className="vh-ranking-primary">{primary}</div>}
        {secondary && <div className="vh-ranking-secondary">{secondary}</div>}
        {!compact && (
          <div className="vh-ranking-meta vh-text-caption">
            <span>{ranking.period}</span>
            <span className="vh-mono">asOf {ranking.asOf}</span>
            {ranking.sourceUrl && (
              <a className="vh-link" href={ranking.sourceUrl} target="_blank" rel="noreferrer">
                来源
              </a>
            )}
          </div>
        )}
        {!compact && ranking.note && <div className="vh-ranking-note">{ranking.note}</div>}
      </div>
    </li>
  );
}

type PopPos = { top: number; left: number; maxWidth: number };

/** 榜名旁问号：点击展开体系说明（全称 / 权威方 / 描述 / 更新节奏）。 */
function RankingInfoTip({ system }: { system: RankingSystem }) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState<PopPos | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const labelId = useId();

  const updatePos = useCallback(() => {
    const el = triggerRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const pad = 8;
    const maxWidth = Math.min(340, window.innerWidth - pad * 2);
    let left = r.left;
    if (left + maxWidth > window.innerWidth - pad) {
      left = window.innerWidth - pad - maxWidth;
    }
    if (left < pad) left = pad;
    const below = r.bottom + pad;
    const estimatedH = 168;
    const top =
      below + estimatedH > window.innerHeight - pad
        ? Math.max(pad, r.top - pad - estimatedH)
        : below;
    setPos({ top, left, maxWidth });
  }, []);

  useLayoutEffect(() => {
    if (!open) return;
    updatePos();
  }, [open, updatePos]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    const onPointer = (e: PointerEvent) => {
      const t = e.target as Node;
      if (triggerRef.current?.contains(t) || panelRef.current?.contains(t)) return;
      setOpen(false);
    };
    const onScroll = () => updatePos();
    window.addEventListener('keydown', onKey);
    window.addEventListener('pointerdown', onPointer, true);
    window.addEventListener('resize', onScroll);
    window.addEventListener('scroll', onScroll, true);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('pointerdown', onPointer, true);
      window.removeEventListener('resize', onScroll);
      window.removeEventListener('scroll', onScroll, true);
    };
  }, [open, updatePos]);

  const cadence =
    system.updateCadence != null
      ? (CADENCE_LABEL[system.updateCadence] ?? `更新节奏：${system.updateCadence}`)
      : null;
  const howToRead = metricHowToRead(system);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        className="vh-ranking-info"
        title="榜单说明"
        aria-label={`${system.shortName} 榜单说明`}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={open ? labelId : undefined}
        onClick={() => setOpen((v) => !v)}
      >
        <Icon name="Question" size={12} weight="bold" />
      </button>
      {open &&
        pos &&
        createPortal(
          <div
            ref={panelRef}
            id={labelId}
            role="dialog"
            aria-labelledby={`${labelId}-title`}
            className="vh-concept-pop vh-ranking-pop"
            style={{ top: pos.top, left: pos.left, maxWidth: pos.maxWidth }}
          >
            <div className="vh-concept-pop-title" id={`${labelId}-title`}>
              {system.name}
            </div>
            <div className="vh-ranking-pop-meta">
              <div>
                <span className="vh-ranking-pop-k">来源</span>
                {system.authority}
              </div>
              {cadence && (
                <div>
                  <span className="vh-ranking-pop-k">更新</span>
                  {cadence}
                </div>
              )}
            </div>
            <div className="vh-concept-pop-body">{system.description}</div>
            {howToRead && <div className="vh-ranking-pop-howto">{howToRead}</div>}
            <a
              className="vh-link vh-ranking-pop-link"
              href={system.url}
              target="_blank"
              rel="noreferrer"
            >
              查看原榜
              <Icon name="ArrowSquareOut" size={11} />
            </a>
          </div>,
          document.body,
        )}
    </>
  );
}

/** 列表/头栏用的精简徽标（主榜优先）。 */
export function RankingBadges({
  rankings,
  categoryId,
}: {
  rankings: EntryRanking[];
  categoryId?: Id;
}) {
  const { bundle } = useContent();
  if (!rankings.length) return null;

  const primary = categoryId
    ? primaryRankingSystem(bundle.rankingSystems.values(), categoryId)
    : undefined;

  const badges = [...rankings]
    .sort((a, b) => {
      if (primary) {
        if (a.systemId === primary.id) return -1;
        if (b.systemId === primary.id) return 1;
      }
      const oa = bundle.rankingSystems.get(a.systemId)?.order ?? 99;
      const ob = bundle.rankingSystems.get(b.systemId)?.order ?? 99;
      return oa - ob || a.systemId.localeCompare(b.systemId);
    })
    .map((r) => {
      const sys = bundle.rankingSystems.get(r.systemId);
      if (!sys) return null;
      const label =
        r.rank != null
          ? `${sys.shortName} #${r.rank}`
          : r.tier
            ? `${sys.shortName} · ${r.tier}`
            : r.share != null
              ? `${sys.shortName} ${r.share}%`
              : null;
      if (!label) return null;
      const isPrimary = primary?.id === r.systemId;
      return {
        id: r.systemId,
        label,
        top: isPrimary || (r.rank != null && r.rank <= 5),
      };
    })
    .filter((x): x is { id: string; label: string; top: boolean } => x != null)
    .slice(0, 2);

  if (!badges.length) return null;

  return (
    <>
      {badges.map((b) => (
        <span
          key={b.id}
          className="vh-tag"
          data-tone={b.top ? 'seal' : 'info'}
          title="权威排行快照"
        >
          {b.label}
        </span>
      ))}
    </>
  );
}
