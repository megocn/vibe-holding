import { ENTRY_UPDATES_DISPLAY_LIMIT, type EntryUpdate, type Id } from '@vh/core';
import { type FeedItem, UPDATE_TYPE_META } from '../lib/intel.ts';
import { Icon } from './Icon.tsx';

interface UpdatesTimelineProps {
  items: FeedItem[];
  onOpenEntry?: (id: Id) => void;
  /** 单条目详情内不展示条目名 */
  showEntryName?: boolean;
  emptyHint?: string;
  /** 截断提示（详情内超上限时） */
  truncatedHint?: string;
}

export function UpdatesTimeline({
  items,
  onOpenEntry,
  showEntryName = true,
  emptyHint = '暂无更新记录',
  truncatedHint,
}: UpdatesTimelineProps) {
  if (items.length === 0) {
    return (
      <div className="vh-text-sm" style={{ color: 'var(--ink-3)' }}>
        {emptyHint}
      </div>
    );
  }

  return (
    <div className="vh-timeline">
      {items.map((item) => (
        <TimelineRow
          key={`${item.entryId}-${item.update.date}-${item.update.summary}`}
          item={item}
          showEntryName={showEntryName}
          onOpenEntry={onOpenEntry}
        />
      ))}
      {truncatedHint && (
        <div className="vh-text-caption" style={{ color: 'var(--ink-3)', paddingLeft: 28 }}>
          {truncatedHint}
        </div>
      )}
    </div>
  );
}

/** 单条目 updates 数组 → 时间线（无条目名；默认截断至展示上限）。 */
export function EntryUpdatesList({
  updates,
  emptyHint,
  limit = ENTRY_UPDATES_DISPLAY_LIMIT,
}: {
  updates: EntryUpdate[];
  emptyHint?: string;
  limit?: number;
}) {
  const sorted = [...updates].sort((a, b) => b.date.localeCompare(a.date));
  const sliced = sorted.slice(0, limit);
  const items: FeedItem[] = sliced.map((update) => ({
    entryId: '_' as Id,
    entryName: '',
    update,
  }));
  const truncated =
    sorted.length > limit ? `仅展示最近 ${limit} 条（共 ${sorted.length}）` : undefined;
  return (
    <UpdatesTimeline
      items={items}
      showEntryName={false}
      emptyHint={emptyHint ?? '暂无更新'}
      truncatedHint={truncated}
    />
  );
}

function TimelineRow({
  item,
  showEntryName,
  onOpenEntry,
}: {
  item: FeedItem;
  showEntryName: boolean;
  onOpenEntry?: (id: Id) => void;
}) {
  const meta = UPDATE_TYPE_META[item.update.type] ?? UPDATE_TYPE_META.other;
  return (
    <div className="vh-timeline-row">
      <div className="vh-timeline-dot" style={{ color: meta.color }} title={meta.label}>
        <Icon name={meta.icon} size={14} weight="duotone" />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="flex flex-wrap items-center gap-2" style={{ marginBottom: 4 }}>
          <span className="vh-mono vh-text-caption" style={{ color: 'var(--ink-3)' }}>
            {item.update.date}
          </span>
          <span className="vh-tag" style={{ color: meta.color, borderColor: meta.color }}>
            {meta.label}
          </span>
          {item.update.version && (
            <span className="vh-mono vh-tag" style={{ color: 'var(--ink-2)' }}>
              {item.update.version}
            </span>
          )}
          {showEntryName &&
            (onOpenEntry ? (
              <button
                type="button"
                className="vh-link"
                style={{
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  padding: 0,
                  fontWeight: 500,
                  color: 'var(--ink-1)',
                  fontFamily: 'var(--font-body)',
                }}
                onClick={() => onOpenEntry(item.entryId)}
              >
                {item.entryName}
              </button>
            ) : (
              <span style={{ fontWeight: 500 }}>{item.entryName}</span>
            ))}
        </div>
        <div className="vh-text-sm" style={{ color: 'var(--ink-2)' }}>
          {item.update.summary}
        </div>
        {item.update.source && (
          <a
            href={item.update.source}
            target="_blank"
            rel="noreferrer"
            className="vh-link vh-text-caption"
            style={{ marginTop: 4, display: 'inline-block' }}
          >
            来源 ↗
          </a>
        )}
      </div>
    </div>
  );
}
