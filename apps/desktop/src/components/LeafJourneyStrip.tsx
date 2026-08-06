import type { Category, Entry, Id } from '@vh/core';
import { leavesOfSection } from '@vh/core';
import { CATEGORY_LAYERS, layerOfCategory } from '@vh/ui';
import { useEffect } from 'react';
import type { KbNav } from './CategoryBrowser.tsx';
import { Icon } from './Icon.tsx';

interface LeafJourneyStripProps {
  leaf: Category;
  categories: Category[];
  /** 当前叶条目（已排序）；密铺可点，与中栏互补非复刻 */
  entries: Entry[];
  onNav?: (nav: KbNav) => void;
  onSelectEntry?: (id: Id) => void;
  /** 与中栏列表双向 hover */
  hoverId?: Id | null;
  onHoverEntry?: (id: Id | null) => void;
}

type Dim = 'ghost' | 'far' | 'near' | 'focus';

/**
 * 上线路程焦点：图廓 → 同卷叶 → 本叶基建网格。
 * 条目层是「图上落点/快跳」，中栏仍是完整扫阅（榜、oneLiner、筛选）。
 */
export function LeafJourneyStrip({
  leaf,
  categories,
  entries,
  onNav,
  onSelectEntry,
  hoverId = null,
  onHoverEntry,
}: LeafJourneyStripProps) {
  const sectionId = leaf.parent;
  if (!sectionId) return null;

  const sections = categories
    .filter((c) => c.kind === 'section')
    .sort((a, b) => a.order - b.order);

  const idx = sections.findIndex((s) => s.id === sectionId);
  if (idx < 0) return null;

  const layer = layerOfCategory(leaf.id, categories);
  const siblingLeaves = leavesOfSection(categories, sectionId);
  const focus = sections[idx]!;

  const windowStart = Math.max(0, idx - 2);
  const windowEnd = Math.min(sections.length - 1, idx + 2);
  const showLeftEllipsis = windowStart > 0;
  const showRightEllipsis = windowEnd < sections.length - 1;
  const visible = sections.slice(windowStart, windowEnd + 1);

  const dimFor = (i: number): Dim => {
    const d = Math.abs(i - idx);
    if (d === 0) return 'focus';
    if (d === 1) return 'near';
    if (d === 2) return 'far';
    return 'ghost';
  };

  const go = (id: Id) => {
    onNav?.({ kind: 'category', categoryId: id });
  };

  const goSection = (secId: string) => {
    const leaves = leavesOfSection(categories, secId);
    const target = leaves.find((l) => l.usageMd)?.id ?? leaves[0]?.id ?? secId;
    go(target as Id);
  };

  // 从中栏 hover 过来时滚到对应落点
  useEffect(() => {
    if (!hoverId) return;
    const el = document.querySelector<HTMLElement>(
      `.vh-journey-dots [data-entry-id="${CSS.escape(hoverId)}"]`,
    );
    el?.scrollIntoView({ block: 'nearest', behavior: 'smooth', inline: 'nearest' });
  }, [hoverId]);

  return (
    <div className="vh-journey" aria-label="你在整条上线路上的位置">
      <div className="vh-journey-meta vh-text-xs">
        <span className="vh-journey-meta-label">大致位置</span>
        <span className="vh-journey-meta-sep" aria-hidden>
          ·
        </span>
        <span>
          {layer?.label ?? '大阶段'}
          {focus.code ? ` · ${focus.code}` : ''}
          {' → '}
          {leaf.name}
          {entries.length > 0 ? ` · ${entries.length} 个产品` : ''}
        </span>
      </div>

      <div className="vh-journey-level">
        <span className="vh-journey-level-tag">前后阶段</span>
        <div className="vh-journey-track" role="list">
          {showLeftEllipsis && (
            <span className="vh-journey-ellipsis" data-dim="ghost" aria-hidden>
              ···
            </span>
          )}
          {visible.map((sec, vi) => {
            const abs = windowStart + vi;
            const dim = dimFor(abs);
            const isFocus = abs === idx;
            return (
              <div key={sec.id} className="vh-journey-step" data-dim={dim} role="listitem">
                {vi > 0 && <span className="vh-journey-link" data-dim={dim} aria-hidden />}
                <button
                  type="button"
                  className="vh-journey-node"
                  data-dim={dim}
                  data-focus={isFocus ? 'true' : undefined}
                  disabled={!onNav || isFocus}
                  onClick={() => {
                    if (!isFocus) goSection(sec.id);
                  }}
                  title={isFocus ? sec.name : `看看：${sec.name}`}
                >
                  {sec.code && <span className="vh-journey-code">{sec.code}</span>}
                  <span className="vh-journey-name">{shortName(sec.name, dim)}</span>
                </button>
              </div>
            );
          })}
          {showRightEllipsis && (
            <span className="vh-journey-ellipsis" data-dim="ghost" aria-hidden>
              ···
            </span>
          )}
        </div>
      </div>

      {siblingLeaves.length > 0 && (
        <div className="vh-journey-level">
          <span className="vh-journey-level-tag">同一大类下的小类</span>
          <div className="vh-journey-leaves" role="list">
            {siblingLeaves.map((sib) => {
              const on = sib.id === leaf.id;
              return (
                <button
                  key={sib.id}
                  type="button"
                  role="listitem"
                  className="vh-journey-leaf"
                  data-on={on ? 'true' : undefined}
                  disabled={on || !onNav}
                  onClick={() => go(sib.id as Id)}
                  title={on ? sib.name : `切到：${sib.name}`}
                >
                  <span className="vh-journey-leaf-dot" aria-hidden />
                  <span className="vh-journey-leaf-label">{sib.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      <div className="vh-journey-level vh-journey-level-entries">
        <div className="vh-journey-entries-head">
          <span className="vh-journey-level-tag" data-accent="true">
            这类里有哪些产品
          </span>
          <span className="vh-journey-entries-cue">
            <Icon name="CursorClick" size={13} weight="duotone" />
            点名字打开详情
          </span>
        </div>

        {entries.length === 0 ? (
          <p className="vh-journey-entries-empty">这一类暂时还没有收录产品</p>
        ) : (
          <div className="vh-journey-dots" role="list">
            {entries.map((e) => (
              <button
                key={e.id}
                type="button"
                role="listitem"
                className="vh-journey-dot"
                data-hover-sync={e.id === hoverId ? 'true' : undefined}
                data-entry-id={e.id}
                onClick={() => onSelectEntry?.(e.id)}
                onMouseEnter={() => onHoverEntry?.(e.id)}
                onMouseLeave={() => onHoverEntry?.(null)}
                title={e.oneLiner ? `${e.name} — ${e.oneLiner}` : e.name}
              >
                <span className="vh-journey-dot-seal" aria-hidden />
                <span className="vh-journey-dot-name">{e.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="vh-journey-spine" aria-hidden>
        {CATEGORY_LAYERS.map((L) => {
          const active = L.id === layer?.id;
          return (
            <span
              key={L.id}
              className="vh-journey-spine-seg"
              data-active={active ? 'true' : undefined}
              title={L.label}
            />
          );
        })}
      </div>
    </div>
  );
}

function shortName(name: string, dim: Dim): string {
  if (dim === 'focus') return name;
  if (dim === 'near') return name.length > 10 ? `${name.slice(0, 9)}…` : name;
  const head = name.split(/[／/·]/)[0] ?? name;
  return head.length > 6 ? `${head.slice(0, 5)}…` : head;
}
