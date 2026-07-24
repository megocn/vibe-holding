import type { EntryRanking, Id, RankingSystem } from '@vh/core';
import { formatRankingPrimary, primaryRankingSystem } from '@vh/core';
import { useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import { Icon } from './Icon.tsx';

interface RankingsPanelProps {
  categoryId: Id;
  rankings: EntryRanking[];
  /** 紧凑：用于侧栏 */
  compact?: boolean;
}

/** 条目多套权威排行快照 + 本分类推荐体系（无数据时提示对照）。 */
export function RankingsPanel({ categoryId, rankings, compact }: RankingsPanelProps) {
  const { bundle } = useContent();

  const { rows, categorySystems } = useMemo(() => {
    const systems = [...bundle.rankingSystems.values()]
      .filter((s) => s.categories.includes(categoryId))
      .sort((a, b) => a.order - b.order || a.id.localeCompare(b.id));

    const byId = new Map(rankings.map((r) => [r.systemId, r]));
    const rows = systems.map((sys) => ({
      system: sys,
      ranking: byId.get(sys.id),
    }));
    // 条目上有、但未挂到本分类的体系（异常数据）仍展示
    for (const r of rankings) {
      if (!systems.some((s) => s.id === r.systemId)) {
        const sys = bundle.rankingSystems.get(r.systemId);
        if (sys) rows.push({ system: sys, ranking: r });
      }
    }
    return { rows, categorySystems: systems };
  }, [bundle.rankingSystems, categoryId, rankings]);

  if (categorySystems.length === 0 && rankings.length === 0) {
    return (
      <p className="vh-text-caption" style={{ color: 'var(--ink-3)', margin: 0 }}>
        本分类尚未登记权威排行体系。
      </p>
    );
  }

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
          主观评分；期次与快照日见各行。选型请交叉多榜并自建评测。
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
  ranking?: EntryRanking;
  compact?: boolean;
}) {
  const primary = ranking ? formatRankingPrimary(ranking, system) : null;

  return (
    <li className="vh-ranking-row" data-has={ranking ? '1' : '0'}>
      <div className="vh-ranking-head">
        <span className="vh-ranking-name" title={system.description}>
          {system.shortName}
        </span>
        <a
          className="vh-ranking-ext"
          href={system.url}
          target="_blank"
          rel="noreferrer"
          title={`${system.name} · ${system.authority}`}
        >
          <Icon name="ArrowSquareOut" size={12} />
        </a>
      </div>
      {ranking ? (
        <>
          <div className="vh-ranking-primary">{primary}</div>
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
        </>
      ) : (
        <div className="vh-ranking-empty vh-text-caption">暂无快照 · 可点开榜单核对</div>
      )}
    </li>
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
