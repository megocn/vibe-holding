import { describe, expect, it } from 'vitest';
import {
  collectCredentialAlerts,
  createEncryptedBackup,
  isVaultBackupFile,
  parseEncryptedBackup,
} from './backup.ts';

describe('encrypted backup', () => {
  it('导出再导入往返', async () => {
    const creds = [
      {
        id: '00000000-0000-4000-8000-0000000000aa',
        entryId: 'cursor',
        accountLabel: 'main',
        type: 'api_key' as const,
        fields: { API_KEY: 'sk-test' },
        isActive: true,
        expiresAt: '2026-12-01',
        quotaNote: '剩 $20',
        createdAt: '2026-07-01T00:00:00.000Z',
      },
    ];
    const backup = await createEncryptedBackup('export-pass-ok', creds);
    expect(isVaultBackupFile(backup)).toBe(true);
    expect(JSON.stringify(backup)).not.toContain('sk-test');
    expect(backup.count).toBe(1);

    const restored = await parseEncryptedBackup('export-pass-ok', backup);
    expect(restored).toHaveLength(1);
    expect(restored[0]?.fields.API_KEY).toBe('sk-test');
    expect(restored[0]?.expiresAt).toBe('2026-12-01');
  });

  it('错误口令拒绝', async () => {
    const backup = await createEncryptedBackup('export-pass-ok', [
      {
        id: '00000000-0000-4000-8000-0000000000bb',
        entryId: 'vercel',
        accountLabel: 'hobby',
        type: 'api_key' as const,
        fields: { TOKEN: 'secret' },
        isActive: false,
        createdAt: '2026-07-01T00:00:00.000Z',
      },
    ]);
    await expect(parseEncryptedBackup('wrong-password', backup)).rejects.toThrow(/E_AUTH/);
  });
});

describe('collectCredentialAlerts', () => {
  it('过期 / 即将到期 / 额度备注', () => {
    const alerts = collectCredentialAlerts(
      [
        {
          id: '1',
          entryId: 'a',
          accountLabel: 'old',
          expiresAt: '2026-01-01',
        },
        {
          id: '2',
          entryId: 'b',
          accountLabel: 'soon',
          expiresAt: '2026-08-01',
        },
        {
          id: '3',
          entryId: 'c',
          accountLabel: 'quota',
          quotaNote: '额度将尽',
        },
        {
          id: '4',
          entryId: 'd',
          accountLabel: 'far',
          expiresAt: '2027-01-01',
        },
      ],
      { today: '2026-07-23', warnWithinDays: 30 },
    );
    expect(alerts.map((a) => a.kind)).toEqual(['expired', 'expiring-soon', 'quota-note']);
    expect(alerts[0]?.accountLabel).toBe('old');
    expect(alerts[1]?.accountLabel).toBe('soon');
  });
});
