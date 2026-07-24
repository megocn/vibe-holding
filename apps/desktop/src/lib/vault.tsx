import {
  type Credential,
  type VaultBlob,
  type VaultRecord,
  collectCredentialAlerts,
  createEncryptedBackup,
  createVault,
  fromVaultRecord,
  parseEncryptedBackup,
  recordMeta,
  toVaultRecord,
  unlockVault,
} from '@vh/core';
import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { clearVaultBlob, loadVaultBlob, saveVaultBlob, vaultExists } from './vault-store.ts';

const IDLE_MS = 5 * 60 * 1000;

interface VaultContextValue {
  ready: boolean;
  hasVault: boolean;
  unlocked: boolean;
  error: string | null;
  records: VaultRecord[];
  setup: (password: string) => Promise<void>;
  unlock: (password: string) => Promise<void>;
  lock: () => void;
  addCredential: (cred: Credential) => Promise<void>;
  updateCredential: (cred: Credential) => Promise<void>;
  removeCredential: (id: string) => Promise<void>;
  setActive: (id: string) => Promise<void>;
  revealFields: (id: string) => Promise<Record<string, string>>;
  /** 解密全部凭据并打成加密备份文件 */
  exportBackup: (exportPassword: string) => Promise<string>;
  /** 解密备份并合并（跳过已有 id）；返回新增条数 */
  importBackup: (
    exportPassword: string,
    json: string,
  ) => Promise<{ added: number; skipped: number }>;
  wipeVault: () => void;
  touch: () => void;
}

const VaultContext = createContext<VaultContextValue | null>(null);

