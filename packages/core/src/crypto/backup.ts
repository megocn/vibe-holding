import { Credential, type Credential as CredentialT } from '../schema/credential.ts';
import {
  VAULT_KDF_ITERATIONS,
  decryptJson,
  deriveKek,
  encryptJson,
  randomSalt,
  saltFromB64,
  saltToB64,
} from './webcrypto.ts';

/** 可移植加密备份（与本机 VaultBlob 分离，可用独立口令）。 */
export interface VaultBackupFile {
  version: 1;
  kind: 'vh-vault-backup';
  exportedAt: string;
  kdf: 'pbkdf2-sha256';
  iterations: number;
  salt: string;
  iv: string;
  ciphertext: string;
  /** 不含密文字段的条数，便于预览 */
  count: number;
}

export function isVaultBackupFile(value: unknown): value is VaultBackupFile {
  if (!value || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  return (
    v.kind === 'vh-vault-backup' &&
    v.version === 1 &&
    typeof v.salt === 'string' &&
    typeof v.iv === 'string' &&
    typeof v.ciphertext === 'string'
  );
}

/** 用导出口令加密凭据明文列表。 */
export async function createEncryptedBackup(
  password: string,
  credentials: CredentialT[],
): Promise<VaultBackupFile> {
  if (password.length < 8) throw new Error('导出口令至少 8 位');
  const parsed = credentials.map((c) => Credential.parse(c));
  const salt = randomSalt();
  const key = await deriveKek(password, salt);
  const { iv, ciphertext } = await encryptJson(key, parsed);
  return {
    version: 1,
    kind: 'vh-vault-backup',
    exportedAt: new Date().toISOString(),
    kdf: 'pbkdf2-sha256',
    iterations: VAULT_KDF_ITERATIONS,
    salt: saltToB64(salt),
    iv,
    ciphertext,
    count: parsed.length,
  };
}

/** 解密备份；口令错误抛 E_AUTH。 */
export async function parseEncryptedBackup(
  password: string,
  backup: VaultBackupFile | string,
): Promise<CredentialT[]> {
  const file: VaultBackupFile =
    typeof backup === 'string' ? (JSON.parse(backup) as VaultBackupFile) : backup;
  if (!isVaultBackupFile(file)) throw new Error('不是有效的 VibeHolding 凭据备份');
  const key = await deriveKek(password, saltFromB64(file.salt), file.iterations);
  try {
    const raw = await decryptJson<unknown>(key, file.iv, file.ciphertext);
    if (!Array.isArray(raw)) throw new Error('备份载荷格式错误');
    return raw.map((c) => Credential.parse(c));
  } catch (err) {
    if (err instanceof Error && err.message.startsWith('E_AUTH')) throw err;
    if (err instanceof Error && /明文|format|parse|OperationError|decrypt/i.test(err.message)) {
      throw new Error('E_AUTH: 导出口令不正确或备份已损坏');
    }
    // AES-GCM 失败多为口令错误
    throw new Error('E_AUTH: 导出口令不正确或备份已损坏');
  }
}

export type CredAlertKind = 'expired' | 'expiring-soon' | 'quota-note';

export interface CredAlert {
  kind: CredAlertKind;
  recordId: string;
  entryId: string;
  accountLabel: string;
  message: string;
  expiresAt?: string;
}

type AlertSource = {
  id: string;
  entryId: string;
  accountLabel: string;
  expiresAt?: string;
  quotaNote?: string;
};

function daysBetween(a: string, b: string): number {
  const ms = Date.parse(`${b}T00:00:00Z`) - Date.parse(`${a}T00:00:00Z`);
  return Math.round(ms / 86_400_000);
}

/**
 * 从凭据元数据收集到期 / 额度提醒（不解密 fields）。
 * @param warnWithinDays 距到期多少天内视为「即将到期」（默认 30）
 */
export function collectCredentialAlerts(
  records: AlertSource[],
  opts?: { today?: string; warnWithinDays?: number },
): CredAlert[] {
  const today = opts?.today ?? new Date().toISOString().slice(0, 10);
  const warnWithinDays = opts?.warnWithinDays ?? 30;
  const alerts: CredAlert[] = [];

  for (const r of records) {
    if (r.expiresAt && /^\d{4}-\d{2}-\d{2}$/.test(r.expiresAt)) {
      const d = daysBetween(today, r.expiresAt);
      if (d < 0) {
        alerts.push({
          kind: 'expired',
          recordId: r.id,
          entryId: r.entryId,
          accountLabel: r.accountLabel,
          message: `已过期 ${Math.abs(d)} 天（${r.expiresAt}）`,
          expiresAt: r.expiresAt,
        });
      } else if (d <= warnWithinDays) {
        alerts.push({
          kind: 'expiring-soon',
          recordId: r.id,
          entryId: r.entryId,
          accountLabel: r.accountLabel,
          message: d === 0 ? `今日到期（${r.expiresAt}）` : `${d} 天后到期（${r.expiresAt}）`,
          expiresAt: r.expiresAt,
        });
      }
    }
    const note = r.quotaNote?.trim();
    if (note) {
      alerts.push({
        kind: 'quota-note',
        recordId: r.id,
        entryId: r.entryId,
        accountLabel: r.accountLabel,
        message: note,
        expiresAt: r.expiresAt,
      });
    }
  }

  const rank = (k: CredAlertKind) => (k === 'expired' ? 0 : k === 'expiring-soon' ? 1 : 2);
  return alerts.sort(
    (a, b) =>
      rank(a.kind) - rank(b.kind) ||
      (a.expiresAt ?? '').localeCompare(b.expiresAt ?? '') ||
      a.accountLabel.localeCompare(b.accountLabel),
  );
}
