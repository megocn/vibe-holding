import type { Id } from '@vh/core';
import { sectionIdOf } from '@vh/core';
import { CATEGORY_LAYERS, layerOfCategory } from '@vh/ui';
import { useMemo } from 'react';
import { useContent } from '../lib/content.tsx';
import type { KbNav } from './Sidebar.tsx';

export type KbCrumb = {
  key: string;
  label: string;
  nav: KbNav;
};

/** 根据当前 kbNav 生成可点面包屑：全图 › 卷 › 分类 › 族 */
export function useKbCrumbs(nav: KbNav): KbCrumb[] {
  const { categories, bundle } = useContent();

  return useMemo(() => {
    const crumbs: KbCrumb[] = [{ key: 'all', label: '全图', nav: { kind: 'all' } }];

    if (nav.kind === 'all') return crumbs;

    if (nav.kind === 'layer') {
      const layer = CATEGORY_LAYERS.find((l) => l.id === nav.layerId);
      crumbs.push({
        key: `layer:${nav.layerId}`,
        label: layer?.label ?? nav.layerId,
        nav: { kind: 'layer', layerId: nav.layerId },
      });
      return crumbs;
    }

    if (nav.kind === 'family') {
      const fam = bundle.entries.get(nav.familyId);
      const layer = CATEGORY_LAYERS.find((l) => l.id === 'intelligence');
      crumbs.push({
        key: 'layer:intelligence',
        label: layer?.label ?? '智能层',
        nav: { kind: 'layer', layerId: 'intelligence' },
      });
      crumbs.push({
        key: 'cat:llm',
        label: 'B · LLM',
        nav: { kind: 'category', categoryId: 'llm' },
      });
      crumbs.push({
        key: `fam:${nav.familyId}`,
        label: fam?.name ?? nav.familyId,
        nav: { kind: 'family', familyId: nav.familyId },
      });
      return crumbs;
    }

    // category
    const cat = categories.find((c) => c.id === nav.categoryId);
    const layer = layerOfCategory(nav.categoryId, categories);
    if (layer) {
      crumbs.push({
        key: `layer:${layer.id}`,
        label: layer.label,
        nav: { kind: 'layer', layerId: layer.id },
      });
    }

    const sectionId = sectionIdOf(categories, nav.categoryId);
    const section = categories.find((c) => c.id === sectionId);
    if (section && section.kind === 'section') {
      const sectionLabel =
        section.code != null ? `${section.code} · ${section.name}` : section.name;
      crumbs.push({
        key: `cat:${section.id}`,
        label: sectionLabel,
        nav: { kind: 'category', categoryId: section.id as Id },
      });
      if (cat?.kind === 'leaf' && cat.id !== section.id) {
        crumbs.push({
          key: `cat:${cat.id}`,
          label: cat.name,
          nav: { kind: 'category', categoryId: cat.id },
        });
      }
    } else if (cat) {
      crumbs.push({
        key: `cat:${cat.id}`,
        label: cat.code ? `${cat.code} · ${cat.name}` : cat.name,
        nav: { kind: 'category', categoryId: cat.id },
      });
    }

    return crumbs;
  }, [nav, categories, bundle.entries]);
}

interface KbBreadcrumbProps {
  nav: KbNav;
  onNav: (nav: KbNav) => void;
  countLabel?: string;
}

export function KbBreadcrumb({ nav, onNav, countLabel }: KbBreadcrumbProps) {
  const crumbs = useKbCrumbs(nav);
  const current = crumbs[crumbs.length - 1];

  return (
    <div className="vh-kb-breadcrumb">
      <nav className="vh-kb-crumbs" aria-label="当前位置">
        {crumbs.map((c, i) => {
          const last = i === crumbs.length - 1;
          return (
            <span key={c.key} className="vh-kb-crumb-item">
              {i > 0 && <span className="vh-kb-crumb-sep">›</span>}
              {last ? (
                <span className="vh-kb-crumb-current" aria-current="page">
                  {c.label}
                </span>
              ) : (
                <button
                  type="button"
                  className="vh-kb-crumb-link"
                  onClick={() => onNav(c.nav)}
                >
                  {c.label}
                </button>
              )}
            </span>
          );
        })}
      </nav>
      <div className="vh-kb-list-head-row">
        <h2 className="vh-kb-list-title">{current?.label ?? '全部条目'}</h2>
        {countLabel && (
          <span className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)' }}>
            {countLabel}
          </span>
        )}
      </div>
    </div>
  );
}
