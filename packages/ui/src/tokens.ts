/**
 * 设计令牌的 TS 镜像（供图谱着色 / 移动端等非 CSS 场景消费）。
 * 与 tokens.css 保持一致。
 */
export const colors = {
  light: {
    paper0: 'oklch(0.988 0.003 95)',
    paper1: 'oklch(0.972 0.004 92)',
    paper2: 'oklch(0.948 0.005 90)',
    ink1: 'oklch(0.28 0.012 55)',
    ink2: 'oklch(0.45 0.01 58)',
    ink3: 'oklch(0.58 0.008 62)',
    line: 'oklch(0.9 0.005 90)',
    primary: 'oklch(0.52 0.09 232)',
    info: 'oklch(0.56 0.08 230)',
    success: 'oklch(0.58 0.09 155)',
    warning: 'oklch(0.7 0.1 75)',
    danger: 'oklch(0.55 0.14 27)',
    seal: 'oklch(0.5 0.14 28)',
  },
  dark: {
    paper0: 'oklch(0.19 0.014 60)',
    paper1: 'oklch(0.23 0.014 60)',
    paper2: 'oklch(0.27 0.014 60)',
    ink1: 'oklch(0.93 0.01 88)',
    ink2: 'oklch(0.78 0.012 85)',
    ink3: 'oklch(0.62 0.012 80)',
    line: 'oklch(0.33 0.014 60)',
    primary: 'oklch(0.68 0.1 232)',
    info: 'oklch(0.7 0.09 230)',
    success: 'oklch(0.72 0.1 155)',
    warning: 'oklch(0.8 0.11 75)',
    danger: 'oklch(0.68 0.15 27)',
    seal: 'oklch(0.66 0.15 28)',
  },
} as const;

/** 字阶（px），与 tokens.css 一致 */
export const typeScale = {
  display: 32,
  h1: 24,
  h2: 20,
  h3: 18,
  body: 16,
  sm: 14,
  caption: 13,
} as const;

/** 关系四大分组的着色相（图谱边用），见设计规范 §6.3 */
export const relationGroupHue = {
  substitution: 'ink', // 替代
  composition: 'info', // 组合
  structure: 'primary', // 归属
  concept: 'warning', // 概念
} as const;

/** 可信度 -> 线型（图谱边） */
export const confidenceLineStyle = {
  verified: 'solid',
  community: 'dashed',
  inferred: 'dotted',
} as const;

export const space = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  6: 24,
  8: 32,
  12: 48,
  16: 64,
} as const;

export const radius = { sm: 6, base: 8, lg: 12, xl: 16, full: 9999 } as const;

export const motion = {
  fast: 120,
  base: 180,
  slow: 240,
  easeStandard: 'cubic-bezier(0.2, 0, 0, 1)',
} as const;

export const fonts = {
  display: "'LXGW ZhenKai', 'LXGW WenKai', system-ui, sans-serif",
  body: "'LXGW WenKai', system-ui, 'PingFang SC', sans-serif",
  mono: "'Maple Mono', 'JetBrains Mono', ui-monospace, monospace",
} as const;
