import { AnimatePresence, motion } from 'motion/react';
import type { ReactNode } from 'react';
import { useMotionPrefs } from '../lib/motion.ts';

/** 主内容区视图切换：淡入微移，尊重 reduced-motion */
export function PageFade({ viewKey, children }: { viewKey: string; children: ReactNode }) {
  const { fadeSlide, tStd } = useMotionPrefs();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={viewKey}
        variants={fadeSlide}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={tStd}
        style={{
          position: 'relative',
          flex: 1,
          alignSelf: 'stretch',
          minHeight: 0,
          minWidth: 0,
          maxWidth: '100%',
          display: 'flex',
          flexDirection: 'row',
          /* 避免 transform 困住抽屉的 fixed/absolute 定位 */
          transform: 'none',
          overflowX: 'clip',
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
