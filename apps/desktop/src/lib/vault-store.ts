import type { VaultBlob } from '@vh/core';

const KEY = 'vh-vault';

export function loadVaultBlob(): VaultBlob | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as VaultBlob;
    if (parsed.version !== 1 || !parsed.salt || !parsed.wrappedDek) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveVaultBlob(blob: VaultBlob): void {
  localStorage.setItem(KEY, JSON.stringify(blob));
}

export function clearVaultBlob(): void {
  localStorage.removeItem(KEY);
}

export function vaultExists(): boolean {
  return loadVaultBlob() != null;
}
