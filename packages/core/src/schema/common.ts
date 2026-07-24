import { z } from 'zod';

/** ID 规范：小写 kebab-case，全局唯一。见 SPEC 附录 A。 */
export const idRegex = /^[a-z0-9][a-z0-9-]*$/;
export const Id = z.string().regex(idRegex, 'ID 必须为小写 kebab-case');
export type Id = z.infer<typeof Id>;

export const Region = z.enum(['overseas', 'domestic', 'both']);
export type Region = z.infer<typeof Region>;

export const Maturity = z.enum(['experimental', 'beta', 'stable', 'mature']);
export type Maturity = z.infer<typeof Maturity>;

export const Confidence = z.enum(['verified', 'community', 'inferred']);
export type Confidence = z.infer<typeof Confidence>;

export const PricingModel = z.enum(['free', 'freemium', 'subscription', 'usage', 'open-source']);
export type PricingModel = z.infer<typeof PricingModel>;

/** ISO 日期（YYYY-MM-DD） */
export const IsoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '需为 YYYY-MM-DD');
export type IsoDate = z.infer<typeof IsoDate>;
