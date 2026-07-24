const KEY = 'vh-layout';

export interface LayoutPrefs {
  sidebarWidth: number;
  listWidth: number;
  /** 宽屏下将分类树钉为常驻栏；亦可随时切换浮层抽屉 */
  sidebarPinned: boolean;
  listCollapsed: boolean;
}

export const LAYOUT_DEFAULTS: LayoutPrefs = {
  sidebarWidth: 300,
  listWidth: 340,
  sidebarPinned: true,
  listCollapsed: false,
};

export const SIDEBAR_MIN = 260;
export const SIDEBAR_MAX = 420;
export const LIST_MIN = 240;
export const LIST_MAX = 480;

export function loadLayout(): LayoutPrefs {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...LAYOUT_DEFAULTS };
    const parsed = JSON.parse(raw) as Partial<LayoutPrefs> & {
      /** 旧字段：折叠=未展开；迁移为未钉住 */
      sidebarCollapsed?: boolean;
    };
    return {
      sidebarWidth: clamp(
        parsed.sidebarWidth ?? LAYOUT_DEFAULTS.sidebarWidth,
        SIDEBAR_MIN,
        SIDEBAR_MAX,
      ),
      listWidth: clamp(parsed.listWidth ?? LAYOUT_DEFAULTS.listWidth, LIST_MIN, LIST_MAX),
      sidebarPinned:
        parsed.sidebarPinned !== undefined
          ? Boolean(parsed.sidebarPinned)
          : parsed.sidebarCollapsed === false
            ? false
            : LAYOUT_DEFAULTS.sidebarPinned,
      listCollapsed: Boolean(parsed.listCollapsed),
    };
  } catch {
    return { ...LAYOUT_DEFAULTS };
  }
}

export function saveLayout(prefs: LayoutPrefs): void {
  localStorage.setItem(KEY, JSON.stringify(prefs));
}

function clamp(n: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, n));
}
