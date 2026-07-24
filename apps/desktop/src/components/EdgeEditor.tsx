import { type Confidence, type EdgeType, EdgeType as EdgeTypeSchema, type Id } from '@vh/core';
import { type CSSProperties, type ReactNode, useMemo, useState } from 'react';
import { useContent, useContentEditor } from '../lib/content.tsx';
import { newEdgeId, todayIso, validateEdgeDraft } from '../lib/edge-validate.ts';
import { REL_META } from '../lib/relations.ts';
import { Icon } from './Icon.tsx';

export type EdgeEditTarget = { mode: 'edit'; edgeId: Id } | { mode: 'create'; from?: Id; to?: Id };

interface EdgeEditorProps {
  target: EdgeEditTarget;
  onClose: () => void;
  onSaved: (edgeId: Id) => void;
}

const EDGE_TYPES = EdgeTypeSchema.options;
const CONFIDENCES: Confidence[] = ['verified', 'community', 'inferred'];

export function EdgeEditor({ target, onClose, onSaved }: EdgeEditorProps) {
  const { bundle } = useContent();
  const { saveEdge, revertEdge, deleteEdge, isEdgeOverridden, overlay } = useContentEditor();

  const existing = target.mode === 'edit' ? bundle.edges.find((e) => e.id === target.edgeId) : null;
  const entryOptions = useMemo(
    () =>
      [...bundle.entries.values()]
        .map((e) => ({ id: e.id, name: e.name }))
        .sort((a, b) => a.name.localeCompare(b.name)),
    [bundle.entries],
  );
  // 概念也可作端点
  const nodeOptions = useMemo(() => {
    const concepts = [...bundle.concepts.values()].map((c) => ({
      id: c.id,
      name: `${c.name}（概念）`,
    }));
    return [...entryOptions, ...concepts].sort((a, b) => a.name.localeCompare(b.name));
  }, [entryOptions, bundle.concepts]);

  const [from, setFrom] = useState(
    () => existing?.from ?? (target.mode === 'create' ? (target.from ?? '') : ''),
  );
  const [to, setTo] = useState(
    () => existing?.to ?? (target.mode === 'create' ? (target.to ?? '') : ''),
  );
  const [type, setType] = useState<EdgeType>(() => existing?.type ?? 'commonly_used_with');
  const [weight, setWeight] = useState(() => String(existing?.weight ?? 0.5));
  const [confidence, setConfidence] = useState<Confidence>(
    () => existing?.confidence ?? 'verified',
  );
  const [note, setNote] = useState(() => existing?.note ?? '');
  const [sources, setSources] = useState(() => (existing?.sources ?? []).join('\n'));
  const [createdAt, setCreatedAt] = useState(() => existing?.createdAt ?? todayIso());
  const [edgeId, setEdgeId] = useState(
    () => existing?.id ?? (from && to ? newEdgeId(from as Id, to as Id, type) : ''),
  );
  const [issues, setIssues] = useState<{ path?: string; message: string }[]>([]);
  const [savedFlash, setSavedFlash] = useState(false);

  const nodeIds = useMemo(() => {
    const s = new Set<string>();
    for (const e of bundle.entries.keys()) s.add(e);
    for (const c of bundle.concepts.keys()) s.add(c);
    for (const v of bundle.vendors.keys()) s.add(v);
    for (const c of bundle.categories) s.add(c.id);
    return s;
  }, [bundle]);

  function refreshId(nextFrom: string, nextTo: string, nextType: EdgeType) {
    if (target.mode === 'edit') return;
    if (nextFrom && nextTo) setEdgeId(newEdgeId(nextFrom as Id, nextTo as Id, nextType));
  }

  function save() {
    const weightNum = Number(weight);
    const candidate = {
      id: edgeId.trim(),
      from: from.trim(),
      to: to.trim(),
      type,
      weight: Number.isFinite(weightNum) ? weightNum : weight,
      confidence,
      note: note.trim() || undefined,
      sources: sources
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
      createdAt: createdAt.trim(),
      lastReviewed: existing?.lastReviewed,
    };
    const result = validateEdgeDraft(candidate, {
      nodeIds,
      existing: bundle.edges,
      editingId: target.mode === 'edit' ? target.edgeId : null,
    });
    if (!result.ok) {
      setIssues(result.issues.map((i) => ({ path: i.path, message: `[${i.code}] ${i.message}` })));
      return;
    }
    if (target.mode === 'edit' && result.edge.id !== target.edgeId) {
      setIssues([{ path: 'id', message: '编辑时不可修改边 ID' }]);
      return;
    }
    saveEdge(result.edge);
    setIssues([]);
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 1200);
    onSaved(result.edge.id);
  }

  const title = target.mode === 'edit' ? `编辑边 · ${existing?.id ?? target.edgeId}` : '新建关系边';

  const err = (path: string) => issues.find((i) => i.path === path)?.message;
  const generalIssues = issues.filter((i) => !i.path);

  return (
    <div className="overflow-y-auto" style={{ padding: 24, maxWidth: 640 }}>
      <div className="flex items-center gap-2" style={{ marginBottom: 16 }}>
        <button type="button" className="vh-btn" onClick={onClose}>
          <Icon name="ArrowLeft" size={14} /> 返回
        </button>
        <h1 className="vh-display" style={{ fontSize: 22, margin: 0, flex: 1 }}>
          {title}
        </h1>
        {target.mode === 'edit' && isEdgeOverridden(target.edgeId) && (
          <span className="vh-tag" style={{ color: 'var(--pigment-warning)' }}>
            本地覆盖
          </span>
        )}
        {savedFlash && (
          <span style={{ color: 'var(--pigment-success)', fontSize: 13 }}>已保存</span>
        )}
      </div>

      {generalIssues.length > 0 && (
        <div style={{ color: 'var(--pigment-danger)', marginBottom: 12, fontSize: 13 }}>
          {generalIssues.map((i) => (
            <div key={i.message}>{i.message}</div>
          ))}
        </div>
      )}

      <Field label="边 ID" error={err('id')}>
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={edgeId}
          disabled={target.mode === 'edit'}
          onChange={(e) => setEdgeId(e.target.value)}
        />
      </Field>

      <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
        <Field label="From" error={err('from')} style={{ flex: 1, minWidth: 180 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={from}
            onChange={(e) => {
              setFrom(e.target.value);
              refreshId(e.target.value, to, type);
            }}
          >
            <option value="">选择节点…</option>
            {nodeOptions.map((n) => (
              <option key={n.id} value={n.id}>
                {n.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="To" error={err('to')} style={{ flex: 1, minWidth: 180 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={to}
            onChange={(e) => {
              setTo(e.target.value);
              refreshId(from, e.target.value, type);
            }}
          >
            <option value="">选择节点…</option>
            {nodeOptions.map((n) => (
              <option key={n.id} value={n.id}>
                {n.name}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <Field label="关系类型" error={err('type')}>
        <select
          className="vh-input"
          style={{ width: '100%' }}
          value={type}
          onChange={(e) => {
            const t = e.target.value as EdgeType;
            setType(t);
            refreshId(from, to, t);
          }}
        >
          {EDGE_TYPES.map((t) => (
            <option key={t} value={t}>
              {REL_META[t]?.label ?? t}（{t}）
            </option>
          ))}
        </select>
      </Field>

      <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
        <Field label="权重 0–1" error={err('weight')} style={{ flex: 1, minWidth: 120 }}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
          />
        </Field>
        <Field label="可信度" error={err('confidence')} style={{ flex: 1, minWidth: 120 }}>
          <select
            className="vh-input"
            style={{ width: '100%' }}
            value={confidence}
            onChange={(e) => setConfidence(e.target.value as Confidence)}
          >
            {CONFIDENCES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </Field>
        <Field label="创建日期" error={err('createdAt')} style={{ flex: 1, minWidth: 140 }}>
          <input
            className="vh-input"
            style={{ width: '100%', boxSizing: 'border-box' }}
            value={createdAt}
            onChange={(e) => setCreatedAt(e.target.value)}
          />
        </Field>
      </div>

      <Field label="备注" error={err('note')}>
        <input
          className="vh-input"
          style={{ width: '100%', boxSizing: 'border-box' }}
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </Field>
      <Field label="来源 URL（每行一条）" error={err('sources')}>
        <textarea
          className="vh-input"
          rows={3}
          style={{ width: '100%', boxSizing: 'border-box', resize: 'vertical' }}
          value={sources}
          onChange={(e) => setSources(e.target.value)}
        />
      </Field>

      <div className="flex flex-wrap gap-2" style={{ marginTop: 8 }}>
        <button type="button" className="vh-btn" onClick={save}>
          <Icon name="FloppyDisk" size={14} /> 保存到本机
        </button>
        {target.mode === 'edit' && overlay.edges[target.edgeId] && (
          <button
            type="button"
            className="vh-btn"
            onClick={() => {
              revertEdge(target.edgeId);
              onClose();
            }}
          >
            恢复基础库版本
          </button>
        )}
        {target.mode === 'edit' && (
          <button
            type="button"
            className="vh-btn"
            onClick={() => {
              if (window.confirm('从本机视图移除这条边？')) {
                deleteEdge(target.edgeId);
                onClose();
              }
            }}
            style={{ color: 'var(--pigment-danger)' }}
          >
            移除边
          </button>
        )}
        <button type="button" className="vh-btn" onClick={onClose}>
          取消
        </button>
      </div>
      <div style={{ marginTop: 10, fontSize: 12, color: 'var(--ink-3)' }}>
        保存即校验 schema / 引用 / 自环 / 重复 / 冲突互斥。仅写本机覆盖层。
      </div>
    </div>
  );
}

function Field({
  label,
  error,
  children,
  style,
}: {
  label: string;
  error?: string;
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
    </div>
  );
}
