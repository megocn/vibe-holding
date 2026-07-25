import type { Id } from '@vh/core';
import { motion } from 'motion/react';
import { useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import {
  type FamilyDuelFighter,
  buildFamilyDuelBoard,
} from '../lib/family-duel.ts';
import { useMotionPrefs } from '../lib/motion.ts';

interface FamilyDuelPanelProps {
  onOpenEntry: (id: Id) => void;
}

export function FamilyDuelPanel({ onOpenEntry }: FamilyDuelPanelProps) {
  const { bundle } = useContent();
  const { fadeSlide, tStd, reduced } = useMotionPrefs();
  const board = useMemo(() => buildFamilyDuelBoard(bundle), [bundle]);

  if (!board) {
    return (
      <section className="vh-home-lane vh-home-duel">
        <div className="vh-home-lane-head">
          <h2 className="vh-home-lane-title">本周对垒</h2>
        </div>
        <div className="vh-home-empty">大语言模型族序数据不足，暂无法对垒</div>
      </section>
    );
  }

  return (
    <motion.section
      className="vh-home-lane vh-home-duel"
      aria-labelledby="vh-home-duel-title"
      variants={fadeSlide}
      initial="initial"
      animate="animate"
      transition={{ ...tStd, delay: reduced ? 0 : 0.08 }}
    >
      <div className="vh-home-lane-head">
        <h2 id="vh-home-duel-title" className="vh-home-lane-title">
          本周对垒
        </h2>
        <span className="vh-home-duel-week" title="插画按 ISO 周更换；战绩随权威榜现算">
          {board.weekLabel}
          <span className="vh-home-duel-week-cadence"> · 每周更新</span>
        </span>
      </div>

      <div className="vh-home-duel-stage">
        <img
          className="vh-home-duel-art"
          src={board.imageSrc}
          alt={`${board.first.name} 与 ${board.second.name} 拟人水墨冷兵器对垒`}
          width={1600}
          height={800}
          decoding="async"
        />
        {!board.artMatches && (
          <p className="vh-home-duel-art-note">
            插画为 {board.artWeek} 双强；战绩已按本周族序刷新
          </p>
        )}
      </div>

      <ul className="vh-home-duel-board">
        <li>
          <FighterCard
            fighter={board.first}
            side="left"
            onOpen={() => onOpenEntry(board.first.id)}
          />
        </li>
        <li className="vh-home-duel-vs" aria-hidden>
          <span>对</span>
        </li>
        <li>
          <FighterCard
            fighter={board.second}
            side="right"
            onOpen={() => onOpenEntry(board.second.id)}
          />
        </li>
      </ul>

      <p className="vh-home-duel-footnote">
        〈大语言模型与多模态〉产品族综合分前二 · 旗舰榜位取族内最佳 · 非墨台主观评分
      </p>
    </motion.section>
  );
}

function FighterCard({
  fighter,
  side,
  onOpen,
}: {
  fighter: FamilyDuelFighter;
  side: 'left' | 'right';
  onOpen: () => void;
}) {
  return (
    <button
      type="button"
      className="vh-home-duel-fighter"
      data-side={side}
      data-place={fighter.place}
      onClick={onOpen}
    >
      <span className="vh-home-duel-fighter-top">
        <span className="vh-home-duel-place">#{fighter.place}</span>
        <span className="vh-home-duel-name">{fighter.name}</span>
        <span className="vh-home-duel-score vh-mono" title="产品族综合分 S">
          {fighter.scoreS.toFixed(1)}
        </span>
      </span>
      {fighter.oneLiner && (
        <span className="vh-home-duel-oneliner">{fighter.oneLiner}</span>
      )}
      <span className="vh-home-duel-metrics">
        {fighter.metrics.map((m) => (
          <span
            key={m.systemId}
            className="vh-home-duel-metric"
            title={
              [m.lineName, m.scoreLabel].filter(Boolean).join(' · ') || m.label
            }
          >
            <span className="vh-home-duel-metric-label">{m.label}</span>
            <span className="vh-home-duel-metric-rank vh-mono">
              {m.rank != null ? `#${m.rank}` : '—'}
            </span>
          </span>
        ))}
      </span>
    </button>
  );
}
