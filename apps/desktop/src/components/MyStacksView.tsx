import type { Id, StackIssue, StackRecipe } from '@vh/core';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { copyText, downloadJson, formatStackMarkdown } from '../lib/stack-export.ts';
import { useIsMobile } from '../lib/use-is-mobile.ts';
import { useUserData } from '../lib/userdata.tsx';
import { Icon } from './Icon.tsx';

interface MyStacksViewProps {
  onOpenEntry: (id: Id) => void;
  onOpenWizard?: () => void;
}

export function MyStacksView({ onOpenEntry, onOpenWizard }: MyStacksViewProps) {
  const { bundle, graph } = useContent();
  const { data, removeStack, updateStack, getNote, setNote, getRating, setRating } = useUserData();
  const isMobile = useIsMobile();
  const stacks = data.myStacks;
  const [selectedId, setSelectedId] = useState<string | null>(() => stacks[0]?.id ?? null);
  const [mobilePane, setMobilePane] = useState<'list' | 'detail'>('list');
  const [flash, setFlash] = useState<string | null>(null);
  const [recheckAt, setRecheckAt] = useState(0);

  useEffect(() => {
    if (!isMobile) setMobilePane('list');
  }, [isMobile]);

  const selected = useMemo(
    () => stacks.find((s) => s.id === selectedId) ?? (!isMobile ? stacks[0] : undefined),
    [stacks, selectedId, isMobile],
  );

  const layers = selected?.layers ?? {};
  const issues = useMemo(() => {
    void recheckAt;
    return Object.keys(layers).length > 0 ? graph.validateStack(layers) : [];
  }, [graph, layers, recheckAt]);

  const catName = (id: string) => bundle.categories.find((c) => c.id === id)?.name ?? id;
  const resolveName = (id: string) => bundle.entries.get(id)?.name ?? id;
  const showList = !isMobile || mobilePane === 'list';
  const showDetail = !isMobile || mobilePane === 'detail';

  function flashMsg(msg: string) {
    setFlash(msg);
    window.setTimeout(() => setFlash(null), 1600);
  }

  function pickStack(id: string) {
    setSelectedId(id);
    if (isMobile) setMobilePane('detail');
  }

  function exportOneJson(stack: Partial<StackRecipe>) {
    const id = stack.id ?? 'stack';
    downloadJson(`${id}.json`, stack);
    flashMsg('已导出 JSON');
  }

  function exportAllJson() {
    downloadJson(`vh-my-stacks-${Date.now()}.json`, stacks);
    flashMsg('已导出全部技术栈');
  }

  async function copyMd(stack: Partial<StackRecipe>) {
    const md = formatStackMarkdown(stack, {
      resolveName,
      catName,
      issues: stack.layers ? graph.validateStack(stack.layers) : [],
      note: stack.id ? getNote(stack.id) : '',
      rating: stack.id ? getRating(stack.id) : null,
    });
    const ok = await copyText(md);
    flashMsg(ok ? '已复制 Markdown' : '复制失败');
  }

  return (
    <div className="vh-recipes-split flex" style={{ height: '100%', minHeight: 0 }}>
      {showList && (
        <aside className="vh-recipes-list vh-column flex flex-col overflow-y-auto">
          <div className="flex items-center gap-2" style={{ margin: '4px 8px 12px' }}>
            <div style={{ flex: 1 }}>
              <div className="vh-page-kicker">私藏</div>
              <div className="vh-text-h3" style={{ color: 'var(--ink-1)', margin: 0 }}>
                我的技术栈
              </div>
            </div>
            {stacks.length > 0 && (
              <button
                type="button"
                className="vh-btn"
                title="导出全部 JSON"
                style={{ padding: '2px 8px', fontSize: 12 }}
                onClick={exportAllJson}
              >
                全部导出
              </button>
            )}
          </div>

          {stacks.length === 0 ? (
            <div className="vh-text-sm" style={{ padding: 12, color: 'var(--ink-3)' }}>
              尚未保存技术栈。
              {onOpenWizard && (
                <div style={{ marginTop: 12 }}>
                  <button type="button" className="vh-btn vh-btn-primary" onClick={onOpenWizard}>
                    打开选型向导
                  </button>
                </div>
              )}
            </div>
          ) : (
            stacks.map((s) => {
              const on = s.id === (selected?.id ?? null);
              const rating = s.id ? getRating(s.id) : null;
              const stackIssues =
                s.layers && Object.keys(s.layers).length > 0 ? graph.validateStack(s.layers) : [];
              return (
                <button
                  key={s.id ?? s.name}
                  type="button"
                  onClick={() => s.id && pickStack(s.id)}
                  className="vh-card flex flex-col gap-1 p-3 text-left"
                  data-selected={on ? 'true' : 'false'}
                  style={{
                    marginBottom: 8,
                    cursor: 'pointer',
                    width: '100%',
                    fontFamily: 'var(--font-body)',
                  }}
                >
                  <div className="flex items-center gap-2">
                    <span style={{ fontWeight: 500, flex: 1, color: 'var(--ink-1)' }}>
                      {s.name ?? s.id}
                    </span>
                    {stackIssues.length > 0 ? (
                      <Icon name="Warning" size={14} color="var(--pigment-warning)" />
                    ) : (
                      <Icon
                        name="CheckCircle"
                        size={14}
                        weight="fill"
                        color="var(--pigment-success)"
                      />
                    )}
                  </div>
                  <div
                    style={{
                      fontSize: 13,
                      color: 'var(--ink-2)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {s.target ?? '—'}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="vh-tag">{Object.keys(s.layers ?? {}).length} 层</span>
                    {rating != null && (
                      <span className="vh-mono" style={{ fontSize: 11, color: 'var(--ink-3)' }}>
                        ★{rating}
                      </span>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </aside>
      )}

      {showDetail && (
        <main className="vh-recipes-detail overflow-y-auto" style={{ flex: 1, minWidth: 0 }}>
          {isMobile && (
            <button
              type="button"
              className="vh-btn vh-recipes-back"
              onClick={() => setMobilePane('list')}
            >
              <Icon name="ArrowLeft" size={16} />
              返回列表
            </button>
          )}
          {!selected?.id ? (
            <div style={{ color: 'var(--ink-3)' }}>选择左侧技术栈查看详情</div>
          ) : (
            <StackDetail
              stack={selected}
              issues={issues}
              note={getNote(selected.id)}
              rating={getRating(selected.id)}
              flash={flash}
              catName={catName}
              resolveName={resolveName}
              onNote={(n) => setNote(selected.id as Id, n)}
              onRating={(r) => setRating(selected.id as Id, r)}
              onRename={(name) => updateStack(selected.id as string, { name })}
              onTarget={(target) => updateStack(selected.id as string, { target })}
              onRecheck={() => {
                setRecheckAt(Date.now());
                flashMsg(issues.length === 0 ? '校验通过' : `发现 ${issues.length} 项问题`);
              }}
              onExportJson={() => exportOneJson(selected)}
              onCopyMd={() => void copyMd(selected)}
              onRemove={() => {
                const id = selected.id as string;
                removeStack(id);
                const next = stacks.find((s) => s.id && s.id !== id);
                setSelectedId(next?.id ?? null);
                if (isMobile) setMobilePane('list');
                flashMsg('已移除');
              }}
              onOpenEntry={onOpenEntry}
            />
          )}
        </main>
      )}
    </div>
  );
}

function StackDetail({
  stack,
  issues,
  note,
  rating,
  flash,
  catName,
  resolveName,
  onNote,
  onRating,
  onRename,
  onTarget,
  onRecheck,
  onExportJson,
  onCopyMd,
  onRemove,
  onOpenEntry,
}: {
  stack: Partial<StackRecipe>;
  issues: StackIssue[];
  note: string;
  rating: number | null;
  flash: string | null;
  catName: (id: string) => string;
  resolveName: (id: string) => string;
  onNote: (n: string) => void;
  onRating: (r: number | null) => void;
  onRename: (name: string) => void;
  onTarget: (target: string) => void;
  onRecheck: () => void;
  onExportJson: () => void;
  onCopyMd: () => void;
  onRemove: () => void;
  onOpenEntry: (id: Id) => void;
}) {
  return (
    <div>
      <div className="flex items-start gap-3" style={{ marginBottom: 12 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <input
            className="vh-input vh-display"
            value={stack.name ?? ''}
            onChange={(e) => onRename(e.target.value)}
            style={{
              fontSize: 24,
              width: '100%',
              border: 'none',
              background: 'transparent',
              padding: 0,
              color: 'var(--ink-1)',
            }}
            aria-label="技术栈名称"
          />
          <input
            className="vh-input"
            value={stack.target ?? ''}
            onChange={(e) => onTarget(e.target.value)}
            placeholder="目标描述"
            style={{
              marginTop: 6,
              width: '100%',
              border: 'none',
              background: 'transparent',
              padding: 0,
              color: 'var(--ink-2)',
              fontSize: 14,
            }}
            aria-label="目标描述"
          />
          <div className="vh-mono" style={{ fontSize: 11, color: 'var(--ink-3)', marginTop: 6 }}>
            {stack.id}
          </div>
        </div>
        <div className="flex flex-wrap gap-2" style={{ justifyContent: 'flex-end' }}>
          <button type="button" className="vh-btn flex items-center gap-1.5" onClick={onRecheck}>
            <Icon name="ArrowsClockwise" size={14} /> 重新校验
          </button>
          <button type="button" className="vh-btn flex items-center gap-1.5" onClick={onCopyMd}>
            <Icon name="Copy" size={14} /> 复制 MD
          </button>
          <button type="button" className="vh-btn flex items-center gap-1.5" onClick={onExportJson}>
            <Icon name="Export" size={14} /> 导出 JSON
          </button>
          <button type="button" className="vh-btn" onClick={onRemove} title="移除">
            <Icon name="Trash" size={14} />
          </button>
        </div>
      </div>

      {flash && (
        <div style={{ color: 'var(--pigment-success)', fontSize: 13, marginBottom: 10 }}>
          {flash}
        </div>
      )}

      <div className="flex items-center gap-2" style={{ marginBottom: 16 }}>
        <span style={{ fontSize: 13, color: 'var(--ink-2)' }}>评分</span>
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            className="vh-btn"
            style={{ padding: '2px 6px' }}
            onClick={() => onRating(rating === n ? null : n)}
            aria-label={`${n} 星`}
          >
            <Icon
              name="Star"
              size={14}
              weight={rating != null && rating >= n ? 'fill' : 'regular'}
              color={rating != null && rating >= n ? 'var(--pigment-warning)' : undefined}
            />
          </button>
        ))}
      </div>

      <label
        htmlFor="stack-note"
        style={{ display: 'block', fontSize: 13, color: 'var(--ink-2)', marginBottom: 6 }}
      >
        备注
      </label>
      <textarea
        id="stack-note"
        className="vh-input"
        value={note}
        onChange={(e) => onNote(e.target.value)}
        rows={3}
        placeholder="个人备注、落地进度、团队约定…"
        style={{ width: '100%', resize: 'vertical', marginBottom: 20 }}
      />

      <Section title="层级组合">
        <div className="flex flex-col gap-2">
          {Object.entries(stack.layers ?? {}).map(([cat, id]) => (
            <div key={cat} className="flex items-center gap-2" style={{ fontSize: 14 }}>
              <span style={{ width: 140, color: 'var(--ink-2)', flexShrink: 0 }}>
                {catName(cat)}
              </span>
              <button
                type="button"
                className="vh-link"
                style={{
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  padding: 0,
                }}
                onClick={() => onOpenEntry(id as Id)}
              >
                {resolveName(id)}
              </button>
            </div>
          ))}
          {Object.keys(stack.layers ?? {}).length === 0 && (
            <div style={{ color: 'var(--ink-3)' }}>无层级</div>
          )}
        </div>
      </Section>

      <Section title="校验结果">
        {issues.length === 0 ? (
          <div className="flex items-center gap-2" style={{ color: 'var(--pigment-success)' }}>
            <Icon name="CheckCircle" size={16} weight="fill" />
            通过 validateStack
          </div>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--pigment-warning)', fontSize: 13 }}>
            {issues.map((issue) => (
              <li key={issue.kind === 'conflict' ? `${issue.a}-${issue.b}` : issue.vendorId}>
                {issue.kind === 'conflict'
                  ? `冲突：${resolveName(issue.a)} ↔ ${resolveName(issue.b)}`
                  : `供应商集中：${issue.vendorId} ×${issue.count}`}
              </li>
            ))}
          </ul>
        )}
      </Section>

      {stack.rationaleMd && (
        <Section title="选型理由">
          <div style={{ fontSize: 14, color: 'var(--ink-1)', whiteSpace: 'pre-wrap' }}>
            {stack.rationaleMd}
          </div>
        </Section>
      )}

      {(stack.caveats?.length ?? 0) > 0 && (
        <Section title="注意事项">
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 14 }}>
            {stack.caveats?.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section style={{ marginTop: 20 }}>
      <h2 className="vh-display" style={{ fontSize: 15, color: 'var(--ink-2)', margin: '0 0 8px' }}>
        {title}
      </h2>
      {children}
    </section>
  );
}
