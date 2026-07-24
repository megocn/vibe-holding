const KEY = 'vh-recent';
const MAX = 20;

export function loadRecent(): string[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((x): x is string => typeof x === 'string').slice(0, MAX);
  } catch {
    return [];
  }
}

export function pushRecent(id: string): string[] {
  const prev = loadRecent().filter((x) => x !== id);
  const next = [id, ...prev].slice(0, MAX);
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

export function clearRecent(): void {
  localStorage.removeItem(KEY);
}
