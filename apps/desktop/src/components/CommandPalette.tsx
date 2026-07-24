import { AnimatePresence, motion } from 'motion/react';
import {
  type KeyboardEvent as ReactKeyboardEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useMotionPrefs } from '../lib/motion.ts';
import { Icon } from './Icon.tsx';

export interface Command {
  id: string;
  label: string;
  icon: string;
  hint?: string;
  keywords?: string;
  run: () => void;
}

interface CommandPaletteProps {
  open: boolean;
  commands: Command[];
  onClose: () => void;
}

export function CommandPalette({ open, commands, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const { pop, backdrop, tFast, tStd } = useMotionPrefs();

  useEffect(() => {
    if (open) {
      setQuery('');
      setActive(0);
      inputRef.current?.focus();
    }
  }, [open]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q
      ? commands.filter((c) =>
          `${c.label} ${c.hint ?? ''} ${c.keywords ?? ''}`.toLowerCase().includes(q),
        )
      : commands;
    return list.slice(0, 50);
  }, [query, commands]);

  useEffect(() => {
    setActive((a) => Math.min(a, Math.max(0, filtered.length - 1)));
  }, [filtered.length]);

  function onKeyDown(e: ReactKeyboardEvent) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((a) => Math.min(a + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const cmd = filtered[active];
      if (cmd) {
        cmd.run();
        onClose();
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            paddingTop: '12vh',
            zIndex: 50,
          }}
        >
          <motion.button
            type="button"
            aria-label="关闭命令面板"
            onClick={onClose}
            variants={backdrop}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={tFast}
            style={{
              position: 'absolute',
              inset: 0,
              background: 'oklch(0.25 0.02 60 / 0.38)',
              border: 'none',
              cursor: 'default',
            }}
          />
          <motion.div
            className="vh-palette"
            variants={pop}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={tStd}
            onKeyDown={onKeyDown}
            style={{
              position: 'relative',
              width: 'min(620px, 92vw)',
            }}
          >
            <div
              className="flex items-center gap-2"
              style={{ padding: '12px 14px', borderBottom: '1px solid var(--line)' }}
            >
              <Icon name="MagnifyingGlass" size={18} color="var(--ink-3)" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="跳转条目、执行命令…"
                style={{
                  flex: 1,
                  border: 'none',
                  outline: 'none',
                  background: 'transparent',
                  color: 'var(--ink-1)',
                  fontFamily: 'var(--font-body)',
                  fontSize: 15,
                }}
              />
              <span className="vh-tag vh-mono">Esc</span>
            </div>
            <div style={{ maxHeight: '50vh', overflowY: 'auto', padding: 6 }}>
              {filtered.length === 0 && (
                <div className="vh-text-sm" style={{ padding: 16, color: 'var(--ink-3)' }}>
                  无匹配。换个词，或从分类栏另寻路径。
                </div>
              )}
              {filtered.map((cmd, i) => (
                <button
                  key={cmd.id}
                  type="button"
                  onMouseEnter={() => setActive(i)}
                  onClick={() => {
                    cmd.run();
                    onClose();
                  }}
                  className="flex items-center gap-3"
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    border: 'none',
                    cursor: 'pointer',
                    borderRadius: 'var(--radius)',
                    padding: '9px 10px',
                    background:
                      i === active
                        ? 'color-mix(in oklch, var(--pigment-primary) 10%, var(--paper-2))'
                        : 'transparent',
                    boxShadow:
                      i === active
                        ? 'inset 3px 0 0 var(--pigment-seal)'
                        : 'inset 3px 0 0 transparent',
                    color: 'var(--ink-1)',
                    fontFamily: 'var(--font-body)',
                    fontSize: 14,
                  }}
                >
                  <Icon name={cmd.icon} size={18} color="var(--ink-2)" />
                  <span style={{ flex: 1 }}>{cmd.label}</span>
                  {cmd.hint && (
                    <span className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)' }}>
                      {cmd.hint}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
