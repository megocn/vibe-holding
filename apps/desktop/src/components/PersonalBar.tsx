import type { Id } from '@vh/core';
import { useEffect, useState } from 'react';
import { useUserData } from '../lib/userdata.tsx';
import { Icon } from './Icon.tsx';

interface PersonalBarProps {
  entryId: Id;
}

/** 详情页：收藏星标 + 关注更新 + 1–5 评分 + 个人笔记（即时持久）。 */
export function PersonalBar({ entryId }: PersonalBarProps) {
  const {
    isFavorite,
    toggleFavorite,
    isFollowing,
    toggleFollow,
    getNote,
    setNote,
    getRating,
    setRating,
  } = useUserData();
  const fav = isFavorite(entryId);
  const following = isFollowing(entryId);
  const rating = getRating(entryId);
  const [draft, setDraft] = useState(() => getNote(entryId));
  const [savedFlash, setSavedFlash] = useState(false);
  const hasNote = draft.trim().length > 0;
  // 有笔记时默认展开，否则收起，减少正文顶部占位
  const [noteOpen, setNoteOpen] = useState(() => getNote(entryId).trim().length > 0);

  // 切换条目时同步草稿与展开态
  useEffect(() => {
    const n = getNote(entryId);
    setDraft(n);
    setNoteOpen(n.trim().length > 0);
  }, [entryId, getNote]);

  function saveNote() {
    setNote(entryId, draft);
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 1200);
  }

  return (
    <div
      style={{
        marginTop: 16,
        padding: '8px 12px',
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-lg)',
        background: 'var(--paper-1)',
      }}
    >
      <div className="flex items-center gap-2" style={{ flexWrap: 'wrap' }}>
        <button
          type="button"
          className="vh-btn flex items-center gap-1.5"
          onClick={() => toggleFavorite(entryId)}
          title={fav ? '取消收藏' : '收藏'}
          style={{
            color: fav ? 'var(--pigment-warning)' : undefined,
            borderColor: fav ? 'var(--pigment-warning)' : undefined,
          }}
        >
          <Icon name="Star" size={16} weight={fav ? 'fill' : 'regular'} />
          {fav ? '已收藏' : '收藏'}
        </button>

        <button
          type="button"
          className="vh-btn flex items-center gap-1.5"
          onClick={() => toggleFollow(entryId)}
          title={following ? '取消关注更新' : '关注更新'}
          style={{
            color: following ? 'var(--pigment-primary)' : undefined,
            borderColor: following ? 'var(--pigment-primary)' : undefined,
          }}
        >
          <Icon name="Bell" size={16} weight={following ? 'fill' : 'regular'} />
          {following ? '已关注更新' : '关注更新'}
        </button>

        <div className="flex items-center gap-1" title="个人评分">
          {[1, 2, 3, 4, 5].map((n) => {
            const on = rating != null && rating >= n;
            return (
              <button
                key={n}
                type="button"
                aria-label={`评分 ${n}`}
                onClick={() => setRating(entryId, rating === n ? null : n)}
                style={{
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  padding: 2,
                  color: on ? 'var(--pigment-warning)' : 'var(--ink-3)',
                }}
              >
                <Icon name="Star" size={18} weight={on ? 'fill' : 'regular'} />
              </button>
            );
          })}
          {rating != null && (
            <button
              type="button"
              className="vh-tag"
              onClick={() => setRating(entryId, null)}
              style={{ cursor: 'pointer', marginLeft: 4 }}
            >
              清除评分
            </button>
          )}
        </div>

        <div style={{ flex: 1 }} />

        <button
          type="button"
          className="vh-btn flex items-center gap-1.5"
          aria-expanded={noteOpen}
          onClick={() => setNoteOpen((o) => !o)}
          title={noteOpen ? '收起笔记' : hasNote ? '展开我的笔记' : '添加笔记'}
          style={{
            color: hasNote ? 'var(--pigment-primary)' : undefined,
            borderColor: hasNote ? 'var(--pigment-primary)' : undefined,
          }}
        >
          <Icon name={hasNote ? 'NotePencil' : 'Note'} size={16} weight={hasNote ? 'fill' : 'regular'} />
          我的笔记
          <Icon name={noteOpen ? 'CaretUp' : 'CaretDown'} size={12} />
        </button>
      </div>

      {noteOpen && (
        <div style={{ marginTop: 10 }}>
          <div
            className="flex items-center justify-between"
            style={{ marginBottom: 6, color: 'var(--ink-2)', fontSize: 13 }}
          >
            <span>我的笔记</span>
            {savedFlash && (
              <span style={{ color: 'var(--pigment-success)', fontSize: 12 }}>已保存</span>
            )}
          </div>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={saveNote}
            placeholder="记录选型理由、坑点、对接备注…"
            rows={4}
            className="vh-input"
            style={{
              width: '100%',
              resize: 'vertical',
              boxSizing: 'border-box',
              fontFamily: 'var(--font-body)',
              fontSize: 14,
              lineHeight: 1.6,
            }}
          />
          <div style={{ marginTop: 6, color: 'var(--ink-3)', fontSize: 12 }}>
            失焦自动保存 · 仅存本机
          </div>
        </div>
      )}
    </div>
  );
}
