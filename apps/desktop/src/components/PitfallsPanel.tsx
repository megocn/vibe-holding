import type { Id } from '@vh/core';
import { useState } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import { useUserData } from '../lib/userdata.tsx';
import { Icon } from './Icon.tsx';

interface PitfallsPanelProps {
  entryId: Id;
}

/** 我踩过的坑：私有记录 + 贡献到本地条目覆盖（模块 07 入口）。 */
export function PitfallsPanel({ entryId }: PitfallsPanelProps) {
  const { bundle } = useContent();
  const { saveEntry } = useContentEditor();
  const { getPitfalls, addPitfall, removePitfall, markPitfallContributed } = useUserData();
  const [draft, setDraft] = useState('');
  const [msg, setMsg] = useState<string | null>(null);
  const pitfalls = getPitfalls(entryId);
  const entry = bundle.entries.get(entryId);

  function add() {
    if (!draft.trim()) return;
    addPitfall(entryId, draft);
    setDraft('');
    setMsg('已记录（仅本机）');
    window.setTimeout(() => setMsg(null), 1500);
  }

  function contribute(pitfallId: string, text: string) {
    if (!entry) return;
    if (entry.pitfalls.includes(text)) {
      markPitfallContributed(pitfallId);
      setMsg('条目中已有相同坑点，已标记为已贡献');
      window.setTimeout(() => setMsg(null), 2000);
      return;
    }
    saveEntry({
      ...entry,
      pitfalls: [...entry.pitfalls, text],
      lastReviewed: new Date().toISOString().slice(0, 10),
    });
    markPitfallContributed(pitfallId);
    setMsg('已写入本地条目覆盖（可在设置中导出）');
    window.setTimeout(() => setMsg(null), 2200);
  }

  return (
    <div>
      <ul style={{ margin: '0 0 12px', paddingLeft: 18, color: 'var(--ink-2)' }}>
        {pitfalls.length === 0 && (
          <li
            className="vh-text-caption"
            style={{ listStyle: 'none', marginLeft: -18, color: 'var(--ink-3)' }}
          >
            尚无私人坑点 · 与公共「坑点」分开存放
          </li>
        )}
        {pitfalls.map((p) => (
          <li key={p.id} style={{ marginBottom: 8 }}>
            <div>{p.text}</div>
            <div
              className="flex flex-wrap items-center gap-2 vh-text-caption"
              style={{ marginTop: 4, color: 'var(--ink-3)' }}
            >
              <span className="vh-mono">{p.createdAt}</span>
              {p.contributedAt ? (
                <span className="vh-tag" data-tone="success">
                  已贡献 {p.contributedAt}
                </span>
              ) : (
                <button
                  type="button"
                  className="vh-btn"
                  style={{ padding: '2px 8px' }}
                  onClick={() => contribute(p.id, p.text)}
                  disabled={!entry}
                  title="写入本地内容覆盖，不直接改仓库文件"
                >
                  贡献到本地条目
                </button>
              )}
              <button
                type="button"
                className="vh-btn"
                style={{ padding: '2px 8px' }}
                onClick={() => removePitfall(p.id)}
              >
                删除
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div className="flex gap-2" style={{ alignItems: 'flex-start' }}>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="记录你踩过的坑…"
          rows={2}
          className="vh-input"
          style={{
            flex: 1,
            resize: 'vertical',
            fontFamily: 'var(--font-body)',
            fontSize: 13,
            lineHeight: 1.5,
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              add();
            }
          }}
        />
        <button
          type="button"
          className="vh-btn vh-btn-primary flex items-center gap-1"
          onClick={add}
        >
          <Icon name="Plus" size={14} /> 添加
        </button>
      </div>
      {msg && (
        <div style={{ marginTop: 6, fontSize: 12, color: 'var(--pigment-success)' }}>{msg}</div>
      )}
      <div style={{ marginTop: 6, fontSize: 12, color: 'var(--ink-3)' }}>
        ⌘/Ctrl+Enter 快速添加 · 贡献仅写入本机覆盖层
      </div>
    </div>
  );
}
