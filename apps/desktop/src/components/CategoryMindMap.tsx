import type { Id } from '@vh/core';
import { CATEGORY_LAYERS } from '@vh/ui';
import { useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import type { KbNav } from './CategoryBrowser.tsx';

interface CategoryMindMapProps {
  nav: KbNav;
  onBrowseLayer: (layerId: string) => void;
  onNav: (nav: KbNav) => void;
}

type SecNode = {
  id: Id;
  code?: string;
  name: string;
  count: number;
  x: number;
  y: number;
  layerId: string;
};

type LayerNode = {
  id: string;
  label: string;
  subtitle: string;
  count: number;
  x: number;
  y: number;
  sections: SecNode[];
};

/**
 * 单向图廓导图（左→右）：全图 → 卷 → 分类，默认全部展开。
 */
export function CategoryMindMap({ nav, onBrowseLayer, onNav }: CategoryMindMapProps) {
  const { categories, categoryCount } = useContent();
  const catById = useMemo(() => new Map(categories.map((c) => [c.id, c])), [categories]);

  const layout = useMemo(() => {
    const HUB_X = 52;
    const LAYER_X = 168;
    const SEC_X = 340;
    const ROW = 34;
    const LAYER_GAP = 14;
    const PAD_Y = 28;

    let y = PAD_Y;
    const layers: LayerNode[] = [];

    for (const layer of CATEGORY_LAYERS) {
      const sections = layer.categories
        .map((sid) => {
          const section = catById.get(sid);
          if (!section || section.kind !== 'section') return null;
          return {
            id: sid as Id,
            code: section.code,
            name: section.name,
            count: categoryCount[sid] ?? 0,
          };
        })
        .filter((x): x is NonNullable<typeof x> => x != null);

      const blockH = Math.max(ROW, sections.length * ROW);
      const layerY = y + blockH / 2;
      const secNodes: SecNode[] = sections.map((s, j) => ({
        ...s,
        x: SEC_X,
        y: y + j * ROW + ROW / 2,
        layerId: layer.id,
      }));

      layers.push({
        id: layer.id,
        label: layer.label,
        subtitle: layer.subtitle,
        count: layer.categories.reduce((sum, id) => sum + (categoryCount[id] ?? 0), 0),
        x: LAYER_X,
        y: layerY,
        sections: secNodes,
      });

      y += blockH + LAYER_GAP;
    }

    const totalH = Math.max(y + PAD_Y - LAYER_GAP, 360);
    const hubY = totalH / 2;
    const W = 500;

    return { layers, hubY, W, H: totalH, HUB_X, LAYER_X, SEC_X };
  }, [catById, categoryCount]);

  function elbow(
    x1: number,
    y1: number,
    x2: number,
    y2: number,
  ): string {
    const mx = (x1 + x2) / 2;
    return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
  }

  const { layers, hubY, W, H, HUB_X, LAYER_X } = layout;
  const allActive = nav.kind === 'all';

  return (
    <div className="vh-kb-mind">
      <div className="vh-kb-mind-hint vh-text-caption">
        全图 → 卷 → 分类 · 默认展开 · 点击筛选
      </div>
      <div className="vh-kb-mind-scroll">
        <svg
          className="vh-kb-mind-svg"
          viewBox={`0 0 ${W} ${H}`}
          width="100%"
          role="img"
          aria-label="图廓单向导图"
        >
          {/* 全图 → 卷 */}
          {layers.map((L) => (
            <path
              key={`e-hub-${L.id}`}
              d={elbow(HUB_X + 28, hubY, LAYER_X - 36, L.y)}
              className="vh-kb-mind-edge"
              data-active={
                (nav.kind === 'layer' && nav.layerId === L.id) ||
                (nav.kind === 'family' && L.id === 'intelligence') ||
                L.sections.some(
                  (s) =>
                    nav.kind === 'category' &&
                    (nav.categoryId === s.id ||
                      catById.get(nav.categoryId)?.parent === s.id),
                )
                  ? 'true'
                  : 'false'
              }
              fill="none"
            />
          ))}
          {/* 卷 → 分类 */}
          {layers.flatMap((L) =>
            L.sections.map((s) => (
              <path
                key={`e-sec-${s.id}`}
                d={elbow(LAYER_X + 36, L.y, s.x - 48, s.y)}
                className="vh-kb-mind-edge vh-kb-mind-edge-sec"
                data-active={
                  (nav.kind === 'category' &&
                    (nav.categoryId === s.id ||
                      catById.get(nav.categoryId)?.parent === s.id)) ||
                  (nav.kind === 'family' && s.id === 'llm')
                    ? 'true'
                    : 'false'
                }
                fill="none"
              />
            )),
          )}

          {/* 全图 */}
          <g
            className="vh-kb-mind-node"
            data-active={allActive ? 'true' : 'false'}
            data-kind="hub"
            transform={`translate(${HUB_X}, ${hubY})`}
            onClick={() => onNav({ kind: 'all' })}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onNav({ kind: 'all' });
              }
            }}
          >
            <rect
              x={-28}
              y={-18}
              width={56}
              height={36}
              rx={10}
              className="vh-kb-mind-pill"
            />
            <text textAnchor="middle" dy="0.35em" className="vh-kb-mind-label">
              全图
            </text>
          </g>

          {/* 卷 */}
          {layers.map((L) => {
            const active =
              (nav.kind === 'layer' && nav.layerId === L.id) ||
              (nav.kind === 'family' && L.id === 'intelligence') ||
              L.sections.some(
                (s) =>
                  nav.kind === 'category' &&
                  (nav.categoryId === s.id ||
                    catById.get(nav.categoryId)?.parent === s.id),
              );
            return (
              <g
                key={L.id}
                className="vh-kb-mind-node"
                data-active={active ? 'true' : 'false'}
                data-kind="layer"
                transform={`translate(${L.x}, ${L.y})`}
                onClick={() => {
                  onBrowseLayer(L.id);
                  onNav({ kind: 'layer', layerId: L.id });
                }}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onBrowseLayer(L.id);
                    onNav({ kind: 'layer', layerId: L.id });
                  }
                }}
              >
                <title>
                  {L.label} · {L.subtitle}
                </title>
                <rect
                  x={-40}
                  y={-16}
                  width={80}
                  height={32}
                  rx={8}
                  className="vh-kb-mind-pill"
                />
                <text textAnchor="middle" dy="0.35em" className="vh-kb-mind-label">
                  {L.label}
                </text>
              </g>
            );
          })}

          {/* 分类 */}
          {layers.flatMap((L) =>
            L.sections.map((s) => {
              const active =
                (nav.kind === 'category' &&
                  (nav.categoryId === s.id ||
                    catById.get(nav.categoryId)?.parent === s.id)) ||
                (nav.kind === 'family' && s.id === 'llm');
              const label = s.code ? `${s.code} ${s.name}` : s.name;
              const short =
                label.length > 10 ? `${label.slice(0, 9)}…` : label;
              return (
                <g
                  key={s.id}
                  className="vh-kb-mind-node"
                  data-active={active ? 'true' : 'false'}
                  data-kind="section"
                  transform={`translate(${s.x}, ${s.y})`}
                  onClick={() => onNav({ kind: 'category', categoryId: s.id })}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onNav({ kind: 'category', categoryId: s.id });
                    }
                  }}
                >
                  <title>
                    {s.code ? `${s.code} · ${s.name}` : s.name}（{s.count}）
                  </title>
                  <rect
                    x={-52}
                    y={-13}
                    width={104}
                    height={26}
                    rx={7}
                    className="vh-kb-mind-pill"
                  />
                  <text textAnchor="middle" dy="0.35em" className="vh-kb-mind-label-sm">
                    {short}
                  </text>
                </g>
              );
            }),
          )}
        </svg>
      </div>
    </div>
  );
}
