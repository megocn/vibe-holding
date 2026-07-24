import { CATEGORY_LAYERS } from '@vh/ui';
import { Icon } from './Icon.tsx';
import { useKbCrumbs, type KbCrumb } from './KbBreadcrumb.tsx';
import type { KbNav } from './Sidebar.tsx';

interface KbScopeHeaderProps {
  nav: KbNav;
  onNav: (nav: KbNav) => void;
  countLabel?: string;
  drawerOpen: boolean;
  pinned: boolean;
  onOpenDrawer: () => void;
  onPinChange?: (pinned: boolean) => void;
}

/** 列表头：高对比「当前范围」+ 固定/抽屉模式 + 卷芯片 */
export function KbScopeHeader({
  nav,
  onNav,
  countLabel,
  drawerOpen,
  pinned,
  onOpenDrawer,
  onPinChange,
}: KbScopeHeaderProps) {
  const crumbs = useKbCrumbs(nav);
  const current = crumbs[crumbs.length - 1];
  const isAll = nav.kind === 'all';
  const scopeTitle = isAll ? '全部条目' : (current?.label ?? '当前范围');
  const parentCrumbs = crumbs.length > 1 ? crumbs.slice(0, -1) : [];
  const hint = pinned ? '侧栏已固定' : isAll ? '点此浏览图廓' : '当前范围 · 可切换';

  return (
    <div className="vh-kb-scope">
      <button
        type="button"
        className="vh-kb-scope-trigger"
        data-all={isAll ? 'true' : 'false'}
        data-open={drawerOpen ? 'true' : 'false'}
        data-pinned={pinned ? 'true' : 'false'}
        aria-expanded={drawerOpen}
        aria-haspopup="dialog"
        title={pinned ? '分类栏已固定在左侧' : '打开图廓分区 (⌘B)'}
        onClick={() => {
          if (pinned) return;
          onOpenDrawer();
        }}
      >
        <span className="vh-kb-scope-icon" aria-hidden>
          <Icon name="Compass" size={16} weight="regular" />
        </span>
        <span className="vh-kb-scope-copy">
          <span className="vh-kb-scope-eyebrow">{hint}</span>
          <span className="vh-kb-scope-title">{scopeTitle}</span>
          {countLabel ? (
            <span className="vh-mono vh-kb-scope-count">{countLabel}</span>
          ) : null}
        </span>
        {!pinned && (
          <span className="vh-kb-scope-caret" aria-hidden>
            <Icon name="CaretDown" size={16} />
          </span>
        )}
      </button>

      {onPinChange && (
        <div className="vh-kb-scope-modes" role="group" aria-label="分类栏显示模式">
          <button
            type="button"
            className="vh-kb-scope-mode"
            data-active={pinned ? 'true' : 'false'}
            onClick={() => onPinChange(true)}
            title="固定左侧分类栏（列表树）"
          >
            <Icon name="Sidebar" size={13} weight={pinned ? 'fill' : 'regular'} />
            固定侧栏
          </button>
          <button
            type="button"
            className="vh-kb-scope-mode"
            data-active={!pinned ? 'true' : 'false'}
            onClick={() => onPinChange(false)}
            title="浮层抽屉（列表树）"
          >
            <Icon name="Browsers" size={13} weight={!pinned ? 'fill' : 'regular'} />
            浮层抽屉
          </button>
        </div>
      )}

      {!isAll && (
        <div className="vh-kb-scope-filtered">
          <nav className="vh-kb-crumbs" aria-label="当前位置">
            {parentCrumbs.map((c: KbCrumb, i: number) => (
              <span key={c.key} className="vh-kb-crumb-item">
                {i > 0 && <span className="vh-kb-crumb-sep">›</span>}
                <button type="button" className="vh-kb-crumb-link" onClick={() => onNav(c.nav)}>
                  {c.label}
                </button>
              </span>
            ))}
            {parentCrumbs.length > 0 && <span className="vh-kb-crumb-sep">›</span>}
            <span className="vh-kb-crumb-current" aria-current="page">
              {scopeTitle}
            </span>
          </nav>
          <button
            type="button"
            className="vh-kb-scope-clear"
            onClick={() => onNav({ kind: 'all' })}
            title="回到全部条目"
          >
            清除范围
          </button>
        </div>
      )}

      {isAll && (
        <div className="vh-kb-scope-layers" role="group" aria-label="按卷浏览">
          <span className="vh-kb-scope-layers-hint">按卷</span>
          {CATEGORY_LAYERS.map((layer) => (
            <button
              key={layer.id}
              type="button"
              className="vh-kb-scope-chip"
              data-active="false"
              title={layer.subtitle}
              onClick={() => onNav({ kind: 'layer', layerId: layer.id })}
            >
              <Icon name={layer.icon} size={13} />
              {layer.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
