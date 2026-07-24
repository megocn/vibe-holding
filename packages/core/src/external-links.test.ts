import { describe, expect, it } from 'vitest';
import { resolveExternalHref, resolveExternalLinks } from './external-links.ts';
import type { Entry } from './schema/entry.ts';

function base(partial: Partial<Entry> = {}): Entry {
  return {
    id: 'cursor',
    name: 'Cursor',
    category: 'coding-ide-agent',
    region: 'overseas',
    oneLiner: 'test',
    descriptionMd: '',
    officialUrl: 'https://cursor.com',
    pricing: { model: 'subscription' },
    availability: { chinaAccessible: true, needsCompany: false, needsIcp: false, regions: [] },
    tags: [],
    maturity: 'stable',
    tutorialLinks: [],
    externalLinks: [],
    pitfalls: [],
    updates: [],
    rankings: [],
    sources: [],
    lastReviewed: '2026-07-23',
    ...partial,
  };
}

describe('resolveExternalLinks', () => {
  it('always shows what_is and wiki via search when no override', () => {
    const links = resolveExternalLinks(base());
    expect(links.map((l) => l.kind)).toEqual(['what_is', 'wiki']);
    expect(links[0]!.curated).toBe(false);
    expect(links[0]!.href).toContain('bing.com');
    expect(links[0]!.href).toContain(encodeURIComponent('Cursor what is'));
    expect(links[1]!.href).toContain('en.wikipedia.org');
  });

  it('uses zh wiki and 是什么 for domestic region', () => {
    const links = resolveExternalLinks(base({ region: 'domestic', name: '通义灵码' }));
    expect(links[0]!.href).toContain(encodeURIComponent('通义灵码 是什么'));
    expect(links[1]!.href).toContain('zh.wikipedia.org');
  });

  it('prefers curated url over search', () => {
    const r = resolveExternalHref(
      base({
        externalLinks: [
          { kind: 'what_is', url: 'https://example.com/what-is-cursor', note: '精选科普' },
        ],
      }),
      'what_is',
    );
    expect(r).toMatchObject({
      curated: true,
      href: 'https://example.com/what-is-cursor',
      note: '精选科普',
    });
  });

  it('shows optional kinds from first-class fields', () => {
    const links = resolveExternalLinks(
      base({
        githubUrl: 'https://github.com/getcursor/cursor',
        changelogUrl: 'https://cursor.com/changelog',
        pricingUrl: 'https://cursor.com/pricing',
      }),
    );
    expect(links.map((l) => l.kind)).toEqual([
      'what_is',
      'wiki',
      'github',
      'pricing',
      'changelog',
    ]);
    expect(links.find((l) => l.kind === 'github')!.href).toBe(
      'https://github.com/getcursor/cursor',
    );
  });

  it('prefers externalLinks url over first-class field', () => {
    const r = resolveExternalHref(
      base({
        githubUrl: 'https://github.com/old/repo',
        externalLinks: [{ kind: 'github', url: 'https://github.com/new/repo' }],
      }),
      'github',
    );
    expect(r!.href).toBe('https://github.com/new/repo');
  });

  it('hides optional kinds without url', () => {
    expect(resolveExternalHref(base(), 'console')).toBeNull();
    expect(resolveExternalHref(base(), 'starter')).toBeNull();
  });
});
