import type { Id } from '@vh/core';
import { motion } from 'motion/react';
import { type ReactNode, useMemo } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import { UPDATE_TYPE_META, collectUpdates } from '../lib/intel.ts';
import { useMotionPrefs } from '../lib/motion.ts';
import { buildCatalogProvenance } from '../lib/provenance.ts';
import { useUserData } from '../lib/userdata.tsx';
import { BrandSeal } from './BrandSeal.tsx';
import { Disclaimer } from './Disclaimer.tsx';
import { FamilyDuelPanel } from './FamilyDuelPanel.tsx';
import { Icon } from './Icon.tsx';

interface DashboardViewProps {
  onOpenEntry: (id: Id) => void;
  onOpenRecipes: () => void;
  onOpenMyStacks: () => void;
  onOpenKnowledge: () => void;
  onOpenGraph: () => void;
  onOpenSettings: () => void;
  /** 未提供时隐藏「本地凭据」卡片（Web / 窄屏只读） */
  onOpenCredentials?: () => void;
  onOpenIntel: () => void;
}

export function DashboardView({
  onOpenEntry,
  onOpenRecipes,
  onOpenMyStacks,
  onOpenKnowledge,
  onOpenGraph,
  onOpenSettings,
  onOpenCredentials,
  onOpenIntel,
}: DashboardViewProps) {
  const { bundle } = useContent();
  const { data } = useUserData();
  const { overlaySummary } = useContentEditor();
  const { fadeSlide, staggerItem, tSlow, tStd, reduced } = useMotionPrefs();

  const noteEntries = Object.keys(data.notes)
    .map((id) => ({ id, note: data.notes[id] ?? '', entry: bundle.entries.get(id) }))
    .filter((x) => x.entry && x.note);

  const followFeed = collectUpdates(bundle.entries.values(), {
    onlyIds: new Set(data.follows),
    limit: 6,
  });
  const allFeed = collectUpdates(bundle.entries.values(), { limit: 6 });
  const feed = followFeed.length > 0 ? followFeed : allFeed;
  const feedTitle = followFeed.length > 0 ? '我的更新流' : '最近更新';

  const provenance = useMemo(
    () => buildCatalogProvenance(bundle.entries.values(), bundle.rankingSystems.values()),
    [bundle],
  );
  const authorityPreview = provenance.authorityLabels.slice(0, 10);
  const authorityMore = Math.max(0, provenance.authorityLabels.length - authorityPreview.length);

  const pulse = [
    { icon: 'Star', label: '收藏', value: data.favorites.length, onClick: onOpenKnowledge },
    { icon: 'Note', label: '笔记', value: Object.keys(data.notes).length, onClick: onOpenKnowledge },
    { icon: 'Stack', label: '技术栈', value: data.myStacks.length, onClick: onOpenMyStacks },
    { icon: 'Warning', label: '踩坑', value: data.myPitfalls.length, onClick: onOpenKnowledge },
    {
      icon: 'PencilSimple',
      label: '本地覆盖',
      value: overlaySummary.entryOverrides + overlaySummary.edgeOverrides,
      onClick: onOpenSettings,
    },
  ];

  return (
    <div className="vh-home overflow-y-auto" style={{ height: '100%' }}>
      {/* —— 首屏：品牌 + 一句主张 + CTA + 全幅舆图 —— */}
      <motion.section
        className="vh-home-hero"
        variants={fadeSlide}
        initial="initial"
        animate="animate"
        transition={tSlow}
      >
        <motion.img
          className="vh-home-hero-art"
          src="/illustrations/hero-atlas.webp"
          alt=""
          width={1920}
          height={823}
          decoding="async"
          initial={reduced ? false : { opacity: 0, scale: 1.04 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ ...tSlow, duration: reduced ? 0 : 0.55 }}
        />
        <div className="vh-home-hero-veil" aria-hidden />
        <div className="vh-home-hero-copy">
          <motion.div
            className="vh-home-brand"
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...tSlow, delay: reduced ? 0 : 0.08 }}
          >
            <BrandSeal size={32} />
            <span className="vh-home-brand-name">墨台</span>
          </motion.div>
          <motion.h1
            className="vh-home-title"
            initial={reduced ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...tSlow, delay: reduced ? 0 : 0.14 }}
          >
            AI 时代的选型擂台
          </motion.h1>
          <motion.p
            className="vh-home-lede"
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...tSlow, delay: reduced ? 0 : 0.2 }}
          >
            从 Agent 选到支付，对照平替、追踪变局。
          </motion.p>
          <motion.div
            className="vh-home-cta"
            initial={reduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...tSlow, delay: reduced ? 0 : 0.26 }}
          >
            <button type="button" className="vh-btn vh-btn-primary" onClick={onOpenKnowledge}>
              进入知识库
            </button>
            <button type="button" className="vh-btn" onClick={onOpenGraph}>
              打开图谱
            </button>
            <button type="button" className="vh-btn" onClick={onOpenRecipes}>
              浏览方案
            </button>
          </motion.div>
        </div>
      </motion.section>

      <div className="vh-home-body">
        {/* —— 墨点脉搏：一行计量，非卡片仪表盘 —— */}
        <motion.div
          className="vh-home-pulse"
          variants={fadeSlide}
          initial="initial"
          animate="animate"
          transition={{ ...tStd, delay: reduced ? 0 : 0.12 }}
        >
          {pulse.map((p) => (
            <button key={p.label} type="button" className="vh-home-pulse-item" onClick={p.onClick}>
              <span className="vh-home-pulse-dot" aria-hidden />
              <Icon name={p.icon} size={14} />
              <span className="vh-home-pulse-label">{p.label}</span>
              <span className="vh-home-pulse-value vh-mono">{p.value}</span>
            </button>
          ))}
        </motion.div>

        {/* —— 两栏：LLM 双强对垒 / 风向 —— */}
        <div className="vh-home-lanes">
          <FamilyDuelPanel onOpenEntry={onOpenEntry} />

          <Lane
            title={feedTitle}
            action={
              <button
                type="button"
                className="vh-btn"
                style={{ padding: '2px 8px', fontSize: 12 }}
                onClick={onOpenIntel}
              >
                全部
              </button>
            }
          >
            {feed.length === 0 ? (
              <Empty hint="关注条目后可看专属更新流" />
            ) : (
              <ul className="vh-home-list">
                {feed.map((item, i) => {
                  const meta = UPDATE_TYPE_META[item.update.type];
                  return (
                    <Row
                      key={`${item.entryId}-${item.update.date}-${item.update.summary}`}
                      label={item.entryName}
                      hint={`${item.update.date} · ${meta.label} · ${item.update.summary}`}
                      icon={meta.icon}
                      onClick={() => onOpenEntry(item.entryId)}
                      variants={staggerItem}
                      delay={reduced ? 0 : i * 0.03}
                    />
                  );
                })}
              </ul>
            )}
          </Lane>
        </div>

        {/* —— 三条航路入口 —— */}
        <section className="vh-home-paths" aria-label="快捷航路">
          <PathCard
            index="壹"
            accent="primary"
            title="我的技术栈"
            lede={
              data.myStacks.length > 0
                ? `${data.myStacks.length} 套已保存 · 可校验兼容与共现边`
                : '从方案模板采用，沉淀为可复用的组合'
            }
            cta="查看技术栈"
            onClick={onOpenMyStacks}
            icon="Stack"
          />
          <PathCard
            index="贰"
            accent="warning"
            title="笔记与踩坑"
            lede={
              noteEntries.length + data.myPitfalls.length > 0
                ? `${noteEntries.length} 则笔记 · ${data.myPitfalls.length} 条私人坑点`
                : '在详情页写下选型备注与私人坑点'
            }
            cta="打开知识库"
            onClick={onOpenKnowledge}
            icon="Note"
          />
          {onOpenCredentials && (
            <PathCard
              index="叁"
              accent="seal"
              title="本地凭据"
              lede="主密码解锁 · 到期提醒 · 加密备份迁移"
              cta="打开凭据"
              onClick={onOpenCredentials}
              icon="Key"
            />
          )}
        </section>

        {/* —— 信息来源公示：公开权威与规模，不涉及采集手段 —— */}
        <motion.section
          className="vh-home-provenance"
          aria-labelledby="vh-home-provenance-title"
          variants={fadeSlide}
          initial="initial"
          animate="animate"
          transition={{ ...tStd, delay: reduced ? 0 : 0.18 }}
        >
          <div className="vh-home-provenance-head">
            <h2 id="vh-home-provenance-title" className="vh-home-lane-title">
              信息来源
            </h2>
            <span className="vh-home-provenance-live" title="知识库持续对照公开信息保鲜">
              <span className="vh-home-provenance-live-dot" aria-hidden />
              持续更新中
            </span>
          </div>
          <p className="vh-home-provenance-lede">
            墨台不编造名次与版本节点。条目事实来自公开权威榜、厂商一手发布与可核验的生态信号；排行展示为第三方快照，非墨台主观评分。
          </p>

          <div className="vh-home-provenance-stats" aria-label="知识库规模">
            <div className="vh-home-provenance-stat">
              <span className="vh-home-provenance-stat-value vh-mono">{provenance.entryCount}</span>
              <span className="vh-home-provenance-stat-label">收录条目</span>
            </div>
            <div className="vh-home-provenance-stat">
              <span className="vh-home-provenance-stat-value vh-mono">
                {provenance.rankingSystemCount}
              </span>
              <span className="vh-home-provenance-stat-label">排行体系</span>
            </div>
            <div className="vh-home-provenance-stat">
              <span className="vh-home-provenance-stat-value vh-mono">
                {provenance.updatesLast30Days}
              </span>
              <span className="vh-home-provenance-stat-label">近 30 日更新</span>
            </div>
            {provenance.lastReviewedDate && (
              <div className="vh-home-provenance-stat">
                <span className="vh-home-provenance-stat-value vh-mono">
                  {provenance.lastReviewedDate}
                </span>
                <span className="vh-home-provenance-stat-label">信息更新</span>
              </div>
            )}
            {provenance.latestUpdateDate && (
              <div className="vh-home-provenance-stat">
                <span className="vh-home-provenance-stat-value vh-mono">
                  {provenance.latestUpdateDate}
                </span>
                <span className="vh-home-provenance-stat-label">最近动态</span>
              </div>
            )}
          </div>

          <ul className="vh-home-provenance-kinds">
            <li>
              <strong>权威排行与基准</strong>
              <span>
                {authorityPreview.join(' · ')}
                {authorityMore > 0 ? ` 等 ${provenance.authorityLabels.length} 家` : ''}
              </span>
            </li>
            <li>
              <strong>官方发布与生命周期</strong>
              <span>厂商 changelog、版本节点与公开维护/停更公告</span>
            </li>
            <li>
              <strong>开源生态信号</strong>
              <span>GitHub 与主流包管理器的客观流行度，作选型旁证</span>
            </li>
            <li>
              <strong>社区与行业观察</strong>
              <span>开发者社区热议与行业报告，仅作扩种参考，不自动定论</span>
            </li>
          </ul>
        </motion.section>

        <motion.div
          variants={fadeSlide}
          initial="initial"
          animate="animate"
          transition={{ ...tStd, delay: reduced ? 0 : 0.22 }}
        >
          <Disclaimer />
        </motion.div>
      </div>
    </div>
  );
}

