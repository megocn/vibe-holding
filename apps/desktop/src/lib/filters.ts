import type { Maturity, PricingModel, Region } from '@vh/core';

export interface Filters {
  region?: Region;
  pricing?: PricingModel;
  maturity?: Maturity;
  chinaAccessible?: boolean;
}

export const REGION_LABELS: Record<Region, string> = {
  overseas: '国外',
  domestic: '国内',
  both: '国内外',
};

export const PRICING_LABELS: Record<PricingModel, string> = {
  free: '免费',
  freemium: '免费增值',
  subscription: '订阅',
  usage: '按量',
  'open-source': '开源',
};

export const MATURITY_LABELS: Record<Maturity, string> = {
  experimental: '实验',
  beta: '测试',
  stable: '稳定',
  mature: '成熟',
};
