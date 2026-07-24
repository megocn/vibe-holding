import type { Id, StackIssue, StackRecipe } from '@vh/core';
import { learningPath, mineRecipeDrafts } from '@vh/core';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { useIsMobile } from '../lib/use-is-mobile.ts';
import { useUserData } from '../lib/userdata.tsx';
import { Icon } from './Icon.tsx';
import { MyStacksView } from './MyStacksView.tsx';
import { WizardView } from './WizardView.tsx';

export type RecipesMode = 'templates' | 'wizard' | 'mystacks' | 'drafts';

interface RecipesViewProps {
  onOpenEntry: (id: Id) => void;
  initialMode?: RecipesMode;
}

const LAYER_LABELS: Record<string, string> = {
  'coding-agent': '编码代理',
  llm: '大模型',
  framework: '框架',
  ui: 'UI',
  'ui-library': 'UI',
  baas: 'BaaS',
  'baas-auth': 'BaaS',
  deploy: '部署',
  'cloud-deploy': '部署',
  payment: '支付',
};

export function RecipesView({ onOpenEntry, initialMode = 'templates' }: RecipesViewProps) {
  const { bundle, graph } = useContent();
  const { hasAdopted, adoptStack, removeStack, data } = useUserData();
  const isMobile = useIsMobile();
  const [mode, setMode] = useState<RecipesMode>(initialMode);

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);
  const recipes = useMemo(
    () => [...bundle.recipes.values()].sort((a, b) => a.name.localeCompare(b.name)),
    [bundle.recipes],
  );
  const [selectedId, setSelectedId] = useState<string | null>(() => recipes[0]?.id ?? null);
  /** 窄屏：列表 / 详情二选一 */
  const [mobilePane, setMobilePane] = useState<'list' | 'detail'>('list');
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => {
    if (!isMobile) setMobilePane('list');
  }, [isMobile]);

  useEffect(() => {
    if (!isMobile && selectedId == null && recipes[0]) {
      setSelectedId(recipes[0].id);
    }
  }, [isMobile, recipes, selectedId]);

  const selected = selectedId ? bundle.recipes.get(selectedId) : undefined;
  const issues = selected ? graph.validateStack(selected.layers) : [];
  const showList = !isMobile || mobilePane === 'list';
  const showDetail = !isMobile || mobilePane === 'detail';

  function adopt(recipe: StackRecipe) {
    adoptStack(recipe);
    setFlash(`已采用「${recipe.name}」`);
    window.setTimeout(() => setFlash(null), 1600);
  }

  function pickRecipe(id: string) {
    setSelectedId(id);
    if (isMobile) setMobilePane('detail');
  }

  if (mode === 'wizard') {
    return (
      <div className="vh-recipes flex flex-col" style={{ height: '100%', minHeight: 0 }}>
        <div className="vh-recipes-tabs flex items-center gap-2">
          <ModeTabs mode={mode} onChange={setMode} stackCount={data.myStacks.length} />
        </div>
        <div style={{ flex: 1, minHeight: 0 }}>
          <WizardView onOpenEntry={onOpenEntry} onDone={() => setMode('mystacks')} />
        </div>
      </div>
    );
  }

  if (mode === 'mystacks') {
    return (
      <div className="vh-recipes flex flex-col" style={{ height: '100%', minHeight: 0 }}>
        <div className="vh-recipes-tabs flex items-center gap-2">
          <ModeTabs mode={mode} onChange={setMode} stackCount={data.myStacks.length} />
        </div>
        <div style={{ flex: 1, minHeight: 0 }}>
          <MyStacksView onOpenEntry={onOpenEntry} onOpenWizard={() => setMode('wizard')} />
        </div>
      </div>
    );
  }

  if (mode === 'drafts') {
    return (
      <DraftsMode
        onOpenEntry={onOpenEntry}
        onModeChange={setMode}
        stackCount={data.myStacks.length}
        flash={flash}
        onAdopt={(recipe) => {
          adopt(recipe);
          setMode('mystacks');
        }}
      />
    );
  }

  return (
    <div className="vh-recipes flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      <div className="vh-recipes-tabs flex items-center gap-2">
        <ModeTabs mode={mode} onChange={setMode} stackCount={data.myStacks.length} />
      </div>
      <div className="vh-recipes-split flex" style={{ flex: 1, minHeight: 0 }}>
        {showList && (
          <aside className="vh-recipes-list vh-column flex flex-col overflow-y-auto">
            <div className="vh-page-kicker" style={{ padding: '4px 8px 0' }}>
              航路
            </div>
            <div className="vh-text-h3" style={{ margin: '2px 8px 12px', color: 'var(--ink-1)' }}>
              方案模板
            </div>
            {recipes.length === 0 && (
              <div style={{ padding: 12, color: 'var(--ink-3)', fontSize: 14 }}>暂无方案。</div>
            )}
            {recipes.map((r) => {
              const on = r.id === selectedId;
              const adopted = hasAdopted(r.id);
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => pickRecipe(r.id)}
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
                    <span style={{ fontWeight: 500, flex: 1, color: 'var(--ink-1)' }}>{r.name}</span>
                    {adopted && (
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
                    {r.target}
                  </div>
                  <div className="vh-tag" style={{ alignSelf: 'flex-start' }}>
                    {Object.keys(r.layers).length} 层
                  </div>
                </button>
              );
            })}

            {data.myStacks.length > 0 && (
              <div style={{ marginTop: 16, padding: '0 4px' }}>
                <button
                  type="button"
                  className="vh-link"
                  style={{
                    border: 'none',
                    background: 'transparent',
                    cursor: 'pointer',
                    padding: 0,
                    fontSize: 13,
                    color: 'var(--ink-2)',
                    marginBottom: 8,
                  }}
                  onClick={() => setMode('mystacks')}
                >
                  我的技术栈 · {data.myStacks.length} →
                </button>
              </div>
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
            {!selected ? (
              <div style={{ color: 'var(--ink-3)' }}>选择左侧方案查看详情</div>
            ) : (
              <RecipeDetail
                recipe={selected}
                issues={issues}
                adopted={hasAdopted(selected.id)}
                flash={flash}
                onAdopt={() => adopt(selected)}
                onRemove={() => removeStack(selected.id)}
                onOpenEntry={onOpenEntry}
                onViewMyStack={() => setMode('mystacks')}
                resolveName={(id) => bundle.entries.get(id)?.name ?? id}
                resolveVendor={(id) => {
                  const vid = bundle.entries.get(id)?.vendorId;
                  return vid ? bundle.vendors.get(vid)?.name : undefined;
                }}
              />
            )}
          </main>
        )}
      </div>
    </div>
  );
}

function ModeTabs({
  mode,
  onChange,
  stackCount,
}: {
  mode: RecipesMode;
  onChange: (m: RecipesMode) => void;
  stackCount: number;
}) {
  return (
    <div className="flex gap-1.5 flex-wrap">
      {(
        [
          { id: 'templates' as const, label: '方案模板', icon: 'Stack' },
          { id: 'wizard' as const, label: '选型向导', icon: 'MagicWand' },
          { id: 'drafts' as const, label: '共现草稿', icon: 'Sparkle' },
          {
            id: 'mystacks' as const,
            label: stackCount > 0 ? `我的技术栈 (${stackCount})` : '我的技术栈',
            icon: 'BookmarkSimple',
          },
        ] as const
      ).map((t) => {
        const on = mode === t.id;
        return (
          <button
            key={t.id}
            type="button"
            className="vh-chip flex items-center gap-1.5"
            onClick={() => onChange(t.id)}
            data-on={on ? 'true' : 'false'}
          >
            <Icon name={t.icon} size={14} weight={on ? 'fill' : 'regular'} />
            {t.label}
          </button>
        );
      })}
    </div>
  );
}

function DraftsMode({
  onOpenEntry,
  onModeChange,
  stackCount,
  flash,
  onAdopt,
}: {
  onOpenEntry: (id: Id) => void;
  onModeChange: (m: RecipesMode) => void;
  stackCount: number;
  flash: string | null;
  onAdopt: (recipe: StackRecipe) => void;
}) {
  const { bundle, graph } = useContent();
  const { data, hasAdopted } = useUserData();
  const isMobile = useIsMobile();
  const drafts = useMemo(
    () =>
      mineRecipeDrafts(bundle, {
        maxDrafts: 8,
        extraStacks: data.myStacks,
      }),
    [bundle, data.myStacks],
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mobilePane, setMobilePane] = useState<'list' | 'detail'>('list');
  const [pathTarget, setPathTarget] = useState<string>('');

  useEffect(() => {
    if (!isMobile) setMobilePane('list');
  }, [isMobile]);

  useEffect(() => {
    if (drafts.length === 0) {
      setSelectedId(null);
      return;
    }
    if (!isMobile && (!selectedId || !drafts.some((d) => d.id === selectedId))) {
      setSelectedId(drafts[0]?.id ?? null);
    }
  }, [drafts, selectedId, isMobile]);

  const selected = drafts.find((d) => d.id === selectedId);
  const issues = selected ? graph.validateStack(selected.layers) : [];
  const showList = !isMobile || mobilePane === 'list';
  const showDetail = !isMobile || mobilePane === 'detail';

  const path = useMemo(() => {
    if (!pathTarget.trim()) return [];
    return learningPath(bundle, pathTarget.trim() as Id);
  }, [bundle, pathTarget]);

  const entryOptions = useMemo(
    () => [...bundle.entries.values()].sort((a, b) => a.name.localeCompare(b.name)).slice(0, 200),
    [bundle.entries],
  );

  function pickDraft(id: string) {
    setSelectedId(id);
    if (isMobile) setMobilePane('detail');
  }

  return (
    <div className="vh-recipes flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      <div className="vh-recipes-tabs flex items-center gap-2">
        <ModeTabs mode="drafts" onChange={onModeChange} stackCount={stackCount} />
      </div>
      <div className="vh-recipes-split flex" style={{ flex: 1, minHeight: 0 }}>
        {showList && (
          <aside className="vh-recipes-list vh-column flex flex-col overflow-y-auto">
            <div className="vh-page-kicker" style={{ padding: '4px 8px 0' }}>
              G7 共现
            </div>
            <div className="vh-text-h3" style={{ margin: '2px 8px 12px', color: 'var(--ink-1)' }}>
              待确认草稿
            </div>
            <p
              style={{ margin: '0 8px 12px', fontSize: 12, color: 'var(--ink-3)', lineHeight: 1.45 }}
            >
              由方案共现与 commonly_used_with 边自动挖掘；确认后可采用为我的技术栈。
            </p>
            {drafts.length === 0 && (
              <div style={{ padding: 12, color: 'var(--ink-3)', fontSize: 14 }}>
                暂无可用草稿（共现信号不足或均已与模板重复）。
              </div>
            )}
            {drafts.map((r) => {
              const on = r.id === selectedId;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => pickDraft(r.id)}
                  className="vh-card flex flex-col gap-1 p-3 text-left"
                  data-selected={on ? 'true' : 'false'}
                  style={{
                    marginBottom: 8,
                    cursor: 'pointer',
                    width: '100%',
                    fontFamily: 'var(--font-body)',
                  }}
                >
                  <div style={{ fontWeight: 500, color: 'var(--ink-1)' }}>{r.name}</div>
                  <div
                    style={{
                      fontSize: 12,
                      color: 'var(--ink-3)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {r.id}
                  </div>
                  <div className="vh-tag" style={{ alignSelf: 'flex-start' }}>
                    {Object.keys(r.layers).length} 层
                  </div>
                </button>
              );
            })}
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
            {flash && (
              <div style={{ color: 'var(--pigment-success)', fontSize: 13, marginBottom: 10 }}>
                {flash}
              </div>
            )}
            {!selected ? (
              <div style={{ color: 'var(--ink-3)' }}>选择左侧草稿查看详情</div>
            ) : (
              <RecipeDetail
                recipe={selected}
                issues={issues}
                adopted={hasAdopted(selected.id)}
                flash={null}
                onAdopt={() => onAdopt(selected)}
                onRemove={() => undefined}
                onOpenEntry={onOpenEntry}
                onViewMyStack={() => onModeChange('mystacks')}
                resolveName={(id) => bundle.entries.get(id)?.name ?? id}
                resolveVendor={(id) => {
                  const vid = bundle.entries.get(id)?.vendorId;
                  return vid ? bundle.vendors.get(vid)?.name : undefined;
                }}
              />
            )}

            <section
              style={{
                marginTop: 28,
                paddingTop: 20,
                borderTop: '1px solid var(--line)',
              }}
            >
              <div className="vh-page-kicker">G8 学习路径</div>
              <h2 className="vh-text-h3" style={{ margin: '4px 0 8px', color: 'var(--ink-1)' }}>
                前置拓扑
              </h2>
              <p style={{ margin: '0 0 12px', fontSize: 13, color: 'var(--ink-2)' }}>
                沿 prerequisite_of / requires_knowledge 生成到目标条目的建议学习顺序。
              </p>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: 360 }}>
                <span style={{ fontSize: 12, color: 'var(--ink-3)' }}>目标条目</span>
                <select
                  value={pathTarget}
                  onChange={(e) => setPathTarget(e.target.value)}
                  style={{
                    padding: '8px 10px',
                    borderRadius: 'var(--radius)',
                    border: '1px solid var(--line)',
                    background: 'var(--paper-1)',
                    color: 'var(--ink-1)',
                    fontFamily: 'var(--font-body)',
                  }}
                >
                  <option value="">选择…</option>
                  {entryOptions.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.name}
                    </option>
                  ))}
                </select>
              </label>
              {path.length > 0 && (
                <ol
                  style={{
                    margin: '16px 0 0',
                    paddingLeft: 22,
                    color: 'var(--ink-1)',
                    lineHeight: 1.7,
                  }}
                >
                  {path.map((id) => (
                    <li key={id}>
                      <button
                        type="button"
                        className="vh-link"
                        style={{
                          border: 'none',
                          background: 'transparent',
                          cursor: 'pointer',
                          padding: 0,
                          fontSize: 14,
                        }}
                        onClick={() => onOpenEntry(id)}
                      >
                        {bundle.entries.get(id)?.name ?? bundle.concepts.get(id)?.name ?? id}
                      </button>
                    </li>
                  ))}
                </ol>
              )}
            </section>
          </main>
        )}
      </div>
    </div>
  );
}

