import { type Theme, applyTheme } from './prefs.ts';

export type ThemeOrigin = { x: number; y: number };

function prefersReducedMotion(): boolean {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function supportsViewTransition(): boolean {
  return typeof document !== 'undefined' && 'startViewTransition' in document;
}

/** 顶栏主题按钮大致位置（无指针事件时用；微动效不再依赖落点） */
export function defaultThemeOrigin(): ThemeOrigin {
  return { x: Math.max(48, window.innerWidth - 72), y: 28 };
}

export function originFromEvent(e: { clientX: number; clientY: number }): ThemeOrigin {
  return { x: e.clientX, y: e.clientY };
}

/**
 * 明暗切换微动效：短时交叉淡入（~180ms），无扩散/水纹叠层。
 * 尊重 prefers-reduced-motion；不支持 VT 时瞬时切换。
 */
export function applyThemeWithTransition(theme: Theme, _origin?: ThemeOrigin | null): void {
  const current = document.documentElement.dataset.theme;
  if (current === theme) {
    applyTheme(theme);
    return;
  }

  if (prefersReducedMotion() || !supportsViewTransition()) {
    applyTheme(theme);
    return;
  }

  const root = document.documentElement;
  root.classList.add('vh-theme-micro');

  const vt = document.startViewTransition(() => {
    applyTheme(theme);
  });

  void vt.finished.finally(() => {
    root.classList.remove('vh-theme-micro');
  });
}
