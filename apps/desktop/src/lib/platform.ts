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
