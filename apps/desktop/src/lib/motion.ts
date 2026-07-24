import type { Transition, Variants } from 'motion/react';
import { useReducedMotion } from 'motion/react';

/** 与 tokens `--dur-*` / `--ease-standard` 对齐（设计规范 §7 / §12） */
export const EASE_STANDARD = [0.2, 0, 0, 1] as const;
export const EASE_EMPHASIZED = [0.3, 0, 0, 1] as const;

export type MotionPace = 'fast' | 'std' | 'slow';

const DUR_MS: Record<MotionPace, number> = {
  fast: 120,
  std: 180,
  slow: 240,
};

export function transition(pace: MotionPace = 'std', reduced = false): Transition {
  if (reduced) return { duration: 0 };
  return {
    duration: DUR_MS[pace] / 1000,
    ease: EASE_STANDARD,
  };
}

/** 页面/面板进入：仅淡入（不用位移，以免 transform 困住内部 fixed/absolute 抽屉） */
export function fadeSlideVariants(reduced: boolean): Variants {
  if (reduced) {
    return {
      initial: { opacity: 1 },
      animate: { opacity: 1 },
      exit: { opacity: 1 },
    };
  }
  return {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  };
}

/** 弹出层（命令面板）：缩放 + 淡入 */
export function popVariants(reduced: boolean): Variants {
  if (reduced) {
    return {
      initial: { opacity: 1 },
      animate: { opacity: 1 },
      exit: { opacity: 1 },
    };
  }
  return {
    initial: { opacity: 0, scale: 0.97, y: -6 },
    animate: { opacity: 1, scale: 1, y: 0 },
    exit: { opacity: 0, scale: 0.98, y: -4 },
  };
}

export function backdropVariants(reduced: boolean): Variants {
  if (reduced) {
    return {
      initial: { opacity: 1 },
      animate: { opacity: 1 },
      exit: { opacity: 1 },
    };
  }
  return {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  };
}

/** 列表项错落入场 */
export function staggerItemVariants(reduced: boolean): Variants {
  if (reduced) {
    return {
      initial: { opacity: 1 },
      animate: { opacity: 1 },
    };
  }
  return {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
  };
}

export function useMotionPrefs() {
  const reduced = useReducedMotion() ?? false;
  return {
    reduced,
    tFast: transition('fast', reduced),
    tStd: transition('std', reduced),
    tSlow: transition('slow', reduced),
    fadeSlide: fadeSlideVariants(reduced),
    pop: popVariants(reduced),
    backdrop: backdropVariants(reduced),
    staggerItem: staggerItemVariants(reduced),
  };
}
