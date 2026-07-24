import { describe, expect, it } from 'vitest';
import {
  createVault,
  decryptCredentialFields,
  encryptCredentialFields,
  unlockVault,
} from './vault.ts';

describe('vault crypto', () => {
  it('创建并解锁往返', async () => {
    const { blob, dek } = await createVault('test-passphrase-正确');
    const dek2 = await unlockVault(blob, 'test-passphrase-正确');
    const enc = await encryptCredentialFields(dek, { API_KEY: 'sk-secret' });
    const fields = await decryptCredentialFields(dek2, {
      id: 'x',
      entryId: 'cursor',
      accountLabel: 'main',
      type: 'api_key',
      isActive: true,
      createdAt: '2026-07-23T00:00:00.000Z',
      fieldsIv: enc.fieldsIv,
      fieldsCiphertext: enc.fieldsCiphertext,
    });
    expect(fields.API_KEY).toBe('sk-secret');
  });

  it('错误主密码拒绝解锁', async () => {
    const { blob } = await createVault('right-password');
    await expect(unlockVault(blob, 'wrong-password')).rejects.toThrow(/E_AUTH/);
  });

  it('落盘 blob 不含明文密钥', async () => {
    const { blob, dek } = await createVault('secret');
    const enc = await encryptCredentialFields(dek, { token: 'plain-value-should-not-appear' });
    blob.records.push({
      id: '00000000-0000-4000-8000-000000000001',
      entryId: 'cursor',
      accountLabel: 'dev',
      type: 'api_key',
      isActive: true,
      createdAt: '2026-07-23T00:00:00.000Z',
      fieldsIv: enc.fieldsIv,
      fieldsCiphertext: enc.fieldsCiphertext,
    });
    const serialized = JSON.stringify(blob);
    expect(serialized).not.toContain('plain-value-should-not-appear');
    expect(serialized).not.toContain('secret');
  });
});