function Lane({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <section className="vh-home-lane">
      <div className="vh-home-lane-head">
        <h2 className="vh-home-lane-title">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function PathCard({
  index,
  accent = 'primary',
  title,
  lede,
  cta,
  onClick,
  icon,
}: {
  index: string;
  accent?: 'primary' | 'warning' | 'seal';
  title: string;
  lede: string;
  cta: string;
  onClick: () => void;
  icon: string;
}) {
  return (
    <button type="button" className="vh-home-path" data-accent={accent} onClick={onClick}>
      <span className="vh-home-path-rule" aria-hidden />
      <span className="vh-home-path-head">
        <span className="vh-home-path-icon" aria-hidden>
          <Icon name={icon} size={24} weight="duotone" />
        </span>
        <span className="vh-home-path-index" aria-hidden>
          {index}
        </span>
      </span>
      <span className="vh-home-path-title">{title}</span>
      <span className="vh-home-path-lede">{lede}</span>
      <span className="vh-home-path-cta">
        {cta}
        <Icon name="ArrowRight" size={14} />
      </span>
    </button>
  );
}

function Row({
  label,
  hint,
  icon,
  onClick,
  variants,
  delay,
}: {
  label: string;
  hint?: string;
  icon?: string;
  onClick?: () => void;
  variants?: import('motion/react').Variants;
  delay?: number;
}) {
  return (
    <motion.li variants={variants} initial="initial" animate="animate" transition={{ delay }}>
      <button type="button" onClick={onClick} className="vh-home-row">
        {icon && (
          <span className="vh-home-row-icon">
            <Icon name={icon} size={14} />
          </span>
        )}
        <span className="vh-home-row-text">
          <span className="vh-home-row-label">{label}</span>
          {hint && <span className="vh-home-row-hint">{hint}</span>}
        </span>
      </button>
    </motion.li>
  );
}

function Empty({ hint }: { hint: string }) {
  return <div className="vh-home-empty">{hint}</div>;
}
