import type { Credential, CredentialType, Id } from '@vh/core';
import { type ReactNode, useMemo, useRef, useState } from 'react';
import { useContent } from '../lib/content.tsx';
import { collectCredentialAlerts, useVault } from '../lib/vault.tsx';
import { Icon } from './Icon.tsx';

const TYPES: { value: CredentialType; label: string }[] = [
  { value: 'api_key', label: 'API Key' },
  { value: 'password', label: '密码' },
  { value: 'oauth_token', label: 'OAuth Token' },
  { value: 'env_group', label: '环境变量组' },
];

export function CredentialsView() {
  const vault = useVault();
  const { bundle } = useContent();
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [revealed, setRevealed] = useState<Record<string, Record<string, string>>>({});
  const [copyToast, setCopyToast] = useState<string | null>(null);
  const [backupPw, setBackupPw] = useState('');
  const [backupPw2, setBackupPw2] = useState('');
  const [showBackup, setShowBackup] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const alerts = useMemo(() => collectCredentialAlerts(vault.records), [vault.records]);

  const grouped = useMemo(() => {
    const map = new Map<string, typeof vault.records>();
    for (const r of vault.records) {
      const list = map.get(r.entryId) ?? [];
      list.push(r);
      map.set(r.entryId, list);
    }
    return [...map.entries()].sort((a, b) => {
      const na = bundle.entries.get(a[0])?.name ?? a[0];
      const nb = bundle.entries.get(b[0])?.name ?? b[0];
      return na.localeCompare(nb);
    });
  }, [vault.records, bundle.entries]);

  async function onSetup() {
    setFormError(null);
    if (password !== password2) {
      setFormError('两次主密码不一致');
      return;
    }
    setBusy(true);
    try {
      await vault.setup(password);
      setPassword('');
      setPassword2('');
    } catch (e) {
      setFormError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onUnlock() {
    setFormError(null);
    setBusy(true);
    try {
      await vault.unlock(password);
      setPassword('');
    } catch (e) {
      setFormError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onReveal(id: string) {
    vault.touch();
    if (revealed[id]) {
      setRevealed((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
      return;
    }
    try {
      const fields = await vault.revealFields(id);
      setRevealed((prev) => ({ ...prev, [id]: fields }));
      window.setTimeout(() => {
        setRevealed((prev) => {
          const next = { ...prev };
          delete next[id];
          return next;
        });
      }, 30_000);
    } catch (e) {
      setFormError(e instanceof Error ? e.message : String(e));
    }
  }

  async function onCopy(id: string, key: string, value: string) {
    vault.touch();
    await navigator.clipboard.writeText(value);
    setCopyToast(`已复制 ${key}（30 秒后尝试清空剪贴板）`);
    window.setTimeout(() => setCopyToast(null), 2000);
    window.setTimeout(async () => {
      try {
        const cur = await navigator.clipboard.readText();
        if (cur === value) await navigator.clipboard.writeText('');
      } catch {
        /* 浏览器可能拒绝读剪贴板 */
      }
    }, 30_000);
  }

  async function onExport() {
    setFormError(null);
    if (backupPw.length < 8) {
      setFormError('导出口令至少 8 位');
      return;
    }
    if (backupPw !== backupPw2) {
      setFormError('两次导出口令不一致');
      return;
    }
    if (!window.confirm('将下载加密备份文件。请牢记导出口令（可与主密码不同）。')) return;
    setBusy(true);
    try {
      const json = await vault.exportBackup(backupPw);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vh-vault-backup-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setBackupPw('');
      setBackupPw2('');
      setShowBackup(false);
      setCopyToast('已导出加密备份');
      window.setTimeout(() => setCopyToast(null), 2000);
    } catch (e) {
      setFormError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onImportFile(file: File) {
    setFormError(null);
    const pw = window.prompt('输入该备份的导出口令');
    if (pw == null) return;
    if (pw.length < 8) {
      setFormError('导出口令至少 8 位');
      return;
    }
    setBusy(true);
    try {
      const text = await file.text();
      const { added, skipped } = await vault.importBackup(pw, text);
      setCopyToast(`导入完成：新增 ${added}，跳过重复 ${skipped}`);
      window.setTimeout(() => setCopyToast(null), 2800);
    } catch (e) {
      setFormError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  }

  if (!vault.ready) {
    return <div style={{ padding: 24, color: 'var(--ink-3)' }}>加载保险库…</div>;
  }

  if (!vault.hasVault) {
    return (
      <Gate
        title="创建凭据保险库"
        subtitle="主密码用于派生加密密钥。仅存本机，无法找回，请牢记。"
        error={formError}
      >
        <input
          className="vh-input"
          type="password"
          placeholder="主密码（≥8 位）"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: '100%', boxSizing: 'border-box', marginBottom: 8 }}
        />
        <input
          className="vh-input"
          type="password"
          placeholder="再次输入主密码"
          value={password2}
          onChange={(e) => setPassword2(e.target.value)}
          style={{ width: '100%', boxSizing: 'border-box', marginBottom: 12 }}
        />
        <button type="button" className="vh-btn" disabled={busy} onClick={onSetup}>
          创建并解锁
        </button>
      </Gate>
    );
  }

  if (!vault.unlocked) {
    return (
      <Gate
        title="解锁保险库"
        subtitle="输入主密码以查看与管理凭据。空闲 5 分钟自动锁定。"
        error={formError}
      >
        <input
          className="vh-input"
          type="password"
          placeholder="主密码"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onUnlock()}
          style={{ width: '100%', boxSizing: 'border-box', marginBottom: 12 }}
        />
        <button type="button" className="vh-btn" disabled={busy} onClick={onUnlock}>
          解锁
        </button>
      </Gate>
    );
  }

  return (
    <div
      className="overflow-y-auto"
      style={{ height: '100%', padding: 24 }}
      onMouseMove={vault.touch}
    >
      <div className="flex items-center gap-2" style={{ marginBottom: 16 }}>
        <h1 className="vh-text-h1" style={{ margin: 0, flex: 1 }}>
          凭据
        </h1>
        {copyToast && (
          <span className="vh-text-caption" style={{ color: 'var(--pigment-success)' }}>
            {copyToast}
          </span>
        )}
        <button type="button" className="vh-btn vh-btn-primary" onClick={() => setShowForm(true)}>
          <Icon name="Plus" size={14} /> 添加
        </button>
        <button type="button" className="vh-btn" onClick={() => setShowBackup((v) => !v)}>
          <Icon name="ArrowsLeftRight" size={14} /> 导入/导出
        </button>
        <button type="button" className="vh-btn" onClick={vault.lock}>
          <Icon name="Lock" size={14} /> 锁定
        </button>
      </div>

      {formError && (
        <div style={{ color: 'var(--pigment-danger)', marginBottom: 12, fontSize: 13 }}>
          {formError}
        </div>
      )}

      {alerts.length > 0 && (
        <div
          className="vh-panel"
          style={{
            padding: 12,
            marginBottom: 16,
            borderColor: 'color-mix(in oklch, var(--pigment-warning) 45%, var(--line))',
          }}
        >
          <div className="vh-section-title" style={{ borderBottom: 'none', paddingBottom: 4 }}>
            <Icon name="Warning" size={14} color="var(--pigment-warning)" /> 提醒 · {alerts.length}
          </div>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, color: 'var(--ink-2)' }}>
            {alerts.slice(0, 8).map((a) => (
              <li key={`${a.kind}-${a.recordId}`} style={{ marginBottom: 4 }}>
                <span style={{ fontWeight: 500, color: 'var(--ink-1)' }}>
                  {bundle.entries.get(a.entryId)?.name ?? a.entryId}
                </span>
                {' · '}
                {a.accountLabel}
                {' — '}
                {a.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {showBackup && (
        <div className="vh-panel" style={{ padding: 14, marginBottom: 16 }}>
          <div className="vh-section-title" style={{ borderBottom: 'none', paddingBottom: 0 }}>
            加密导入 / 导出
          </div>
          <p className="vh-text-caption" style={{ color: 'var(--ink-3)', margin: '4px 0 10px' }}>
            备份使用独立导出口令（PBKDF2 + AES-GCM），与主密码可不同。导入时跳过已有 id。
          </p>
          <input
            className="vh-input"
            type="password"
            placeholder="导出口令（≥8）"
            value={backupPw}
            onChange={(e) => setBackupPw(e.target.value)}
            style={{ width: '100%', boxSizing: 'border-box', marginBottom: 8 }}
          />
          <input
            className="vh-input"
            type="password"
            placeholder="再次确认导出口令"
            value={backupPw2}
            onChange={(e) => setBackupPw2(e.target.value)}
            style={{ width: '100%', boxSizing: 'border-box', marginBottom: 10 }}
          />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="vh-btn vh-btn-primary"
              disabled={busy}
              onClick={onExport}
            >
              <Icon name="DownloadSimple" size={14} /> 导出备份
            </button>
            <button
              type="button"
              className="vh-btn"
              disabled={busy}
              onClick={() => fileRef.current?.click()}
            >
              <Icon name="UploadSimple" size={14} /> 导入备份
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="application/json,.json"
              style={{ display: 'none' }}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void onImportFile(f);
              }}
            />
          </div>
        </div>
      )}

      {showForm && (
        <CredentialForm
          entryOptions={[...bundle.entries.values()].map((e) => ({ id: e.id, name: e.name }))}
          onCancel={() => setShowForm(false)}
          onSave={async (cred) => {
            await vault.addCredential(cred);
            setShowForm(false);
          }}
        />
      )}

      {grouped.length === 0 && !showForm && (
        <div style={{ color: 'var(--ink-3)', fontSize: 14 }}>尚无凭据。点击「添加」开始。</div>
      )}

      {grouped.map(([entryId, records]) => (
        <section key={entryId} style={{ marginBottom: 20 }}>
          <h2
            className="vh-display"
            style={{ fontSize: 15, color: 'var(--ink-2)', margin: '0 0 8px' }}
          >
            {bundle.entries.get(entryId)?.name ?? entryId}
          </h2>
          <div className="flex flex-col gap-2">
            {records.map((r) => {
              const fields = revealed[r.id];
              return (
                <div key={r.id} className="vh-card" style={{ padding: 12 }}>
                  <div className="flex items-center gap-2" style={{ marginBottom: 6 }}>
                    <span style={{ fontWeight: 500, flex: 1 }}>{r.accountLabel}</span>
                    <span className="vh-tag">
                      {TYPES.find((t) => t.value === r.type)?.label ?? r.type}
                    </span>
                    {r.isActive && (
                      <span className="vh-tag" style={{ color: 'var(--pigment-success)' }}>
                        当前生效
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--ink-3)', marginBottom: 8 }}>
                    {(r.expiresAt || r.quotaNote) && (
                      <div style={{ marginBottom: 6 }}>
                        {r.expiresAt && (
                          <span
                            className="vh-tag"
                            style={{
                              marginRight: 6,
                              color:
                                r.expiresAt < new Date().toISOString().slice(0, 10)
                                  ? 'var(--pigment-danger)'
                                  : 'var(--ink-2)',
                            }}
                          >
                            到期 {r.expiresAt}
                          </span>
                        )}
                        {r.quotaNote && <span className="vh-tag">{r.quotaNote}</span>}
                      </div>
                    )}
                    {fields
                      ? Object.entries(fields).map(([k, v]) => (
                          <div
                            key={k}
                            className="flex items-center gap-2"
                            style={{ marginBottom: 4 }}
                          >
                            <span className="vh-mono">{k}</span>
                            <span className="vh-mono" style={{ flex: 1 }}>
                              {v}
                            </span>
                            <button
                              type="button"
                              className="vh-btn"
                              style={{ padding: '2px 6px' }}
                              onClick={() => onCopy(r.id, k, v)}
                            >
                              复制
                            </button>
                          </div>
                        ))
                      : '••••••••（点击显示解密）'}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button type="button" className="vh-btn" onClick={() => onReveal(r.id)}>
                      <Icon name={fields ? 'EyeSlash' : 'Eye'} size={14} />
                      {fields ? '隐藏' : '显示'}
                    </button>
                    {!r.isActive && (
                      <button
                        type="button"
                        className="vh-btn"
                        onClick={() => vault.setActive(r.id)}
                      >
                        设为生效
                      </button>
                    )}
                    <button
                      type="button"
                      className="vh-btn"
                      style={{ color: 'var(--pigment-danger)' }}
                      onClick={() => {
                        if (window.confirm(`删除账号「${r.accountLabel}」？`)) {
                          void vault.removeCredential(r.id);
                          setRevealed((prev) => {
                            const next = { ...prev };
                            delete next[r.id];
                            return next;
                          });
                        }
                      }}
                    >
                      删除
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      ))}

      <div style={{ marginTop: 32, paddingTop: 16, borderTop: '1px solid var(--line)' }}>
        <button
          type="button"
          className="vh-btn"
          style={{ color: 'var(--pigment-danger)' }}
          onClick={() => {
            if (window.confirm('销毁本机保险库？所有凭据密文将被删除且无法恢复。')) {
              vault.wipeVault();
            }
          }}
        >
          销毁保险库
        </button>
        <div style={{ marginTop: 8, fontSize: 12, color: 'var(--ink-3)' }}>
          使用 PBKDF2 + AES-256-GCM（WebCrypto）。正式版将迁移至 Argon2id +
          XChaCha20（Tauri/libsodium）与 OS 钥匙串。
        </div>
      </div>
    </div>
  );
}

function Gate({
  title,
  subtitle,
  error,
  children,
}: {
  title: string;
  subtitle: string;
  error: string | null;
  children: ReactNode;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center"
      style={{ height: '100%', padding: 24 }}
    >
      <div className="vh-lock-gate">
        <div
          className="flex items-center gap-2.5"
          style={{ marginBottom: 10, position: 'relative', zIndex: 1 }}
        >
          <Icon name="LockKey" size={28} weight="duotone" color="var(--pigment-seal)" />
          <h1 className="vh-text-h2" style={{ margin: 0, color: 'var(--ink-1)' }}>
            {title}
          </h1>
        </div>
        <p
          className="vh-text-sm"
          style={{ color: 'var(--ink-2)', marginBottom: 16, position: 'relative', zIndex: 1 }}
        >
          {subtitle}
        </p>
        {error && (
          <div
            className="vh-text-caption"
            style={{
              color: 'var(--pigment-danger)',
              marginBottom: 10,
              position: 'relative',
              zIndex: 1,
            }}
          >
            {error}
          </div>
        )}
        <div style={{ position: 'relative', zIndex: 1 }}>{children}</div>
      </div>
    </div>
  );
}

function CredentialForm({
  entryOptions,
  onCancel,
  onSave,
}: {
  entryOptions: { id: Id; name: string }[];
  onCancel: () => void;
  onSave: (cred: Credential) => Promise<void>;
}) {
  const [entryId, setEntryId] = useState(entryOptions[0]?.id ?? '');
  const [accountLabel, setAccountLabel] = useState('default');
  const [type, setType] = useState<CredentialType>('api_key');
  const [fieldKey, setFieldKey] = useState('API_KEY');
  const [fieldValue, setFieldValue] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [expiresAt, setExpiresAt] = useState('');
  const [quotaNote, setQuotaNote] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit() {
    setErr(null);
    if (!entryId || !accountLabel.trim() || !fieldKey.trim() || !fieldValue) {
      setErr('请填写完整');
      return;
    }
    if (expiresAt && !/^\d{4}-\d{2}-\d{2}$/.test(expiresAt)) {
      setErr('到期日须为 YYYY-MM-DD');
      return;
    }
    setBusy(true);
    try {
      await onSave({
        id: globalThis.crypto.randomUUID(),
        entryId,
        accountLabel: accountLabel.trim(),
        type,
        fields: { [fieldKey.trim()]: fieldValue },
        isActive,
        expiresAt: expiresAt || undefined,
        quotaNote: quotaNote.trim() || undefined,
        createdAt: new Date().toISOString(),
      });
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      className="vh-panel"
      style={{
        padding: 14,
        marginBottom: 16,
      }}
    >
      <div className="vh-section-title" style={{ borderBottom: 'none', paddingBottom: 0 }}>
        新建凭据
      </div>
      {err && (
        <div style={{ color: 'var(--pigment-danger)', fontSize: 13, marginBottom: 8 }}>{err}</div>
      )}
      <label style={{ display: 'block', fontSize: 13, color: 'var(--ink-2)', marginBottom: 8 }}>
        关联条目
        <select
          className="vh-input"
          style={{ width: '100%', marginTop: 4 }}
          value={entryId}
          onChange={(e) => setEntryId(e.target.value)}
        >
          {entryOptions.map((o) => (
            <option key={o.id} value={o.id}>
              {o.name}
            </option>
          ))}
        </select>
      </label>
      <input
        className="vh-input"
        placeholder="账号标签"
        value={accountLabel}
        onChange={(e) => setAccountLabel(e.target.value)}
        style={{ width: '100%', boxSizing: 'border-box', marginBottom: 8 }}
      />
      <select
        className="vh-input"
        style={{ width: '100%', marginBottom: 8 }}
        value={type}
        onChange={(e) => setType(e.target.value as CredentialType)}
      >
        {TYPES.map((t) => (
          <option key={t.value} value={t.value}>
            {t.label}
          </option>
        ))}
      </select>
      <div className="flex gap-2" style={{ marginBottom: 8 }}>
        <input
          className="vh-input"
          placeholder="字段名"
          value={fieldKey}
          onChange={(e) => setFieldKey(e.target.value)}
          style={{ flex: 1, boxSizing: 'border-box' }}
        />
        <input
          className="vh-input"
          type="password"
          placeholder="密钥值"
          value={fieldValue}
          onChange={(e) => setFieldValue(e.target.value)}
          style={{ flex: 2, boxSizing: 'border-box' }}
        />
      </div>
      <label className="flex items-center gap-2" style={{ fontSize: 13, marginBottom: 10 }}>
        <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
        设为该平台当前生效账号
      </label>
      <div className="flex gap-2" style={{ marginBottom: 8 }}>
        <label style={{ flex: 1, fontSize: 12, color: 'var(--ink-3)' }}>
          到期日
          <input
            className="vh-input"
            type="date"
            value={expiresAt}
            onChange={(e) => setExpiresAt(e.target.value)}
            style={{ width: '100%', boxSizing: 'border-box', marginTop: 4 }}
          />
        </label>
        <label style={{ flex: 2, fontSize: 12, color: 'var(--ink-3)' }}>
          额度备注
          <input
            className="vh-input"
            placeholder="如：剩 $50"
            value={quotaNote}
            onChange={(e) => setQuotaNote(e.target.value)}
            style={{ width: '100%', boxSizing: 'border-box', marginTop: 4 }}
          />
        </label>
      </div>
      <div className="flex gap-2">
        <button type="button" className="vh-btn" disabled={busy} onClick={submit}>
          保存
        </button>
        <button type="button" className="vh-btn" onClick={onCancel}>
          取消
        </button>
      </div>
    </div>
  );
}
