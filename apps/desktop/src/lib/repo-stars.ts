import { useEffect, useState } from 'react';

/** 墨台本仓（与 README / origin 一致）。 */
export const VH_GITHUB_REPO = 'megocn/vibe-holding';
export const VH_GITHUB_URL = `https://github.com/${VH_GITHUB_REPO}`;

const CACHE_KEY = 'vh:repo-stars';
const TTL_MS = 60 * 60 * 1000;

interface StarsCache {
  stars: number;
  fetchedAt: number;
}

function readCache(): StarsCache | null {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StarsCache;
    if (typeof parsed.stars !== 'number' || typeof parsed.fetchedAt !== 'number') return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeCache(stars: number): void {
  const payload: StarsCache = { stars, fetchedAt: Date.now() };
  localStorage.setItem(CACHE_KEY, JSON.stringify(payload));
}

/** 拉取本仓 stargazers_count；失败返回 null。 */
export async function fetchRepoStars(): Promise<number | null> {
  try {
    const res = await fetch(`https://api.github.com/repos/${VH_GITHUB_REPO}`, {
      headers: { Accept: 'application/vnd.github+json' },
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { stargazers_count?: number };
    return typeof data.stargazers_count === 'number' ? data.stargazers_count : null;
  } catch {
    return null;
  }
}

/** 千以上缩写为 1.2k / 12k。 */
export function formatStarCount(n: number): string {
  if (n < 1000) return String(n);
  if (n < 10_000) return `${(n / 1000).toFixed(1).replace(/\.0$/, '')}k`;
  return `${Math.round(n / 1000)}k`;
}

/** 先读缓存，过期则后台刷新。 */
export function useRepoStars(): number | null {
  const [stars, setStars] = useState<number | null>(() => readCache()?.stars ?? null);

  useEffect(() => {
    let cancelled = false;
    const cached = readCache();
    const fresh = cached != null && Date.now() - cached.fetchedAt < TTL_MS;
    if (fresh) {
      setStars(cached.stars);
      return;
    }

    void fetchRepoStars().then((n) => {
      if (cancelled || n == null) return;
      writeCache(n);
      setStars(n);
    });

    return () => {
      cancelled = true;
    };
  }, []);

  return stars;
}
