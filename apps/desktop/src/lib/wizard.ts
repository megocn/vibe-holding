import type { Id, RecommendPrefs } from '@vh/core';

/** 向导默认层顺序（与内容分类 id 对齐）；支付层按是否收费动态加入。 */
export const WIZARD_CORE_LAYERS: Id[] = [
  'coding-agent',
  'llm',
  'framework',
  'ui-library',
  'baas-auth',
  'cloud-deploy',
];

export const PAYMENT_LAYER: Id = 'payment';

export interface WizardAnswers {
  market: NonNullable<RecommendPrefs['market']>;
  budget: NonNullable<RecommendPrefs['budget']>;
  monetize: boolean;
  preferOpenSource: boolean;
}

export const DEFAULT_ANSWERS: WizardAnswers = {
  market: 'overseas',
  budget: 'low',
  monetize: true,
  preferOpenSource: false,
};

export function layersForAnswers(answers: WizardAnswers): Id[] {
  const layers = [...WIZARD_CORE_LAYERS];
  if (answers.monetize) layers.push(PAYMENT_LAYER);
  return layers;
}

export function prefsFromAnswers(answers: WizardAnswers): RecommendPrefs {
  return {
    market: answers.market,
    budget: answers.budget,
    preferOpenSource: answers.preferOpenSource,
  };
}

export function slugifyStackId(name: string): string {
  const base = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 40);
  const ascii = base.replace(/[^a-z0-9-]/g, '') || 'my-stack';
  return `${ascii}-${Date.now().toString(36)}`;
}
