import type { EntryUpdate, Id, UpdateType } from '@vh/core';
import { useCallback, useMemo, useState } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import {
  type IntelDraft,
  addIntelDraft,
  loadIntelDrafts,
  mergeDraftIntoEntry,
  pendingDrafts,
  removeIntelDraft,
  saveIntelDrafts,
  seedSimulatedDrafts,
  setDraftStatus,
} from '../lib/intel-drafts.ts';
import { INTEL_FEEDS, scrapeFeedsToDrafts } from '../lib/intel-scrape.ts';
import {
  STALE_DAYS,
  UPDATE_TYPE_META,
  collectStaleEntries,
  collectUpdates,
  daysSince,
} from '../lib/intel.ts';
import { useUserData } from '../lib/userdata.tsx';
import { EmptyState } from './EmptyState.tsx';
import { Icon } from './Icon.tsx';
import { UpdatesTimeline } from './UpdatesTimeline.tsx';

interface IntelViewProps {
  onOpenEntry: (id: Id) => void;
}

type Tab = 'feed' | 'all' | 'drafts' | 'stale' | 'follows';

const UPDATE_TYPES: UpdateType[] = [
  'release',
  'feature',
  'pricing',
  'policy',
  'deprecation',
  'other',
];

export function IntelView({ onOpenEntry }: IntelViewProps) {
  const { bundle } = useContent();
  const { saveEntry } = useContentEditor();
  const { data, isFollowing, toggleFollow } = useUserData();
  const [tab, setTab] = useState<Tab>('feed');
  const [drafts, setDrafts] = useState<IntelDraft[]>(() => loadIntelDrafts());
  const [flash, setFlash] = useState<string | null>(null);
  const [manualEntryId, setManualEntryId] = useState('');
  const [manualSummary, setManualSummary] = useState('');
  const [manualType, setManualType] = useState<UpdateType>('feature');
  const [manualSource, setManualSource] = useState('');
  const [scraping, setScraping] = useState(false);

  const commitDrafts = useCallback((next: IntelDraft[]) => {
    setDrafts(next);
    saveIntelDrafts(next);
  }, []);

  const showFlash = (msg: string) => {
    setFlash(msg);
    window.setTimeout(() => setFlash(null), 2200);
  };

  const followSet = useMemo(() => new Set(data.follows), [data.follows]);
  const allEntries = useMemo(() => [...bundle.entries.values()], [bundle.entries]);
  const entryOptions = useMemo(
    () =>
      allEntries
        .map((e) => ({ id: e.id, name: e.name }))
        .sort((a, b) => a.name.localeCompare(b.name)),
    [allEntries],
  );

  const feed = useMemo(
    () => collectUpdates(allEntries, { onlyIds: followSet, limit: 50 }),
    [allEntries, followSet],
  );
  const all = useMemo(() => collectUpdates(allEntries, { limit: 80 }), [allEntries]);
  const stale = useMemo(() => collectStaleEntries(allEntries), [allEntries]);
  const pending = useMemo(() => pendingDrafts(drafts), [drafts]);

  const followedEntries = useMemo(
    () => data.follows.map((id) => bundle.entries.get(id)).filter((e) => e != null),
    [data.follows, bundle.entries],
  );

  function acceptDraft(draft: IntelDraft) {
    const entry = bundle.entries.get(draft.entryId);
    if (!entry) {
      showFlash(`条目不存在：${draft.entryId}`);
      return;
    }
    const merged = mergeDraftIntoEntry(entry, draft);
    if (!merged) {
      commitDrafts(setDraftStatus(drafts, draft.id, 'accepted', '条目中已有相同更新'));
      showFlash('已存在相同更新，草稿标为已确认');
      return;
    }
    saveEntry(merged);
    commitDrafts(setDraftStatus(drafts, draft.id, 'accepted'));
    showFlash(`已入库：${entry.name}`);
  }

  function rejectDraft(draft: IntelDraft) {
    commitDrafts(setDraftStatus(drafts, draft.id, 'rejected'));
    showFlash('已拒绝草稿');
  }

  function seedDemos() {
    const { drafts: next, added } = seedSimulatedDrafts(drafts, new Set(bundle.entries.keys()));
    commitDrafts(next);
    showFlash(added > 0 ? `已生成 ${added} 条演示草稿` : '演示草稿已存在，无新增');
    setTab('drafts');
  }

  async function scrapeFeeds() {
    if (scraping) return;
    setScraping(true);
    try {
      const {
        drafts: next,
        results,
        added,
      } = await scrapeFeedsToDrafts(drafts, {
        entryIds: new Set(bundle.entries.keys()),
        perFeedLimit: 3,
      });
      commitDrafts(next);
      const failed = results.filter((r) => !r.ok);
      if (added > 0) {
        showFlash(
          failed.length
            ? `抓取新增 ${added} 条；${failed.length} 源失败`
            : `抓取新增 ${added} 条草稿`,
        );
      } else if (failed.length === results.length) {
        showFlash('抓取失败：请确认开发服务器代理可用');
      } else {
        showFlash('无新增（条目已在待确认队列或 feed 为空）');
      }
      setTab('drafts');
    } catch (err) {
      showFlash(err instanceof Error ? err.message : '抓取失败');
    } finally {
      setScraping(false);
    }
  }

  function addManual() {
    if (!manualEntryId || !manualSummary.trim()) {
      showFlash('请选择条目并填写摘要');
      return;
    }
    const update: EntryUpdate = {
      date: new Date().toISOString().slice(0, 10),
      type: manualType,
      summary: manualSummary.trim(),
      source: manualSource.trim() || undefined,
    };
    if (update.source) {
      try {
        new URL(update.source);
      } catch {
        showFlash('来源须为合法 URL（可留空）');
        return;
      }
    }
    commitDrafts(
      addIntelDraft(drafts, {
        entryId: manualEntryId as Id,
        update,
        origin: 'manual',
      }),
    );
    setManualSummary('');
    setManualSource('');
    showFlash('已加入待确认队列');
    setTab('drafts');
  }

  return (
    <div className="flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      <header className="vh-page-header">
        <div style={{ flex: 1 }}>
          <div className="vh-page-kicker">讯报 · 关注流</div>
          <h1>情报</h1>
          <div className="vh-text-caption" style={{ marginTop: 4 }}>
            关注流 · 草稿确认 · 超期复核（{STALE_DAYS} 天）
          </div>
        </div>
        <div className="flex items-center gap-2">
          {flash && (
            <span className="vh-text-caption" style={{ color: 'var(--pigment-success)' }}>
              {flash}
            </span>
          )}
          <button
            type="button"
            className="vh-btn vh-btn-primary"
            onClick={() => void scrapeFeeds()}
            disabled={scraping}
            title={`抓取 ${INTEL_FEEDS.length} 个配置源（RSS/Atom）`}
          >
            <Icon name="CloudArrowDown" size={14} /> {scraping ? '抓取中…' : '抓取订阅'}
          </button>
          <button type="button" className="vh-btn" onClick={seedDemos} title="模拟抓取生成草稿">
            <Icon name="MagicWand" size={14} /> 演示草稿
          </button>
          <span className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)' }}>
            关注 {data.follows.length}
          </span>
        </div>
      </header>

      <div
        className="flex gap-1.5 flex-wrap"
        style={{
          padding: '10px 24px',
          borderBottom: '1px solid var(--line)',
          flexShrink: 0,
          background: 'color-mix(in oklch, var(--paper-1) 70%, transparent)',
        }}
      >
        {(
          [
            { id: 'feed' as const, label: `我的更新流 (${feed.length})` },
            { id: 'all' as const, label: `全部更新 (${all.length})` },
            { id: 'drafts' as const, label: `待确认 (${pending.length})` },
            { id: 'follows' as const, label: `关注列表 (${followedEntries.length})` },
            { id: 'stale' as const, label: `待复核 (${stale.length})` },
          ] as const
        ).map((t) => {
          const on = tab === t.id;
          return (
            <button
              key={t.id}
              type="button"
              className={`vh-chip${t.id === 'drafts' || t.id === 'stale' ? ' vh-chip-seal' : ''}`}
              onClick={() => setTab(t.id)}
              data-on={on ? 'true' : 'false'}
            >
              {t.label}
            </button>
          );
        })}
      </div>

      <div className="overflow-y-auto" style={{ flex: 1, padding: '16px 24px', maxWidth: 820 }}>
        {tab === 'feed' && (
          <UpdatesTimeline
            items={feed}
            onOpenEntry={onOpenEntry}
            emptyHint="关注条目后，其更新会出现在这里。在详情页点「关注更新」。"
          />
        )}
        {tab === 'all' && (
          <UpdatesTimeline
            items={all}
            onOpenEntry={onOpenEntry}
            emptyHint="内容库暂无 updates 记录。"
          />
        )}

        {tab === 'drafts' && (
          <div className="flex flex-col gap-4">
            <section className="vh-panel" style={{ padding: 14 }}>
              <h2
                className="vh-display"
                style={{ fontSize: 15, margin: '0 0 8px', color: 'var(--ink-2)' }}
              >
                手动添加草稿
              </h2>
              <div className="flex flex-col gap-2">
                <select
                  className="vh-input"
                  value={manualEntryId}
                  onChange={(e) => setManualEntryId(e.target.value)}
                >
                  <option value="">选择条目…</option>
                  {entryOptions.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
                <div className="flex gap-2 flex-wrap">
                  <select
                    className="vh-input"
                    value={manualType}
                    onChange={(e) => setManualType(e.target.value as UpdateType)}
                    style={{ minWidth: 120 }}
                  >
                    {UPDATE_TYPES.map((t) => (
                      <option key={t} value={t}>
                        {UPDATE_TYPE_META[t].label}
                      </option>
                    ))}
                  </select>
                  <input
                    className="vh-input"
                    style={{ flex: 1, minWidth: 160 }}
                    placeholder="来源 URL（可选）"
                    value={manualSource}
                    onChange={(e) => setManualSource(e.target.value)}
                  />
                </div>
                <textarea
                  className="vh-input"
                  rows={2}
                  placeholder="更新摘要…"
                  value={manualSummary}
                  onChange={(e) => setManualSummary(e.target.value)}
                  style={{ resize: 'vertical', fontFamily: 'var(--font-body)' }}
                />
                <button type="button" className="vh-btn vh-btn-primary" onClick={addManual}>
                  <Icon name="Plus" size={14} /> 加入队列
                </button>
              </div>
              <div className="vh-text-caption" style={{ marginTop: 8, color: 'var(--ink-3)' }}>
                确认后写入本机条目覆盖（updates）；拒绝仅改草稿状态。订阅源见 content/feeds.json（
                {INTEL_FEEDS.length} 个）。
              </div>
            </section>

            {pending.length === 0 ? (
              <EmptyState
                icon="Tray"
                title="暂无待确认草稿"
                hint="点「抓取订阅」拉取 RSS/Atom，或「演示草稿」/手动添加。"
              />
            ) : (
              <div className="flex flex-col gap-2">
                {pending.map((d) => {
                  const entry = bundle.entries.get(d.entryId);
                  const meta = UPDATE_TYPE_META[d.update.type];
                  const originLabel =
                    d.origin === 'feed-scrape'
                      ? '订阅抓取'
                      : d.origin === 'simulated-scrape'
                        ? '模拟抓取'
                        : '手动';
                  return (
                    <div key={d.id} className="vh-card" style={{ padding: 14 }}>
                      <div className="flex items-start gap-2">
                        <Icon name={meta.icon} size={18} color={meta.color} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <button
                            type="button"
                            className="vh-link"
                            style={{
                              border: 'none',
                              background: 'transparent',
                              cursor: 'pointer',
                              padding: 0,
                              fontWeight: 600,
                              fontFamily: 'var(--font-body)',
                              color: 'var(--ink-1)',
                            }}
                            onClick={() => onOpenEntry(d.entryId)}
                          >
                            {entry?.name ?? d.entryId}
                          </button>
                          <div
                            className="vh-text-sm"
                            style={{ color: 'var(--ink-2)', marginTop: 4 }}
                          >
                            {d.update.summary}
                          </div>
                          <div
                            className="vh-mono vh-text-caption flex flex-wrap gap-2"
                            style={{ color: 'var(--ink-3)', marginTop: 6 }}
                          >
                            <span>{d.update.date}</span>
                            <span>{meta.label}</span>
                            <span>{originLabel}</span>
                            {d.update.source && (
                              <a
                                className="vh-link"
                                href={d.update.source}
                                target="_blank"
                                rel="noreferrer"
                              >
                                来源 ↗
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2" style={{ marginTop: 10 }}>
                        <button
                          type="button"
                          className="vh-btn vh-btn-primary"
                          onClick={() => acceptDraft(d)}
                        >
                          <Icon name="Check" size={14} /> 确认入库
                        </button>
                        <button type="button" className="vh-btn" onClick={() => rejectDraft(d)}>
                          拒绝
                        </button>
                        <button
                          type="button"
                          className="vh-btn"
                          onClick={() => {
                            commitDrafts(removeIntelDraft(drafts, d.id));
                            showFlash('已删除草稿');
                          }}
                          style={{ color: 'var(--pigment-danger)' }}
                        >
                          删除
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {tab === 'follows' &&
          (followedEntries.length === 0 ? (
            <EmptyState
              icon="Bell"
              title="尚未关注"
              hint="在条目详情点「关注更新」，讯报会汇入「我的更新流」。"
            />
          ) : (
            <div className="flex flex-col gap-2">
              {followedEntries.map((e) => (
                <div key={e.id} className="vh-card flex items-center gap-3" style={{ padding: 12 }}>
                  <button
                    type="button"
                    className="vh-link"
                    style={{
                      border: 'none',
                      background: 'transparent',
                      cursor: 'pointer',
                      padding: 0,
                      flex: 1,
                      textAlign: 'left',
                      fontWeight: 500,
                      color: 'var(--ink-1)',
                      fontFamily: 'var(--font-body)',
                    }}
                    onClick={() => onOpenEntry(e.id)}
                  >
                    {e.name}
                    <span style={{ fontWeight: 400, color: 'var(--ink-2)', marginLeft: 8 }}>
                      {e.oneLiner}
                    </span>
                  </button>
                  <span className="vh-tag">{e.updates.length} 更新</span>
                  {isFollowing(e.id) && (
                    <button
                      type="button"
                      className="vh-btn"
                      onClick={() => toggleFollow(e.id)}
                      style={{ padding: '2px 8px' }}
                    >
                      取消关注
                    </button>
                  )}
                </div>
              ))}
            </div>
          ))}
        {tab === 'stale' &&
          (stale.length === 0 ? (
            <div
              className="flex items-center gap-2 vh-text-sm"
              style={{ color: 'var(--pigment-success)' }}
            >
              <Icon name="CheckCircle" size={16} weight="fill" />
              暂无超期未复核条目
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {stale.map((e) => (
                <div key={e.id} className="vh-card flex items-center gap-3" style={{ padding: 12 }}>
                  <Icon name="Warning" size={16} color="var(--pigment-warning)" />
                  <button
                    type="button"
                    className="vh-link"
                    style={{
                      border: 'none',
                      background: 'transparent',
                      cursor: 'pointer',
                      padding: 0,
                      flex: 1,
                      textAlign: 'left',
                      fontWeight: 500,
                      fontFamily: 'var(--font-body)',
                    }}
                    onClick={() => onOpenEntry(e.id)}
                  >
                    {e.name}
                  </button>
                  <span className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)' }}>
                    复核 {e.lastReviewed} · {daysSince(e.lastReviewed)} 天前
                  </span>
                </div>
              ))}
            </div>
          ))}
      </div>
    </div>
  );
}
