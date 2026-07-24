import type { Maturity, PricingModel, Region } from '@vh/core';
import type { ReactNode } from 'react';
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

export function FilterBar({
  filters,
  onChange,
  favoritesOnly,
  onFavoritesOnly,
  favoriteCount,
}: FilterBarProps) {
  const active =
    filters.region !== undefined ||
    filters.pricing !== undefined ||
    filters.maturity !== undefined ||
    filters.chinaAccessible !== undefined ||
    favoritesOnly;

  function toggle<K extends keyof Filters>(key: K, value: Filters[K]) {
    onChange({ ...filters, [key]: filters[key] === value ? undefined : value });
  }

  return (
    <div className="vh-kb-filters">
      <Facet label="范围">
        <Chip
          label={`收藏 ${favoriteCount}`}
          on={favoritesOnly}
          seal
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
      <Facet label="成熟度">
        {MATURITIES.map((m) => (
          <Chip
            key={m}
            label={MATURITY_LABELS[m]}
            on={filters.maturity === m}
            onClick={() => toggle('maturity', m)}
          />
        ))}
        {active && (
          <button
            type="button"
            onClick={() => {
              onChange({});
              onFavoritesOnly(false);
            }}
            className="vh-kb-filter-clear flex items-center gap-1"
          >
            <Icon name="X" size={12} /> 清除
          </button>
        )}
      </Facet>
    </div>
  );
}

function Facet({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="vh-kb-facet">
      <span className="vh-kb-facet-label">{label}</span>
      <div className="vh-kb-facet-chips flex flex-wrap items-center gap-1.5">{children}</div>
    </div>
  );
}

function Chip({
  label,
  on,
  onClick,
  seal,
}: {
  label: string;
  on: boolean;
  onClick: () => void;
  seal?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`vh-chip${seal ? ' vh-chip-seal' : ''}`}
      data-on={on ? 'true' : 'false'}
    >
      {label}
    </button>
  );
}
