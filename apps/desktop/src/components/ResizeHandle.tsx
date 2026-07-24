import { useCallback, useEffect, useRef } from 'react';

interface ResizeHandleProps {
  onResizeStart: () => void;
  /** 相对按下点的累计水平位移（正=向右）。 */
  onResize: (deltaX: number) => void;
  onResizeEnd?: () => void;
  title?: string;
}

/** 垂直分隔拖拽条。 */
export function ResizeHandle({
  onResizeStart,
  onResize,
  onResizeEnd,
  title = '拖拽调整宽度',
}: ResizeHandleProps) {
  const startX = useRef(0);
  const dragging = useRef(false);

  const onPointerMove = useCallback(
    (e: PointerEvent) => {
      if (!dragging.current) return;
      onResize(e.clientX - startX.current);
    },
    [onResize],
  );

  const onPointerUp = useCallback(() => {
    if (!dragging.current) return;
    dragging.current = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
    onResizeEnd?.();
  }, [onPointerMove, onResizeEnd]);

  useEffect(() => {
    return () => {
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
    };
  }, [onPointerMove, onPointerUp]);

  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      className="vh-resize"
      onPointerDown={(e) => {
        e.preventDefault();
        dragging.current = true;
        startX.current = e.clientX;
        onResizeStart();
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        window.addEventListener('pointermove', onPointerMove);
        window.addEventListener('pointerup', onPointerUp);
      }}
    />
  );
}
