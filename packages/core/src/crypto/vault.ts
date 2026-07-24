import { Credential, type Credential as CredentialT } from '../schema/credential.ts';
import {
  VAULT_KDF_ITERATIONS,
  decryptJson,
  deriveKek,
  encryptJson,
  generateDek,
  randomSalt,
  saltFromB64,
  saltToB64,
  unwrapDek,
  wrapDek,
} from './webcrypto.ts';

export interface VaultBlob {
  version: 1;
  kdf: 'pbkdf2-sha256';
  iterations: number;
  salt: string;
  wrappedDek: string;
  wrapIv: string;
  records: VaultRecord[];
}

/** 落盘结构：元数据明文，fields 密文。 */
export interface VaultRecord {
  id: string;
  entryId: string;
  accountLabel: string;
  type: CredentialT['type'];
  envMapping?: Record<string, string>;
  isActive: boolean;
  quotaNote?: string;
  expiresAt?: string;
  createdAt: string;
  lastUsedAt?: string;
  fieldsIv: string;
  fieldsCiphertext: string;
}

export type CredentialPlain = CredentialT;

export function emptyVaultBlob(salt: Uint8Array, wrap: { iv: string; wrapped: string }): VaultBlob {
  return {
    version: 1,
    kdf: 'pbkdf2-sha256',
    iterations: VAULT_KDF_ITERATIONS,
    salt: saltToB64(salt),
    wrappedDek: wrap.wrapped,
    wrapIv: wrap.iv,
    records: [],
  };
}

/** 首次初始化保险库：生成 DEK 并用主密码派生的 KEK 包装。 */
export async function createVault(password: string): Promise<{ blob: VaultBlob; dek: CryptoKey }> {
  const salt = randomSalt();
  const kek = await deriveKek(password, salt);
  const dek = await generateDek();
  const wrap = await wrapDek(dek, kek);
  return { blob: emptyVaultBlob(salt, wrap), dek };
}

/** 用主密码解锁，返回 DEK（失败抛错）。 */
export async function unlockVault(blob: VaultBlob, password: string): Promise<CryptoKey> {
  const kek = await deriveKek(password, saltFromB64(blob.salt), blob.iterations);
  try {
    return await unwrapDek(blob.wrappedDek, blob.wrapIv, kek);
  } catch {
    throw new Error('E_AUTH: 主密码不正确');
  }
}

export async function encryptCredentialFields(
  dek: CryptoKey,
  fields: Record<string, string>,
): Promise<{ fieldsIv: string; fieldsCiphertext: string }> {
  const { iv, ciphertext } = await encryptJson(dek, fields);
  return { fieldsIv: iv, fieldsCiphertext: ciphertext };
}

export async function decryptCredentialFields(
  dek: CryptoKey,
  record: VaultRecord,
): Promise<Record<string, string>> {
  return decryptJson(dek, record.fieldsIv, record.fieldsCiphertext);
}

export async function toVaultRecord(dek: CryptoKey, cred: CredentialPlain): Promise<VaultRecord> {
  const parsed = Credential.parse(cred);
  const enc = await encryptCredentialFields(dek, parsed.fields);
  return {
    id: parsed.id,
    entryId: parsed.entryId,
    accountLabel: parsed.accountLabel,
    type: parsed.type,
    envMapping: parsed.envMapping,
    isActive: parsed.isActive,
    quotaNote: parsed.quotaNote,
    expiresAt: parsed.expiresAt,
    createdAt: parsed.createdAt,
    lastUsedAt: parsed.lastUsedAt,
    ...enc,
  };
}

export async function fromVaultRecord(
  dek: CryptoKey,
  record: VaultRecord,
): Promise<CredentialPlain> {
  const fields = await decryptCredentialFields(dek, record);
  return Credential.parse({
    id: record.id,
    entryId: record.entryId,
    accountLabel: record.accountLabel,
    type: record.type,
    fields,
    envMapping: record.envMapping,
    isActive: record.isActive,
    quotaNote: record.quotaNote,
    expiresAt: record.expiresAt,
    createdAt: record.createdAt,
    lastUsedAt: record.lastUsedAt,
  });
}

/** 列表用：不解密 fields。 */
export function recordMeta(
  record: VaultRecord,
): Omit<CredentialPlain, 'fields'> & { fields: Record<string, string> } {
  return {
    id: record.id,
    entryId: record.entryId,
    accountLabel: record.accountLabel,
    type: record.type,
    fields: {},
    envMapping: record.envMapping,
    isActive: record.isActive,
    quotaNote: record.quotaNote,
    expiresAt: record.expiresAt,
    createdAt: record.createdAt,
    lastUsedAt: record.lastUsedAt,
  };
}
