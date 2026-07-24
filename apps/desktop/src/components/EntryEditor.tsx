import {
  type Entry,
  Entry as EntrySchema,
  type ExternalLink,
  type ExternalLinkKind,
  EXTERNAL_LINK_KINDS,
  type Id,
  type Maturity,
  type PricingModel,
  type Region,
  type TutorialLink,
  type TutorialPlatform,
  TUTORIAL_PLATFORMS,
} from '@vh/core';
import { type CSSProperties, type ReactNode, useMemo, useRef, useState } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import { todayIso } from '../lib/intel.ts';
import { Icon } from './Icon.tsx';

interface EntryEditorProps {
  entryId: Id;
  onClose: () => void;
  onSaved: (id: Id) => void;
}

type TutorialDraft = {
  platform: TutorialPlatform;
  url: string;
  query: string;
  note: string;
};

type ExternalDraft = {
  kind: ExternalLinkKind;
  url: string;
  query: string;
  note: string;
};

type Draft = {
  id: string;
  name: string;
  category: string;
  vendorId: string;
  region: Region;
  oneLiner: string;
  descriptionMd: string;
  officialUrl: string;
  docsUrl: string;
  githubUrl: string;
  pricingUrl: string;
  statusUrl: string;
  consoleUrl: string;
  playgroundUrl: string;
  changelogUrl: string;
  loginUrl: string;
  pricingModel: PricingModel;
  pricingNotes: string;
  chinaAccessible: boolean;
  needsCompany: boolean;
  needsIcp: boolean;
  tags: string;
  maturity: Maturity;
  usageGuideMd: string;
  tutorialLinks: TutorialDraft[];
  externalLinks: ExternalDraft[];
  pitfalls: string;
  lastReviewed: string;
};

function tutorialToDraft(t: TutorialLink): TutorialDraft {
  return {
    platform: t.platform,
    url: t.url ?? '',
    query: t.query ?? '',
    note: t.note ?? '',
  };
}

function emptyTutorialDraft(): TutorialDraft {
  return { platform: 'bilibili', url: '', query: '', note: '' };
}

function patchTutorialRow(
  rows: TutorialDraft[],
  index: number,
  patch: Partial<TutorialDraft>,
): TutorialDraft[] {
  const cur = rows[index] ?? emptyTutorialDraft();
  const next = [...rows];
  next[index] = {
    platform: patch.platform ?? cur.platform,
    url: patch.url ?? cur.url,
    query: patch.query ?? cur.query,
    note: patch.note ?? cur.note,
  };
  return next;
}

function externalToDraft(t: ExternalLink): ExternalDraft {
  return {
    kind: t.kind,
    url: t.url ?? '',
    query: t.query ?? '',
    note: t.note ?? '',
  };
}

function emptyExternalDraft(): ExternalDraft {
  return { kind: 'what_is', url: '', query: '', note: '' };
}

function patchExternalRow(
  rows: ExternalDraft[],
  index: number,
  patch: Partial<ExternalDraft>,
): ExternalDraft[] {
  const cur = rows[index] ?? emptyExternalDraft();
  const next = [...rows];
  next[index] = {
    kind: patch.kind ?? cur.kind,
    url: patch.url ?? cur.url,
    query: patch.query ?? cur.query,
    note: patch.note ?? cur.note,
  };
  return next;
}

function entryToDraft(e: Entry): Draft {
  return {
    id: e.id,
    name: e.name,
    category: e.category,
    vendorId: e.vendorId ?? '',
    region: e.region,
    oneLiner: e.oneLiner,
    descriptionMd: e.descriptionMd,
    officialUrl: e.officialUrl,
    docsUrl: e.docsUrl ?? '',
    githubUrl: e.githubUrl ?? '',
    pricingUrl: e.pricingUrl ?? '',
    statusUrl: e.statusUrl ?? '',
    consoleUrl: e.consoleUrl ?? '',
    playgroundUrl: e.playgroundUrl ?? '',
    changelogUrl: e.changelogUrl ?? '',
    loginUrl: e.loginUrl ?? '',
    pricingModel: e.pricing.model,
    pricingNotes: e.pricing.notes ?? '',
    chinaAccessible: e.availability.chinaAccessible,
    needsCompany: e.availability.needsCompany,
    needsIcp: e.availability.needsIcp,
    tags: e.tags.join(', '),
    maturity: e.maturity,
    usageGuideMd: e.usageGuideMd ?? '',
    tutorialLinks: (e.tutorialLinks ?? []).map(tutorialToDraft),
    externalLinks: (e.externalLinks ?? []).map(externalToDraft),
    pitfalls: e.pitfalls.join('\n'),
    lastReviewed: e.lastReviewed,
  };
}

