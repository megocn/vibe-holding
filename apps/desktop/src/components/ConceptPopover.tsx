import type { Id } from '@vh/core';
import {
  type CSSProperties,
  type ReactNode,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import { createPortal } from 'react-dom';
import { useContent } from '../lib/content.tsx';

interface ConceptPopoverProps {
  conceptId: Id;
  children: ReactNode;
  /** 触发器额外 class（如 vh-tag / vh-concept-term） */
  className?: string;
  style?: CSSProperties;
  title?: string;
}

type Pos = { top: number; left: number; maxWidth: number };

export function ConceptPopover({
  conceptId,
  children,
  className,
  style,
  title,
}: ConceptPopoverProps) {
  const { bundle } = useContent();
  const concept = bundle.concepts.get(conceptId);
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState<Pos | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const labelId = useId();

  const updatePos = useCallback(() => {
    const el = triggerRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const pad = 8;
    const maxWidth = Math.min(320, window.innerWidth - pad * 2);
    let left = r.left;
    if (left + maxWidth > window.innerWidth - pad) {
      left = window.innerWidth - pad - maxWidth;
    }
    if (left < pad) left = pad;
    const below = r.bottom + pad;
    const estimatedH = 140;
    const top =
      below + estimatedH > window.innerHeight - pad
        ? Math.max(pad, r.top - pad - estimatedH)
        : below;
    setPos({ top, left, maxWidth });
  }, []);

  useLayoutEffect(() => {
    if (!open) return;
    updatePos();
  }, [open, updatePos]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    const onPointer = (e: PointerEvent) => {
      const t = e.target as Node;
      if (triggerRef.current?.contains(t) || panelRef.current?.contains(t)) return;
      setOpen(false);
    };
    const onScroll = () => updatePos();
    window.addEventListener('keydown', onKey);
    window.addEventListener('pointerdown', onPointer, true);
    window.addEventListener('resize', onScroll);
    window.addEventListener('scroll', onScroll, true);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('pointerdown', onPointer, true);
      window.removeEventListener('resize', onScroll);
      window.removeEventListener('scroll', onScroll, true);
    };
  }, [open, updatePos]);

  if (!concept) {
    return (
      <span className={className} style={style} title={title}>
        {children}
      </span>
    );
  }

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        className={className}
        style={{ cursor: 'pointer', ...style }}
        title={title ?? `解释：${concept.name}`}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={open ? labelId : undefined}
        onClick={() => setOpen((v) => !v)}
      >
        {children}
      </button>
      {open &&
        pos &&
        createPortal(
          <div
            ref={panelRef}
            id={labelId}
            role="dialog"
            aria-labelledby={`${labelId}-title`}
            className="vh-concept-pop"
            style={{ top: pos.top, left: pos.left, maxWidth: pos.maxWidth }}
          >
            <div className="vh-concept-pop-title" id={`${labelId}-title`}>
              {concept.name}
            </div>
            {concept.aliases.length > 0 && (
              <div className="vh-concept-pop-aliases">{concept.aliases.join(' · ')}</div>
            )}
            <div className="vh-concept-pop-body">{concept.summaryMd}</div>
          </div>,
          document.body,
        )}
    </>
  );
}
