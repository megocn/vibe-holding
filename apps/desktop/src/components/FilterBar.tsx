import type { Maturity, PricingModel, Region } from '@vh/core';
import { type ReactNode, useCallback, useState } from 'react';
import { type Filters, MATURITY_LABELS, PRICING_LABELS, REGION_LABELS } from '../lib/filters.ts';
import { Icon } from './Icon.tsx';

interface FilterBarProps {
  filters: Filters;
  onChange: (next: Filters) => void;
  favoritesOnly: boolean;
  onFavoritesOnly: (v: boolean) => void;
  favoriteCount: number;
}

const REGIONS = Object.keys(REGION_LABELS) as Region[];
const PRICINGS = Object.keys(PRICING_LABELS) as PricingModel[];
const MATURITIES = Object.keys(MATURITY_LABELS) as Maturity[];

const EXPANDED_KEY = 'vh-filters-expanded';

function loadExpanded(): boolean {
  try {
    const raw = localStorage.getItem(EXPANDED_KEY);
    // 默认折叠，把垂直空间留给条目列表
    if (raw === null) return false;
    return raw === '1';
  } catch {
    return false;
  }
}

function saveExpanded(expanded: boolean) {
  try {
    localStorage.setItem(EXPANDED_KEY, expanded ? '1' : '0');
  } catch {
    /* ignore */
  }
}

export function FilterBar({
  filters,
  onChange,
  favoritesOnly,
  onFavoritesOnly,
  favoriteCount,
}: FilterBarProps) {
  const [expanded, setExpanded] = useState(loadExpanded);

  const active =
    filters.region !== undefined ||
    filters.pricing !== undefined ||
    filters.maturity !== undefined ||
    filters.chinaAccessible !== undefined ||
    favoritesOnly;

  const activeLabels: string[] = [];
  if (favoritesOnly) activeLabels.push(`收藏 ${favoriteCount}`);
  if (filters.region) activeLabels.push(REGION_LABELS[filters.region]);
  if (filters.chinaAccessible) activeLabels.push('国内可访问');
  if (filters.pricing) activeLabels.push(PRICING_LABELS[filters.pricing]);
  if (filters.maturity) activeLabels.push(MATURITY_LABELS[filters.maturity]);

  function toggleExpanded() {
    setExpanded((prev) => {
      const next = !prev;
      saveExpanded(next);
      return next;
    });
  }

  function toggle<K extends keyof Filters>(key: K, value: Filters[K]) {
    onChange({ ...filters, [key]: filters[key] === value ? undefined : value });
  }

  const clearAll = useCallback(() => {
    onChange({});
    onFavoritesOnly(false);
  }, [onChange, onFavoritesOnly]);

  return (
    <div className="vh-kb-filters" data-expanded={expanded ? 'true' : 'false'}>
      <div className="vh-kb-filters-bar">
        <button
          type="button"
          className="vh-kb-filters-toggle"
          aria-expanded={expanded}
          onClick={toggleExpanded}
        >
          <Icon name="FunnelSimple" size={14} />
          <span>筛选</span>
          {activeLabels.length > 0 && (
            <span className="vh-kb-filters-badge">{activeLabels.length}</span>
          )}
          <Icon name={expanded ? 'CaretUp' : 'CaretDown'} size={12} />
        </button>

        {!expanded && activeLabels.length > 0 && (
          <div className="vh-kb-filters-summary" title={activeLabels.join(' · ')}>
            {activeLabels.map((label) => (
              <span key={label} className="vh-kb-filters-summary-chip">
                {label}
              </span>
            ))}
          </div>
        )}

        {active && (
          <button
            type="button"
            onClick={clearAll}
            className="vh-kb-filter-clear flex items-center gap-1"
          >
            <Icon name="X" size={12} /> 清除
          </button>
        )}
      </div>

      {expanded && (
        <div className="vh-kb-filters-body">
          <Facet label="范围">
            <Chip
              label={`收藏 ${favoriteCount}`}
              on={favoritesOnly}
              seal
              icon="Star"
              onClick={() => onFavoritesOnly(!favoritesOnly)}
            />
            {REGIONS.map((r) => (
              <Chip
                key={r}
                label={REGION_LABELS[r]}
                on={filters.region === r}
                seal={r === 'domestic'}
                onClick={() => toggle('region', r)}
              />
            ))}
            <Chip
              label="国内可访问"
              on={filters.chinaAccessible === true}
              onClick={() => toggle('chinaAccessible', true)}
            />
          </Facet>
          <Facet label="定价">
            {PRICINGS.map((p) => (
              <Chip
                key={p}
                label={PRICING_LABELS[p]}
                on={filters.pricing === p}
                onClick={() => toggle('pricing', p)}
              />
            ))}
          </Facet>
          <Facet label="成熟度" segment>
            {MATURITIES.map((m) => (
              <Chip
                key={m}
                label={MATURITY_LABELS[m]}
                on={filters.maturity === m}
                onClick={() => toggle('maturity', m)}
              />
            ))}
          </Facet>
        </div>
      )}
    </div>
  );
}

function Facet({
  label,
  children,
  segment,
}: {
  label: string;
  children: ReactNode;
  segment?: boolean;
}) {
  return (
    <div className="vh-kb-facet">
      <span className="vh-kb-facet-label">{label}</span>
      <div
        className={
          segment ? 'vh-kb-facet-segment' : 'vh-kb-facet-chips flex flex-wrap items-center'
        }
        role={segment ? 'group' : undefined}
        aria-label={segment ? label : undefined}
      >
        {children}
      </div>
    </div>
  );
}

function Chip({
  label,
  on,
  onClick,
  seal,
  icon,
}: {
  label: string;
  on: boolean;
  onClick: () => void;
  seal?: boolean;
  icon?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`vh-kb-facet-chip${seal ? ' vh-kb-facet-chip-seal' : ''}`}
      data-on={on ? 'true' : 'false'}
      aria-pressed={on}
    >
      {icon && <Icon name={icon} size={11} weight={on ? 'fill' : 'regular'} />}
      <span>{label}</span>
    </button>
  );
}
