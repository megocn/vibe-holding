import type { MouseEvent, ReactNode } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import { isTauri } from '../lib/platform.ts';
import type { Density, Theme } from '../lib/prefs.ts';
import { useUserData } from '../lib/userdata.tsx';
import { Disclaimer } from './Disclaimer.tsx';

interface SettingsViewProps {
  theme: Theme;
  density: Density;
  onTheme: (t: Theme, origin?: { x: number; y: number }) => void;
  onDensity: (d: Density) => void;
  onOpenKitchen?: () => void;
}

export function SettingsView({
  theme,
  density,
  onTheme,
  onDensity,
  onOpenKitchen,
}: SettingsViewProps) {
  const { bundle, source } = useContent();
  const { data, rebuildPersonalEdges } = useUserData();
  const { overlaySummary, exportOverlay, clearAllOverlay } = useContentEditor();
  const noteCount = Object.keys(data.notes).length;
  const ratingCount = Object.keys(data.ratings).length;

  function downloadOverlay() {
    const json = exportOverlay();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vh-content-overlay.json';
    a.click();
    URL.revokeObjectURL(url);
  }
  return (
    <div style={{ padding: 32, maxWidth: 560 }}>
      <h1 className="vh-text-h1" style={{ margin: '0 0 8px', color: 'var(--ink-1)' }}>
        设置
      </h1>
      <p className="vh-text-sm" style={{ color: 'var(--ink-2)', margin: '0 0 20px' }}>
        纸墨主题、密度与本地内容覆盖。
      </p>

      <Row label="主题">
        <Segmented
          options={[
            { value: 'light', label: '浅色' },
            { value: 'dark', label: '深色' },
          ]}
          value={theme}
          onChange={(v, e) => onTheme(v as Theme, { x: e.clientX, y: e.clientY })}
        />
      </Row>

      <Row label="密度">
        <Segmented
          options={[
            { value: 'comfortable', label: '宽松' },
            { value: 'compact', label: '紧凑' },
          ]}
          value={density}
          onChange={(v) => onDensity(v as Density)}
        />
      </Row>

      {onOpenKitchen && (
        <Row label="组件预览">
          <button type="button" className="vh-btn vh-btn-primary" onClick={onOpenKitchen}>
            打开厨房水槽
          </button>
        </Row>
      )}

      <Row label="运行环境">
        <span className="vh-tag">{isTauri ? 'Tauri 桌面' : '浏览器（开发）'}</span>
      </Row>

      <Row label="内容来源">
        <span className="vh-tag">{source === 'ipc' ? 'IPC content_load' : '静态 JSON'}</span>
      </Row>

      <Row label="内容库">
        <span style={{ color: 'var(--ink-2)', fontSize: 14 }}>
          {bundle.entries.size} 条目 · {bundle.edges.length} 关系 · {bundle.categories.length} 分类
        </span>
      </Row>

      <Row label="个人沉淀">
        <span style={{ color: 'var(--ink-2)', fontSize: 14 }}>
          {data.favorites.length} 收藏 · {noteCount} 笔记 · {ratingCount} 评分 ·{' '}
          {data.myStacks.length} 技术栈 · {data.myPitfalls.length} 踩坑 ·{' '}
          {data.personalEdges.length} 个人边
        </span>
      </Row>

      {data.myStacks.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <button type="button" className="vh-btn" onClick={() => rebuildPersonalEdges()}>
            从技术栈重建个人共现边
          </button>
        </div>
      )}

      <Row label="内容覆盖层">
        <span style={{ color: 'var(--ink-2)', fontSize: 14 }}>
          {overlaySummary.entryOverrides} 条目 · {overlaySummary.edgeOverrides} 边
          {overlaySummary.removed > 0 ? ` · 隐藏 ${overlaySummary.removed}` : ''}
        </span>
      </Row>

      {(overlaySummary.entryOverrides > 0 ||
        overlaySummary.edgeOverrides > 0 ||
        overlaySummary.removed > 0) && (
        <div className="flex gap-2" style={{ marginTop: 16 }}>
          <button type="button" className="vh-btn" onClick={downloadOverlay}>
            导出覆盖层 JSON
          </button>
          <button
            type="button"
            className="vh-btn"
            onClick={() => {
              if (window.confirm('清除全部本地内容覆盖？此操作不可撤销。')) clearAllOverlay();
            }}
          >
            清除覆盖层
          </button>
        </div>
      )}

      <div style={{ marginTop: 28 }}>
        <Disclaimer compact id="vh-settings-disclaimer" />
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div
      className="flex items-center justify-between"
      style={{ padding: '14px 0', borderBottom: '1px solid var(--line)' }}
    >
      <span style={{ color: 'var(--ink-1)', fontSize: 15 }}>{label}</span>
      {children}
    </div>
  );
}

function Segmented({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string }[];
  value: string;
  onChange: (v: string, e: MouseEvent) => void;
}) {
  return (
    <div
      className="flex"
      style={{ border: '1px solid var(--line)', borderRadius: 'var(--radius)', overflow: 'hidden' }}
    >
      {options.map((o) => {
        const on = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            onClick={(e) => onChange(o.value, e)}
            className="vh-chip"
            data-on={on ? 'true' : 'false'}
            style={{
              borderRadius: 0,
              border: 'none',
              padding: '6px 16px',
            }}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
