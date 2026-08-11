/** 运行环境探测与桌面窗口控制封装（浏览器 dev 下均为 no-op）。 */

export const isTauri =
  typeof window !== 'undefined' && ('__TAURI_INTERNALS__' in window || '__TAURI__' in window);

async function currentWindow() {
  const { getCurrentWindow } = await import('@tauri-apps/api/window');
  return getCurrentWindow();
}

export async function winMinimize(): Promise<void> {
  if (!isTauri) return;
  await (await currentWindow()).minimize();
}

export async function winToggleMaximize(): Promise<void> {
  if (!isTauri) return;
  await (await currentWindow()).toggleMaximize();
}

export async function winClose(): Promise<void> {
  if (!isTauri) return;
  await (await currentWindow()).close();
}

/** 只读 IPC：优先走 Rust `content_load`，非 Tauri 环境返回 null 由调用方回退。 */
export async function ipcContentLoad(): Promise<unknown | null> {
  if (!isTauri) return null;
  const { invoke } = await import('@tauri-apps/api/core');
  return invoke('content_load');
}

function isHttpUrl(href: string): boolean {
  return /^https?:\/\//i.test(href);
}

/** 是否指向应用自身以外的 http(s) 地址（同源 / 路由不外开）。 */
export function isExternalHttpUrl(href: string): boolean {
  if (!isHttpUrl(href)) return false;
  try {
    const target = new URL(href, window.location.href);
    return target.origin !== window.location.origin;
  } catch {
    return false;
  }
}

/**
 * 在系统默认浏览器中打开 URL。
 * Tauri：plugin-opener；浏览器 dev：新标签页。
 * 用于绕开 WebView 内访问 Cloudflare 站点时被 Bot 防护硬拦。
 */
export async function openExternalUrl(url: string): Promise<void> {
  if (!isHttpUrl(url)) return;
  if (isTauri) {
    const { openUrl } = await import('@tauri-apps/plugin-opener');
    await openUrl(url);
    return;
  }
  window.open(url, '_blank', 'noopener,noreferrer');
}

/**
 * 全局拦截外链：桌面端一律走系统浏览器。
 * 覆盖 `target=_blank` 与无 target 的 `<a href="https://…">`，并阻止 WebView 原地导航。
 */
export function installExternalLinkHandler(): void {
  if (typeof document === 'undefined') return;

  document.addEventListener(
    'click',
    (event) => {
      if (event.defaultPrevented) return;
      if (event.button !== 0) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

      const el = event.target;
      if (!(el instanceof Element)) return;
      const anchor = el.closest('a[href]');
      if (!(anchor instanceof HTMLAnchorElement)) return;
      if (anchor.hasAttribute('download')) return;

      const href = anchor.href;
      if (!isExternalHttpUrl(href)) return;

      event.preventDefault();
      void openExternalUrl(href).catch(() => {
        // opener 失败时再放行原生跳转（至少可在日志/无 opener 环境兜底）
        window.open(href, '_blank', 'noopener,noreferrer');
      });
    },
    true,
  );
}