function draftTutorialsToLinks(rows: TutorialDraft[]): TutorialLink[] {
  return rows
    .map((r) => {
      const url = r.url.trim();
      const query = r.query.trim();
      const note = r.note.trim();
      if (!url && !query && !note) return null;
      const link: TutorialLink = { platform: r.platform };
      if (url) link.url = url;
      if (query) link.query = query;
      if (note) link.note = note;
      return link;
    })
    .filter((x): x is TutorialLink => x !== null);
}

function draftExternalsToLinks(rows: ExternalDraft[]): ExternalLink[] {
  return rows
    .map((r) => {
      const url = r.url.trim();
      const query = r.query.trim();
      const note = r.note.trim();
      if (!url && !query && !note) return null;
      const link: ExternalLink = { kind: r.kind };
      if (url) link.url = url;
      if (query) link.query = query;
      if (note) link.note = note;
      return link;
    })
    .filter((x): x is ExternalLink => x !== null);
}

function optUrl(s: string): string | undefined {
  const t = s.trim();
  return t || undefined;
}

function draftToCandidate(d: Draft, base: Entry): unknown {
  return {
    ...base,
    id: d.id.trim(),
    name: d.name.trim(),
    category: d.category.trim(),
    vendorId: d.vendorId.trim() || undefined,
    region: d.region,
    oneLiner: d.oneLiner.trim(),
    descriptionMd: d.descriptionMd,
    officialUrl: d.officialUrl.trim(),
    docsUrl: optUrl(d.docsUrl),
    githubUrl: optUrl(d.githubUrl),
    pricingUrl: optUrl(d.pricingUrl),
    statusUrl: optUrl(d.statusUrl),
    consoleUrl: optUrl(d.consoleUrl),
    playgroundUrl: optUrl(d.playgroundUrl),
    changelogUrl: optUrl(d.changelogUrl),
    loginUrl: optUrl(d.loginUrl),
    pricing: {
      model: d.pricingModel,
      notes: d.pricingNotes.trim() || undefined,
      currency: base.pricing.currency,
    },
    availability: {
      chinaAccessible: d.chinaAccessible,
      needsCompany: d.needsCompany,
      needsIcp: d.needsIcp,
      regions: base.availability.regions,
    },
    tags: d.tags
      .split(/[,，]/)
      .map((t) => t.trim())
      .filter(Boolean),
    maturity: d.maturity,
    usageGuideMd: d.usageGuideMd.trim() || undefined,
    tutorialLinks: draftTutorialsToLinks(d.tutorialLinks),
    externalLinks: draftExternalsToLinks(d.externalLinks),
    pitfalls: d.pitfalls
      .split('\n')
      .map((p) => p.trim())
      .filter(Boolean),
    lastReviewed: d.lastReviewed.trim(),
  };
}

