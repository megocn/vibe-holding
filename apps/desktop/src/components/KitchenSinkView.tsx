import { motion } from 'motion/react';
import type { ReactNode } from 'react';
import { useMotionPrefs } from '../lib/motion.ts';
import { BrandSeal } from './BrandSeal.tsx';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';

interface KitchenSinkViewProps {
  onBack: () => void;
}

/** 设计系统组件预览（T-UI-9 · 墨台厨房水槽） */
export function KitchenSinkView({ onBack }: KitchenSinkViewProps) {
  const { reduced, tStd, fadeSlide } = useMotionPrefs();

  return (
    <div className="overflow-y-auto" style={{ height: '100%' }}>
      <header className="vh-page-header">
        <div style={{ flex: 1 }}>
          <div className="vh-page-kicker">设计系统 · T-UI-9</div>
          <h1>组件预览</h1>
          <div className="vh-text-caption" style={{ marginTop: 4 }}>
            令牌、品牌标记、按钮、Chip、Tag、空态与动效。reduced-motion：{reduced ? '开' : '关'}
          </div>
        </div>
        <button type="button" className="vh-btn" onClick={onBack}>
          返回设置
        </button>
      </header>

      <div
        style={{
          padding: '24px 28px',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          gap: 28,
        }}
      >
        <Block title="品牌标记">
          <div className="flex items-center gap-4">
            <BrandSeal size={28} />
            <BrandSeal size={36} />
            <BrandSeal size={48} />
            <span className="vh-display" style={{ fontSize: 22 }}>
              墨台
            </span>
          </div>
        </Block>

        <Block title="字阶">
          <div className="vh-text-display">展示 Display 32</div>
          <div className="vh-text-h1">标题 H1 24</div>
          <div className="vh-text-h2">标题 H2 20</div>
          <div className="vh-text-h3">标题 H3 18</div>
          <p className="vh-text-sm" style={{ margin: '8px 0 0', maxWidth: '36em' }}>
            正文楷体需更宽行距。等宽示例：
            <code className="vh-mono"> sk-••••9f2a </code>
          </p>
          <p className="vh-text-caption" style={{ margin: '4px 0 0' }}>
            Caption 13 · 标注与时间戳
          </p>
        </Block>

        <Block title="颜料色 / Tag">
          <div className="flex flex-wrap gap-2">
            <span className="vh-tag">中性</span>
            <span className="vh-tag" data-tone="success">
              松绿 success
            </span>
            <span className="vh-tag" data-tone="info">
              石青 info
            </span>
            <span className="vh-tag" data-tone="warning">
              赭石 warning
            </span>
            <span className="vh-tag" data-tone="danger">
              朱砂 danger
            </span>
            <span className="vh-tag" data-tone="seal">
              印色 seal
            </span>
          </div>
        </Block>

        <Block title="Chip / 按钮">
          <div className="flex flex-wrap gap-2" style={{ marginBottom: 12 }}>
            <button type="button" className="vh-chip" data-on="false">
              未选
            </button>
            <button type="button" className="vh-chip" data-on="true">
              石青选中
            </button>
            <button type="button" className="vh-chip vh-chip-seal" data-on="true">
              朱砂选中
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="vh-btn">
              默认
            </button>
            <button type="button" className="vh-btn vh-btn-primary">
              <Icon name="Check" size={14} /> 主操作
            </button>
            <button type="button" className="vh-btn" disabled>
              禁用
            </button>
          </div>
        </Block>

        <Block title="卡片 / 面板 / 输入">
          <div className="flex flex-wrap gap-3">
            <div className="vh-card" style={{ padding: 14, width: 200 }}>
              <div style={{ fontWeight: 500 }}>vh-card</div>
              <div className="vh-text-caption">hover 抬升描边</div>
            </div>
            <div className="vh-card" data-selected="true" style={{ padding: 14, width: 200 }}>
              <div style={{ fontWeight: 500 }}>选中</div>
              <div className="vh-text-caption">data-selected</div>
            </div>
            <div className="vh-panel" style={{ padding: 14, width: 200 }}>
              <div className="vh-section-title">面板</div>
              <input className="vh-input" placeholder="vh-input" style={{ width: '100%' }} />
            </div>
          </div>
        </Block>

        <Block title="英雄图廓">
          <div className="vh-hero-atlas">
            <div style={{ position: 'relative', zIndex: 1 }}>
              <div className="vh-page-kicker">墨台 · 示例</div>
              <div className="vh-text-h2" style={{ margin: 0 }}>
                宣纸为底、墨为径
              </div>
            </div>
          </div>
        </Block>

        <Block title="空状态">
          <div
            className="vh-panel"
            style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <EmptyState seal title="选一枚墨点" hint="预览 EmptyState + BrandSeal。" />
          </div>
        </Block>

        <Block title="动效（fadeSlide）">
          <motion.div
            key={String(reduced)}
            variants={fadeSlide}
            initial="initial"
            animate="animate"
            transition={tStd}
            className="vh-card"
            style={{ padding: 16 }}
          >
            此块在挂载时淡入微移 · 时长 {reduced ? '0（reduced）' : '180ms'}
          </motion.div>
        </Block>

        <Block title="纸墨色板">
          <div className="flex flex-wrap gap-2">
            {(
              [
                ['--paper-0', 'paper-0'],
                ['--paper-1', 'paper-1'],
                ['--paper-2', 'paper-2'],
                ['--ink-1', 'ink-1'],
                ['--ink-2', 'ink-2'],
                ['--ink-3', 'ink-3'],
                ['--line', 'line'],
                ['--pigment-primary', 'primary'],
                ['--pigment-seal', 'seal'],
                ['--pigment-success', 'success'],
                ['--pigment-warning', 'warning'],
                ['--pigment-danger', 'danger'],
              ] as const
            ).map(([css, label]) => (
              <div key={css} style={{ width: 72, textAlign: 'center' }}>
                <div
                  style={{
                    height: 40,
                    borderRadius: 8,
                    background: `var(${css})`,
                    border: '1px solid var(--line)',
                    marginBottom: 4,
                  }}
                />
                <div className="vh-mono vh-text-caption">{label}</div>
              </div>
            ))}
          </div>
        </Block>
      </div>
    </div>
  );
}

function Block({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="vh-section-title">{title}</h2>
      {children}
    </section>
  );
}
