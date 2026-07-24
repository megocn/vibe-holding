import { z } from 'zod';
import { Id, IsoDate } from './common.ts';

/**
 * 凭据（个人数据，本地加密）。此处描述明文结构；
 * 存储时 fields 的值均为密文，加解密见 crypto 模块（M2）。
 */
export const CredentialType = z.enum(['api_key', 'password', 'oauth_token', 'env_group']);
export type CredentialType = z.infer<typeof CredentialType>;

export const Credential = z.object({
  id: z.string().uuid(),
  entryId: Id,
  accountLabel: z.string(),
  type: CredentialType,
  fields: z.record(z.string(), z.string()),
  envMapping: z.record(z.string(), z.string()).optional(),
  isActive: z.boolean().default(false),
  /** 额度/用量备注（提醒用，明文元数据） */
  quotaNote: z.string().optional(),
  /** 到期日 YYYY-MM-DD（提醒用，明文元数据） */
  expiresAt: IsoDate.optional(),
  createdAt: z.string(),
  lastUsedAt: z.string().optional(),
});
export type Credential = z.infer<typeof Credential>;