export function EntryEditor({ entryId, onClose, onSaved }: EntryEditorProps) {
  const { bundle, categories } = useContent();
  const { saveEntry, isOverridden, revertEntry } = useContentEditor();
  const base = bundle.entries.get(entryId);
  const [draft, setDraft] = useState<Draft | null>(() => (base ? entryToDraft(base) : null));
  /** 打开编辑器时的复核日；保存时若用户未改动则自动刷新为今天 */
  const initialReviewedRef = useRef(base?.lastReviewed ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);

  const categoryOptions = useMemo(() => {
    const sections = new Map(
      categories.filter((c) => c.kind === 'section').map((c) => [c.id, c]),
    );
    return categories
      .filter((c) => c.kind === 'leaf')
      .sort((a, b) => {
        const sa = sections.get(a.parent ?? '')?.order ?? 0;
        const sb = sections.get(b.parent ?? '')?.order ?? 0;
        if (sa !== sb) return sa - sb;
        return a.order - b.order;
      })
      .map((c) => {
        const sec = sections.get(c.parent ?? '');
        const prefix = sec?.code ? `${sec.code} · ${sec.name}` : sec?.name ?? '';
        return { id: c.id, label: prefix ? `${prefix} › ${c.name}` : c.name };
      });
  }, [categories]);

  if (!base || !draft) {
    return (
      <div style={{ padding: 24, color: 'var(--ink-3)' }}>
        条目不存在
        <button type="button" className="vh-btn" style={{ marginLeft: 12 }} onClick={onClose}>
          返回
        </button>
      </div>
    );
  }

  function patch<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((prev) => (prev ? { ...prev, [key]: value } : prev));
  }

  function save() {
    if (!draft || !base) return;
    const reviewedUnchanged = draft.lastReviewed.trim() === initialReviewedRef.current;
    const nextDraft = reviewedUnchanged
      ? { ...draft, lastReviewed: todayIso() }
      : draft;
    const candidate = draftToCandidate(nextDraft, base);
    const result = EntrySchema.safeParse(candidate);
    if (!result.success) {
      const errs: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const path = issue.path.join('.') || '_';
        if (!errs[path]) errs[path] = issue.message;
      }
      setFieldErrors(errs);
      setFormError('请修正标红字段后再保存');
      return;
    }
    // id 不可在编辑现有条目时更改（覆盖层按原 id）
    if (result.data.id !== entryId) {
      setFormError('暂不支持修改条目 ID');
      return;
    }
    saveEntry(result.data);
    setDraft(nextDraft);
    initialReviewedRef.current = result.data.lastReviewed;
    setFieldErrors({});
    setFormError(null);
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 1200);
    onSaved(result.data.id);
  }

  const err = (path: string) => fieldErrors[path];

  return (
    <div className="overflow-y-auto" style={{ padding: 24, maxWidth: 720 }}>
      <div className="flex items-center gap-2" style={{ marginBottom: 16 }}>
        <button type="button" className="vh-btn" onClick={onClose}>
          <Icon name="ArrowLeft" size={14} /> 返回
        </button>
        <h1 className="vh-display" style={{ fontSize: 22, margin: 0, flex: 1 }}>
          编辑 · {base.name}
        </h1>
        {isOverridden(entryId) && (
          <span className="vh-tag" style={{ color: 'var(--pigment-warning)' }}>
            本地覆盖
          </span>
        )}
        {savedFlash && (
          <span style={{ color: 'var(--pigment-success)', fontSize: 13 }}>已保存</span>
        )}
      </div>

      {formError && (
        <div style={{ color: 'var(--pigment-danger)', marginBottom: 12, fontSize: 14 }}>
          {formError}
        </div>
      )}

      <Field label="名称" error={err('name')}>
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={draft.name}
          onChange={(e) => patch('name', e.target.value)}
        />
      </Field>

      <Field
        label="选型一句话（≤80）"
        error={err('oneLiner')}
        hint="同层差异化特点（能力/生态/约束），用「·」串点；勿写简介或「适合…时」"
      >
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={draft.oneLiner}
          maxLength={80}
          onChange={(e) => patch('oneLiner', e.target.value)}
        />
      </Field>

      <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
        <Field label="分类" error={err('category')} style={{ flex: 1, minWidth: 160 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={draft.category}
            onChange={(e) => patch('category', e.target.value)}
          >
            {categoryOptions.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="地区" error={err('region')} style={{ flex: 1, minWidth: 120 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={draft.region}
            onChange={(e) => patch('region', e.target.value as Region)}
          >
            <option value="overseas">国外</option>
            <option value="domestic">国内</option>
            <option value="both">国内外</option>
          </select>
        </Field>
        <Field label="成熟度" error={err('maturity')} style={{ flex: 1, minWidth: 120 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={draft.maturity}
            onChange={(e) => patch('maturity', e.target.value as Maturity)}
          >
            <option value="experimental">实验</option>
            <option value="beta">测试</option>
            <option value="stable">稳定</option>
            <option value="mature">成熟</option>
          </select>
        </Field>
      </div>

      <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
        <Field label="定价模型" error={err('pricing.model')} style={{ flex: 1, minWidth: 140 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={draft.pricingModel}
            onChange={(e) => patch('pricingModel', e.target.value as PricingModel)}
          >
            <option value="free">免费</option>
            <option value="freemium">免费增值</option>
            <option value="subscription">订阅</option>
            <option value="usage">按量</option>
            <option value="open-source">开源</option>
          </select>
        </Field>
        <Field label="定价说明" error={err('pricing.notes')} style={{ flex: 2, minWidth: 200 }}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.pricingNotes}
            onChange={(e) => patch('pricingNotes', e.target.value)}
          />
        </Field>
      </div>

      <Field label="官网 URL" error={err('officialUrl')}>
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={draft.officialUrl}
          onChange={(e) => patch('officialUrl', e.target.value)}
        />
      </Field>
      <Field label="文档 URL（可选）" error={err('docsUrl')}>
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={draft.docsUrl}
          onChange={(e) => patch('docsUrl', e.target.value)}
        />
      </Field>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 12,
          marginBottom: 12,
        }}
      >
        <Field label="源码 GitHub（可选）" error={err('githubUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.githubUrl}
            onChange={(e) => patch('githubUrl', e.target.value)}
          />
        </Field>
        <Field label="定价页（可选）" error={err('pricingUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.pricingUrl}
            onChange={(e) => patch('pricingUrl', e.target.value)}
          />
        </Field>
        <Field label="状态页（可选）" error={err('statusUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.statusUrl}
            onChange={(e) => patch('statusUrl', e.target.value)}
          />
        </Field>
        <Field label="控制台（可选）" error={err('consoleUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.consoleUrl}
            onChange={(e) => patch('consoleUrl', e.target.value)}
          />
        </Field>
        <Field label="沙箱 / Playground（可选）" error={err('playgroundUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.playgroundUrl}
            onChange={(e) => patch('playgroundUrl', e.target.value)}
          />
        </Field>
        <Field label="更新日志（可选）" error={err('changelogUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.changelogUrl}
            onChange={(e) => patch('changelogUrl', e.target.value)}
          />
        </Field>
        <Field label="登录页（可选）" error={err('loginUrl')}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={draft.loginUrl}
            onChange={(e) => patch('loginUrl', e.target.value)}
          />
        </Field>
      </div>

      <Field label="说明（Markdown）" error={err('descriptionMd')}>
        <textarea
          className="vh-input"
          rows={5}
          style={{ width: '100%', boxSizing: 'border-box', resize: 'vertical' }}
          value={draft.descriptionMd}
          onChange={(e) => patch('descriptionMd', e.target.value)}
        />
      </Field>
      <Field label="使用方式（Markdown）" error={err('usageGuideMd')}>
        <textarea
          className="vh-input"
          rows={4}
          style={{ width: '100%', boxSizing: 'border-box', resize: 'vertical' }}
          value={draft.usageGuideMd}
          onChange={(e) => patch('usageGuideMd', e.target.value)}
        />
      </Field>

      <div style={{ marginBottom: 16 }}>
        <div
          className="flex items-center gap-2"
          style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 6 }}
        >
          <span>延伸外链（可选覆盖）</span>
          <button
            type="button"
            className="vh-btn"
            style={{ padding: '2px 8px', fontSize: 12 }}
            onClick={() =>
              setDraft((prev) =>
                prev
                  ? { ...prev, externalLinks: [...prev.externalLinks, emptyExternalDraft()] }
                  : prev,
              )
            }
          >
            <Icon name="Plus" size={12} /> 添加
          </button>
        </div>
        <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 8 }}>
          「这是什么？/Wiki」无 URL 时跳转搜索；其余种类也可在此精选覆盖一等字段。
        </div>
        {err('externalLinks') && (
          <div style={{ color: 'var(--pigment-danger)', fontSize: 12, marginBottom: 6 }}>
            {err('externalLinks')}
          </div>
        )}
        {draft.externalLinks.map((row, i) => (
          <div
            key={`${row.kind}-${i}`}
            className="flex gap-2"
            style={{ flexWrap: 'wrap', marginBottom: 8, alignItems: 'flex-start' }}
          >
            <select
              className="vh-input"
              style={{ width: 120 }}
              value={row.kind}
              onChange={(e) => {
                const kind = e.target.value as ExternalLinkKind;
                setDraft((prev) =>
                  prev
                    ? { ...prev, externalLinks: patchExternalRow(prev.externalLinks, i, { kind }) }
                    : prev,
                );
              }}
            >
              {EXTERNAL_LINK_KINDS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
            <input
              className="vh-input"
              style={{ flex: 2, minWidth: 160, boxSizing: 'border-box' }}
              placeholder="精选 URL（可选）"
              value={row.url}
              onChange={(e) => {
                const url = e.target.value;
                setDraft((prev) =>
                  prev
                    ? { ...prev, externalLinks: patchExternalRow(prev.externalLinks, i, { url }) }
                    : prev,
                );
              }}
            />
            <input
              className="vh-input"
              style={{ flex: 1, minWidth: 100, boxSizing: 'border-box' }}
              placeholder="搜索词"
              value={row.query}
              onChange={(e) => {
                const query = e.target.value;
                setDraft((prev) =>
                  prev
                    ? {
                        ...prev,
                        externalLinks: patchExternalRow(prev.externalLinks, i, { query }),
                      }
                    : prev,
                );
              }}
            />
            <input
              className="vh-input"
              style={{ flex: 1, minWidth: 80, boxSizing: 'border-box' }}
              placeholder="备注"
              value={row.note}
              onChange={(e) => {
                const note = e.target.value;
                setDraft((prev) =>
                  prev
                    ? { ...prev, externalLinks: patchExternalRow(prev.externalLinks, i, { note }) }
                    : prev,
                );
              }}
            />
            <button
              type="button"
              className="vh-btn"
              style={{ padding: '4px 8px' }}
              title="删除"
              onClick={() =>
                setDraft((prev) =>
                  prev
                    ? {
                        ...prev,
                        externalLinks: prev.externalLinks.filter((_, j) => j !== i),
                      }
                    : prev,
                )
              }
            >
              <Icon name="Trash" size={12} />
            </button>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: 16 }}>
        <div
          className="flex items-center gap-2"
          style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 6 }}
        >
          <span>教程入口（可选覆盖）</span>
          <button
            type="button"
            className="vh-btn"
            style={{ padding: '2px 8px', fontSize: 12 }}
            onClick={() =>
              setDraft((prev) =>
                prev
                  ? { ...prev, tutorialLinks: [...prev.tutorialLinks, emptyTutorialDraft()] }
                  : prev,
              )
            }
          >
            <Icon name="Plus" size={12} /> 添加
          </button>
        </div>
        <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 8 }}>
          留空则详情页用条目名跳转各平台搜索；填写 URL 可直达精选课。
        </div>
        {err('tutorialLinks') && (
          <div style={{ color: 'var(--pigment-danger)', fontSize: 12, marginBottom: 6 }}>
            {err('tutorialLinks')}
          </div>
        )}
        {draft.tutorialLinks.map((row, i) => (
          <div
            key={`${row.platform}-${i}`}
            className="flex gap-2"
            style={{ flexWrap: 'wrap', marginBottom: 8, alignItems: 'flex-start' }}
          >
            <select
              className="vh-input"
              style={{ width: 120 }}
              value={row.platform}
              onChange={(e) => {
                const platform = e.target.value as TutorialPlatform;
                setDraft((prev) =>
                  prev
                    ? { ...prev, tutorialLinks: patchTutorialRow(prev.tutorialLinks, i, { platform }) }
                    : prev,
                );
              }}
            >
              {TUTORIAL_PLATFORMS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
            <input
              className="vh-input"
              style={{ flex: 2, minWidth: 160, boxSizing: 'border-box' }}
              placeholder="精选 URL（可选）"
              value={row.url}
              onChange={(e) => {
                const url = e.target.value;
                setDraft((prev) =>
                  prev
                    ? { ...prev, tutorialLinks: patchTutorialRow(prev.tutorialLinks, i, { url }) }
                    : prev,
                );
              }}
            />
            <input
              className="vh-input"
              style={{ flex: 1, minWidth: 100, boxSizing: 'border-box' }}
              placeholder="搜索词"
              value={row.query}
              onChange={(e) => {
                const query = e.target.value;
                setDraft((prev) =>
                  prev
                    ? { ...prev, tutorialLinks: patchTutorialRow(prev.tutorialLinks, i, { query }) }
                    : prev,
                );
              }}
            />
            <input
              className="vh-input"
              style={{ flex: 1, minWidth: 80, boxSizing: 'border-box' }}
              placeholder="备注"
              value={row.note}
              onChange={(e) => {
                const note = e.target.value;
                setDraft((prev) =>
                  prev
                    ? { ...prev, tutorialLinks: patchTutorialRow(prev.tutorialLinks, i, { note }) }
                    : prev,
                );
              }}
            />
            <button
              type="button"
              className="vh-btn"
              style={{ padding: '4px 8px' }}
              title="删除"
              onClick={() =>
                setDraft((prev) =>
                  prev
                    ? {
                        ...prev,
                        tutorialLinks: prev.tutorialLinks.filter((_, j) => j !== i),
                      }
                    : prev,
                )
              }
            >
              <Icon name="Trash" size={12} />
            </button>
          </div>
        ))}
      </div>

      <Field label="坑点（每行一条）" error={err('pitfalls')}>
        <textarea
          className="vh-input"
          rows={3}
          style={{ width: '100%', boxSizing: 'border-box', resize: 'vertical' }}
          value={draft.pitfalls}
          onChange={(e) => patch('pitfalls', e.target.value)}
        />
      </Field>
      <Field label="标签（逗号分隔）" error={err('tags')}>
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={draft.tags}
          onChange={(e) => patch('tags', e.target.value)}
        />
      </Field>
      <Field
        label="最近复核日期"
        error={err('lastReviewed')}
        hint="保存时若未改动此字段，将自动标为今天"
      >
        <div className="flex gap-2" style={{ alignItems: 'center' }}>
          <input
            className="vh-input"
            style={{ flex: 1, boxSizing: 'border-box' }}
            value={draft.lastReviewed}
            placeholder="YYYY-MM-DD"
            onChange={(e) => patch('lastReviewed', e.target.value)}
          />
          <button
            type="button"
            className="vh-btn"
            onClick={() => patch('lastReviewed', todayIso())}
          >
            标为今天
          </button>
        </div>
      </Field>

      <div className="flex flex-wrap gap-4" style={{ margin: '8px 0 16px', fontSize: 14 }}>
        <label className="flex items-center gap-2" style={{ cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={draft.chinaAccessible}
            onChange={(e) => patch('chinaAccessible', e.target.checked)}
          />
          国内可访问
        </label>
        <label className="flex items-center gap-2" style={{ cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={draft.needsCompany}
            onChange={(e) => patch('needsCompany', e.target.checked)}
          />
          需公司主体
        </label>
        <label className="flex items-center gap-2" style={{ cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={draft.needsIcp}
            onChange={(e) => patch('needsIcp', e.target.checked)}
          />
          需备案
        </label>
      </div>

      <div className="flex flex-wrap gap-2" style={{ marginTop: 8 }}>
        <button type="button" className="vh-btn" onClick={save}>
          <Icon name="FloppyDisk" size={14} /> 保存到本机
        </button>
        {isOverridden(entryId) && (
          <button
            type="button"
            className="vh-btn"
            onClick={() => {
              revertEntry(entryId);
              onClose();
            }}
          >
            恢复基础库版本
          </button>
        )}
        <button type="button" className="vh-btn" onClick={onClose}>
          取消
        </button>
      </div>
      <div style={{ marginTop: 10, fontSize: 12, color: 'var(--ink-3)' }}>
        修改仅存本机覆盖层（localStorage），不写 content/。可在设置中导出 JSON 后手工合并入库。
      </div>
    </div>
  );
}

function Field({
  label,
  error,
  hint,
  children,
  style,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <div style={{ marginBottom: 12, ...style }}>
      <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 4 }}>{label}</div>
      {children}
      {error && (
        <div style={{ color: 'var(--pigment-danger)', fontSize: 12, marginTop: 4 }}>{error}</div>
      )}
      {!error && hint && (
        <div style={{ color: 'var(--ink-3)', fontSize: 12, marginTop: 4 }}>{hint}</div>
      )}
    </div>
  );
}