function RecipeDetail({
  recipe,
  issues,
  adopted,
  flash,
  onAdopt,
  onRemove,
  onOpenEntry,
  onViewMyStack,
  resolveName,
  resolveVendor,
}: {
  recipe: StackRecipe;
  issues: StackIssue[];
  adopted: boolean;
  flash: string | null;
  onAdopt: () => void;
  onRemove: () => void;
  onOpenEntry: (id: Id) => void;
  onViewMyStack: () => void;
  resolveName: (id: Id) => string;
  resolveVendor: (id: Id) => string | undefined;
}) {
  return (
    <div>
      <div className="flex items-start gap-3" style={{ marginBottom: 12 }}>
        <div style={{ flex: 1 }}>
          <div className="vh-page-kicker">航路详情</div>
          <h1 className="vh-text-h1" style={{ margin: 0 }}>
            {recipe.name}
          </h1>
          <div className="vh-text-sm" style={{ color: 'var(--ink-2)', marginTop: 4 }}>
            {recipe.target}
          </div>
        </div>
        {adopted ? (
          <div className="flex gap-2">
            <button type="button" className="vh-btn" onClick={onViewMyStack}>
              查看我的技术栈
            </button>
            <button type="button" className="vh-btn" onClick={onRemove}>
              取消采用
            </button>
          </div>
        ) : (
          <button type="button" className="vh-btn vh-btn-primary" onClick={onAdopt}>
            <Icon name="DownloadSimple" size={14} /> 采用为我的技术栈
          </button>
        )}
      </div>

      {flash && (
        <div style={{ color: 'var(--pigment-success)', fontSize: 13, marginBottom: 10 }}>
          {flash}
        </div>
      )}

      {recipe.estimatedCost && (
        <div className="vh-tag" style={{ marginBottom: 12 }}>
          估算成本 · {recipe.estimatedCost}
        </div>
      )}

      <Section title="分层组合">
        <div className="flex flex-col gap-2">
          {Object.entries(recipe.layers).map(([layer, entryId]) => (
            <div
              key={layer}
              className="flex items-center gap-3"
              style={{
                padding: '8px 10px',
                border: '1px solid var(--line)',
                borderRadius: 'var(--radius)',
                background: 'var(--paper-1)',
              }}
            >
              <span className="vh-tag" style={{ minWidth: 72, textAlign: 'center' }}>
                {LAYER_LABELS[layer] ?? layer}
              </span>
              <button
                type="button"
                className="vh-link"
                style={{
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  padding: 0,
                  fontSize: 15,
                }}
                onClick={() => onOpenEntry(entryId)}
              >
                {resolveName(entryId)}
              </button>
              {resolveVendor(entryId) && (
                <span style={{ color: 'var(--ink-3)', fontSize: 12 }}>
                  {resolveVendor(entryId)}
                </span>
              )}
            </div>
          ))}
        </div>
      </Section>

      <Section title="选型理由">
        <div style={{ color: 'var(--ink-1)', whiteSpace: 'pre-wrap' }}>{recipe.rationaleMd}</div>
      </Section>

      {recipe.caveats.length > 0 && (
        <Section title="注意事项">
          <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--ink-2)' }}>
            {recipe.caveats.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </Section>
      )}

      <Section title="栈校验">
        {issues.length === 0 ? (
          <div style={{ color: 'var(--pigment-success)', fontSize: 14 }}>
            <Icon name="CheckCircle" size={16} weight="fill" /> 未发现冲突或供应商过度集中
          </div>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--pigment-danger)' }}>
            {issues.map((issue) => (
              <li key={JSON.stringify(issue)}>
                {issue.kind === 'conflict'
                  ? `冲突：${resolveName(issue.a)} ↔ ${resolveName(issue.b)}`
                  : `供应商集中：${issue.vendorId} 出现 ${issue.count} 次`}
              </li>
            ))}
          </ul>
        )}
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section style={{ marginTop: 20 }}>
      <h2
        className="vh-display"
        style={{
          fontSize: 15,
          color: 'var(--ink-2)',
          margin: '0 0 8px',
          paddingBottom: 4,
          borderBottom: '1px solid var(--line)',
        }}
      >
        {title}
      </h2>
      {children}
    </section>
  );
}
