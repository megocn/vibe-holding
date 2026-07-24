import type { Id, StackRecipe } from '@vh/core';
import { buildGraph, sectionIdOf } from '@vh/core';
import { type ReactNode, useMemo, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { useUserData } from '../lib/userdata.tsx';
import {
  DEFAULT_ANSWERS,
  type WizardAnswers,
  layersForAnswers,
  prefsFromAnswers,
  slugifyStackId,
} from '../lib/wizard.ts';
import { Icon } from './Icon.tsx';

interface WizardViewProps {
  onOpenEntry: (id: Id) => void;
  onDone?: () => void;
}

type Phase = 'answers' | 'layers' | 'summary';

export function WizardView({ onOpenEntry, onDone }: WizardViewProps) {
  const { bundle, categories } = useContent();
  const { adoptStack, data: userData } = useUserData();
  const [phase, setPhase] = useState<Phase>('answers');
  const [answers, setAnswers] = useState<WizardAnswers>(DEFAULT_ANSWERS);
  const [layerIndex, setLayerIndex] = useState(0);
  const [layers, setLayers] = useState<Record<string, Id>>({});
  const [stackName, setStackName] = useState('我的选型方案');
  const [flash, setFlash] = useState<string | null>(null);

  /** 叠加个人共现边，使选型推荐尊重我的技术栈习惯。 */
  const graph = useMemo(
    () => buildGraph(bundle, userData.personalEdges),
    [bundle, userData.personalEdges],
  );

  const layerKeys = useMemo(() => {
    const keys = layersForAnswers(answers);
    return keys.filter((cat) =>
      [...bundle.entries.values()].some(
        (e) => e.category === cat || sectionIdOf(categories, e.category) === cat,
      ),
    );
  }, [answers, bundle.entries, categories]);

  const prefs = useMemo(() => prefsFromAnswers(answers), [answers]);
  const currentCat = layerKeys[layerIndex];
  const selectedIds = Object.values(layers);
  const candidates = useMemo(() => {
    if (!currentCat || phase !== 'layers') return [];
    return graph.recommendForCategory(selectedIds, currentCat, prefs);
  }, [graph, selectedIds, currentCat, prefs, phase]);

  const issues = useMemo(() => graph.validateStack(layers), [graph, layers]);
  const catName = (id: Id) => bundle.categories.find((c) => c.id === id)?.name ?? id;

  function startLayers() {
    setLayers({});
    setLayerIndex(0);
    setPhase('layers');
  }

  function pick(entryId: Id) {
    if (!currentCat) return;
    const next = { ...layers, [currentCat]: entryId };
    setLayers(next);
    if (layerIndex + 1 < layerKeys.length) {
      setLayerIndex((i) => i + 1);
    } else {
      setPhase('summary');
    }
  }

  function skipLayer() {
    if (!currentCat) return;
    const next = { ...layers };
    delete next[currentCat];
    setLayers(next);
    if (layerIndex + 1 < layerKeys.length) {
      setLayerIndex((i) => i + 1);
    } else {
      setPhase('summary');
    }
  }

  function goBack() {
    if (phase === 'summary') {
      setPhase('layers');
      setLayerIndex(Math.max(0, layerKeys.length - 1));
      return;
    }
    if (phase === 'layers') {
      if (layerIndex === 0) {
        setPhase('answers');
        return;
      }
      const prevCat = layerKeys[layerIndex - 1];
      if (prevCat) {
        setLayers((prev) => {
          const n = { ...prev };
          delete n[prevCat];
          return n;
        });
      }
      setLayerIndex((i) => i - 1);
    }
  }

  function save() {
    const recipe: StackRecipe = {
      id: slugifyStackId(stackName),
      name: stackName.trim() || '我的选型方案',
      target: targetLabel(answers),
      layers,
      rationaleMd: `由选型向导生成（市场=${answers.market}，预算=${answers.budget}，收费=${answers.monetize ? '是' : '否'}）。`,
      caveats: issues.map(issueText),
    };
    adoptStack(recipe);
    setFlash(`已保存「${recipe.name}」`);
    window.setTimeout(() => {
      setFlash(null);
      onDone?.();
    }, 1200);
  }

  function issueText(i: (typeof issues)[number]): string {
    if (i.kind === 'conflict') {
      const a = bundle.entries.get(i.a)?.name ?? i.a;
      const b = bundle.entries.get(i.b)?.name ?? i.b;
      return `冲突：${a} ↔ ${b}`;
    }
    const v = bundle.vendors.get(i.vendorId)?.name ?? i.vendorId;
    return `供应商集中：${v} ×${i.count}`;
  }

  return (
    <div className="flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      <header className="vh-page-header">
        <div style={{ flex: 1 }}>
          <div className="vh-page-kicker">问路 · 沿图而行</div>
          <h1>选型向导</h1>
          <div className="vh-text-caption" style={{ marginTop: 4 }}>
            问答 → 沿图推荐 → validateStack 校验
          </div>
        </div>
        <StepDots phase={phase} layerIndex={layerIndex} layerCount={layerKeys.length} />
      </header>

      <div className="overflow-y-auto" style={{ flex: 1, padding: 24 }}>
        {phase === 'answers' && (
          <AnswersStep answers={answers} onChange={setAnswers} onNext={startLayers} />
        )}

        {phase === 'layers' && currentCat && (
          <LayersStep
            categoryId={currentCat}
            categoryName={catName(currentCat)}
            step={layerIndex + 1}
            total={layerKeys.length}
            candidates={candidates}
            layers={layers}
            catName={catName}
            resolveName={(id) => bundle.entries.get(id)?.name ?? id}
            resolveOneLiner={(id) => bundle.entries.get(id)?.oneLiner ?? ''}
            onPick={pick}
            onSkip={skipLayer}
            onBack={goBack}
            onOpenEntry={onOpenEntry}
          />
        )}

        {phase === 'summary' && (
          <SummaryStep
            answers={answers}
            layers={layers}
            issues={issues.map(issueText)}
            stackName={stackName}
            onName={setStackName}
            catName={catName}
            resolveName={(id) => bundle.entries.get(id)?.name ?? id}
            onOpenEntry={onOpenEntry}
            onBack={goBack}
            onSave={save}
            flash={flash}
            canSave={Object.keys(layers).length > 0}
          />
        )}
      </div>
    </div>
  );
}

function targetLabel(a: WizardAnswers): string {
  const market = a.market === 'domestic' ? '国内' : a.market === 'overseas' ? '出海' : '国内外通用';
  const pay = a.monetize ? '可收费' : '不收费';
  return `${market} · ${pay} · 预算 ${a.budget}`;
}

function StepDots({
  phase,
  layerIndex,
  layerCount,
}: {
  phase: Phase;
  layerIndex: number;
  layerCount: number;
}) {
  const label =
    phase === 'answers'
      ? '偏好'
      : phase === 'layers'
        ? `层 ${Math.min(layerIndex + 1, Math.max(layerCount, 1))}/${Math.max(layerCount, 1)}`
        : '汇总';
  return (
    <span className="vh-mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>
      {label}
    </span>
  );
}

function AnswersStep({
  answers,
  onChange,
  onNext,
}: {
  answers: WizardAnswers;
  onChange: (a: WizardAnswers) => void;
  onNext: () => void;
}) {
  return (
    <div style={{ maxWidth: 560 }}>
      <p style={{ color: 'var(--ink-2)', fontSize: 14, marginTop: 0 }}>
        先回答几个偏好问题，向导会按兼容/常搭配边逐层推荐，并实时排除冲突项。
      </p>

      <Field label="目标市场">
        <ChoiceRow
          value={answers.market}
          options={[
            { value: 'overseas', label: '出海 / 海外' },
            { value: 'domestic', label: '国内' },
            { value: 'both', label: '不限' },
          ]}
          onChange={(market) => onChange({ ...answers, market })}
        />
      </Field>

      <Field label="预算">
        <ChoiceRow
          value={answers.budget}
          options={[
            { value: 'free', label: '尽量免费' },
            { value: 'low', label: '低成本' },
            { value: 'flexible', label: '灵活' },
          ]}
          onChange={(budget) => onChange({ ...answers, budget })}
        />
      </Field>

      <Field label="是否收费">
        <ChoiceRow
          value={answers.monetize ? 'yes' : 'no'}
          options={[
            { value: 'yes', label: '需要收款' },
            { value: 'no', label: '暂不收费' },
          ]}
          onChange={(v) => onChange({ ...answers, monetize: v === 'yes' })}
        />
      </Field>

      <Field label="技术偏好">
        <ChoiceRow
          value={answers.preferOpenSource ? 'oss' : 'any'}
          options={[
            { value: 'any', label: '不限' },
            { value: 'oss', label: '开源优先' },
          ]}
          onChange={(v) => onChange({ ...answers, preferOpenSource: v === 'oss' })}
        />
      </Field>

      <button
        type="button"
        className="vh-btn flex items-center gap-1.5"
        style={{
          marginTop: 20,
          background: 'var(--pigment-primary)',
          color: 'var(--paper-0)',
          borderColor: 'var(--pigment-primary)',
        }}
        onClick={onNext}
      >
        开始逐层选型 <Icon name="ArrowRight" size={14} />
      </button>
    </div>
  );
}

function LayersStep({
  categoryId,
  categoryName,
  step,
  total,
  candidates,
  layers,
  catName,
  resolveName,
  resolveOneLiner,
  onPick,
  onSkip,
  onBack,
  onOpenEntry,
}: {
  categoryId: Id;
  categoryName: string;
  step: number;
  total: number;
  candidates: { id: Id; score: number; reasons: string[] }[];
  layers: Record<string, Id>;
  catName: (id: Id) => string;
  resolveName: (id: Id) => string;
  resolveOneLiner: (id: Id) => string;
  onPick: (id: Id) => void;
  onSkip: () => void;
  onBack: () => void;
  onOpenEntry: (id: Id) => void;
}) {
  return (
    <div>
      <div className="flex items-center gap-2" style={{ marginBottom: 16 }}>
        <button type="button" className="vh-btn" onClick={onBack}>
          返回
        </button>
        <div style={{ flex: 1 }}>
          <div className="vh-display" style={{ fontSize: 18 }}>
            {step}. 选择{categoryName}
          </div>
          <div className="vh-mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>
            {categoryId}
          </div>
        </div>
        <button type="button" className="vh-btn" onClick={onSkip}>
          跳过此层
        </button>
      </div>

      {Object.keys(layers).length > 0 && (
        <div
          className="flex flex-wrap gap-2"
          style={{ marginBottom: 16, fontSize: 12, color: 'var(--ink-2)' }}
        >
          {Object.entries(layers).map(([cat, id]) => (
            <span key={cat} className="vh-tag">
              {catName(cat)} · {resolveName(id)}
            </span>
          ))}
        </div>
      )}

      {candidates.length === 0 ? (
        <div style={{ color: 'var(--ink-3)', fontSize: 14 }}>
          当前偏好下没有可选条目，可跳过或返回调整偏好。
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {candidates.map((c, i) => (
            <div
              key={c.id}
              className="vh-card flex items-start gap-3 p-3"
              style={{ width: '100%' }}
            >
              <span
                className="vh-mono"
                style={{
                  width: 28,
                  color: i === 0 ? 'var(--pigment-primary)' : 'var(--ink-3)',
                  fontSize: 13,
                  paddingTop: 2,
                }}
              >
                #{i + 1}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <button
                  type="button"
                  className="vh-link"
                  style={{
                    border: 'none',
                    background: 'transparent',
                    cursor: 'pointer',
                    padding: 0,
                    fontSize: 15,
                    fontWeight: 500,
                    color: 'var(--ink-1)',
                  }}
                  onClick={() => onOpenEntry(c.id)}
                >
                  {resolveName(c.id)}
                </button>
                <div style={{ fontSize: 13, color: 'var(--ink-2)', marginTop: 2 }}>
                  {resolveOneLiner(c.id)}
                </div>
                {c.reasons.length > 0 && (
                  <div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 6 }}>
                    {c.reasons.slice(0, 3).join(' · ')}
                    {c.score > 0 && (
                      <span className="vh-mono" style={{ marginLeft: 8 }}>
                        score {c.score.toFixed(2)}
                      </span>
                    )}
                  </div>
                )}
              </div>
              <button type="button" className="vh-btn" onClick={() => onPick(c.id)}>
                选用
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SummaryStep({
  answers,
  layers,
  issues,
  stackName,
  onName,
  catName,
  resolveName,
  onOpenEntry,
  onBack,
  onSave,
  flash,
  canSave,
}: {
  answers: WizardAnswers;
  layers: Record<string, Id>;
  issues: string[];
  stackName: string;
  onName: (n: string) => void;
  catName: (id: Id) => string;
  resolveName: (id: Id) => string;
  onOpenEntry: (id: Id) => void;
  onBack: () => void;
  onSave: () => void;
  flash: string | null;
  canSave: boolean;
}) {
  return (
    <div style={{ maxWidth: 640 }}>
      <button type="button" className="vh-btn" onClick={onBack} style={{ marginBottom: 16 }}>
        返回调整
      </button>
      <h2 className="vh-display" style={{ fontSize: 20, margin: '0 0 8px' }}>
        方案汇总
      </h2>
      <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 16 }}>
        {targetLabel(answers)}
      </div>

      <label
        htmlFor="wizard-stack-name"
        style={{ display: 'block', fontSize: 13, color: 'var(--ink-2)', marginBottom: 6 }}
      >
        方案名称
      </label>
      <input
        id="wizard-stack-name"
        className="vh-input"
        value={stackName}
        onChange={(e) => onName(e.target.value)}
        style={{ width: '100%', maxWidth: 360, marginBottom: 20 }}
      />

      <div className="flex flex-col gap-2" style={{ marginBottom: 20 }}>
        {Object.entries(layers).map(([cat, id]) => (
          <div
            key={cat}
            className="flex items-center gap-2"
            style={{ fontSize: 14, color: 'var(--ink-1)' }}
          >
            <span style={{ width: 140, color: 'var(--ink-2)', flexShrink: 0 }}>{catName(cat)}</span>
            <button
              type="button"
              className="vh-link"
              style={{
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                padding: 0,
              }}
              onClick={() => onOpenEntry(id)}
            >
              {resolveName(id)}
            </button>
          </div>
        ))}
        {Object.keys(layers).length === 0 && (
          <div style={{ color: 'var(--ink-3)' }}>尚未选择任何层。</div>
        )}
      </div>

      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 8 }}>校验结果</div>
        {issues.length === 0 ? (
          <div className="flex items-center gap-2" style={{ color: 'var(--pigment-success)' }}>
            <Icon name="CheckCircle" size={16} weight="fill" />
            通过 validateStack（无冲突 / 无供应商过度集中）
          </div>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--pigment-warning)', fontSize: 13 }}>
            {issues.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          className="vh-btn flex items-center gap-1.5"
          disabled={!canSave}
          style={{
            background: canSave ? 'var(--pigment-primary)' : undefined,
            color: canSave ? 'var(--paper-0)' : undefined,
            borderColor: canSave ? 'var(--pigment-primary)' : undefined,
            opacity: canSave ? 1 : 0.5,
          }}
          onClick={onSave}
        >
          <Icon name="DownloadSimple" size={14} /> 保存为我的技术栈
        </button>
        {flash && <span style={{ fontSize: 13, color: 'var(--pigment-success)' }}>{flash}</span>}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 8 }}>{label}</div>
      {children}
    </div>
  );
}

function ChoiceRow<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => {
        const on = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            className="vh-btn"
            onClick={() => onChange(o.value)}
            style={{
              borderColor: on ? 'var(--pigment-primary)' : undefined,
              color: on ? 'var(--pigment-primary)' : undefined,
            }}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