export function VaultProvider({ children }: { children: ReactNode }) {
  const [hasVault, setHasVault] = useState(false);
  const [blob, setBlob] = useState<VaultBlob | null>(null);
  const [dek, setDek] = useState<CryptoKey | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const idleTimer = useRef<number | null>(null);

  useEffect(() => {
    const b = loadVaultBlob();
    setBlob(b);
    setHasVault(b != null);
    setReady(true);
  }, []);

  const persist = useCallback((next: VaultBlob) => {
    setBlob(next);
    saveVaultBlob(next);
    setHasVault(true);
  }, []);

  const lock = useCallback(() => {
    setDek(null);
    setError(null);
    if (idleTimer.current) {
      window.clearTimeout(idleTimer.current);
      idleTimer.current = null;
    }
  }, []);

  const armIdle = useCallback(() => {
    if (idleTimer.current) window.clearTimeout(idleTimer.current);
    idleTimer.current = window.setTimeout(() => lock(), IDLE_MS);
  }, [lock]);

  const touch = useCallback(() => {
    if (dek) armIdle();
  }, [dek, armIdle]);

  const setup = useCallback(
    async (password: string) => {
      if (password.length < 8) throw new Error('主密码至少 8 位');
      const { blob: next, dek: d } = await createVault(password);
      persist(next);
      setDek(d);
      armIdle();
      setError(null);
    },
    [persist, armIdle],
  );

  const unlock = useCallback(
    async (password: string) => {
      const current = loadVaultBlob();
      if (!current) throw new Error('尚未初始化保险库');
      const d = await unlockVault(current, password);
      setBlob(current);
      setDek(d);
      armIdle();
      setError(null);
    },
    [armIdle],
  );

  const addCredential = useCallback(
    async (cred: Credential) => {
      if (!dek || !blob) throw new Error('保险库已锁定');
      const record = await toVaultRecord(dek, cred);
      let records = [...blob.records];
      if (cred.isActive) {
        records = records.map((r) => (r.entryId === cred.entryId ? { ...r, isActive: false } : r));
      }
      records.push(record);
      persist({ ...blob, records });
      armIdle();
    },
    [dek, blob, persist, armIdle],
  );

  const updateCredential = useCallback(
    async (cred: Credential) => {
      if (!dek || !blob) throw new Error('保险库已锁定');
      const record = await toVaultRecord(dek, cred);
      let records = blob.records.map((r) => (r.id === cred.id ? record : r));
      if (cred.isActive) {
        records = records.map((r) =>
          r.id !== cred.id && r.entryId === cred.entryId ? { ...r, isActive: false } : r,
        );
      }
      persist({ ...blob, records });
      armIdle();
    },
    [dek, blob, persist, armIdle],
  );

  const removeCredential = useCallback(
    async (id: string) => {
      if (!blob) throw new Error('保险库已锁定');
      persist({ ...blob, records: blob.records.filter((r) => r.id !== id) });
      armIdle();
    },
    [blob, persist, armIdle],
  );

  const setActive = useCallback(
    async (id: string) => {
      if (!blob) throw new Error('保险库已锁定');
      const target = blob.records.find((r) => r.id === id);
      if (!target) return;
      const records = blob.records.map((r) => ({
        ...r,
        isActive: r.entryId === target.entryId ? r.id === id : r.isActive,
      }));
      persist({ ...blob, records });
      armIdle();
    },
    [blob, persist, armIdle],
  );

  const revealFields = useCallback(
    async (id: string) => {
      if (!dek || !blob) throw new Error('保险库已锁定');
      const record = blob.records.find((r) => r.id === id);
      if (!record) throw new Error('凭据不存在');
      const cred = await fromVaultRecord(dek, record);
      armIdle();
      return cred.fields;
    },
    [dek, blob, armIdle],
  );

  const exportBackup = useCallback(
    async (exportPassword: string) => {
      if (!dek || !blob) throw new Error('保险库已锁定');
      const creds: Credential[] = [];
      for (const r of blob.records) {
        creds.push(await fromVaultRecord(dek, r));
      }
      const file = await createEncryptedBackup(exportPassword, creds);
      armIdle();
      return `${JSON.stringify(file, null, 2)}\n`;
    },
    [dek, blob, armIdle],
  );

  const importBackup = useCallback(
    async (exportPassword: string, json: string) => {
      if (!dek || !blob) throw new Error('保险库已锁定');
      const incoming = await parseEncryptedBackup(exportPassword, json);
      const existing = new Set(blob.records.map((r) => r.id));
      let added = 0;
      let skipped = 0;
      const records = [...blob.records];
      for (const cred of incoming) {
        if (existing.has(cred.id)) {
          skipped += 1;
          continue;
        }
        const record = await toVaultRecord(dek, { ...cred, isActive: false });
        records.push(record);
        existing.add(cred.id);
        added += 1;
      }
      persist({ ...blob, records });
      armIdle();
      return { added, skipped };
    },
    [dek, blob, persist, armIdle],
  );

  const wipeVault = useCallback(() => {
    lock();
    clearVaultBlob();
    setBlob(null);
    setHasVault(false);
  }, [lock]);

  const value = useMemo<VaultContextValue>(
    () => ({
      ready,
      hasVault: hasVault || vaultExists(),
      unlocked: dek != null,
      error,
      records: blob?.records ?? [],
      setup,
      unlock,
      lock,
      addCredential,
      updateCredential,
      removeCredential,
      setActive,
      revealFields,
      exportBackup,
      importBackup,
      wipeVault,
      touch,
    }),
    [
      ready,
      hasVault,
      dek,
      error,
      blob,
      setup,
      unlock,
      lock,
      addCredential,
      updateCredential,
      removeCredential,
      setActive,
      revealFields,
      exportBackup,
      importBackup,
      wipeVault,
      touch,
    ],
  );

  return <VaultContext.Provider value={value}>{children}</VaultContext.Provider>;
}

export function useVault(): VaultContextValue {
  const ctx = useContext(VaultContext);
  if (!ctx) throw new Error('useVault 须在 VaultProvider 内');
  return ctx;
}

export { recordMeta, collectCredentialAlerts };
