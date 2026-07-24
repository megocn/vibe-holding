import { describe, expect, it } from 'vitest';
import { feedItemToUpdate, guessUpdateType, parseFeedXml } from './rss.ts';

const RSS = `<?xml version="1.0"?>
<rss version="2.0"><channel>
<title>Demo</title>
<item>
  <title><![CDATA[July 2026 Security Release]]></title>
  <link>https://example.com/sec</link>
  <description>Patch notes</description>
  <pubDate>Mon, 20 Jul 2026 12:00:00 GMT</pubDate>
  <guid>sec-1</guid>
</item>
<item>
  <title>Pricing update for Hobby plan</title>
  <link>https://example.com/price</link>
  <pubDate>2026-07-01T00:00:00Z</pubDate>
</item>
</channel></rss>`;

const ATOM = `<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Vercel</title>
  <entry>
    <id>https://vercel.com/changelog/a</id>
    <title>AI Gateway streaming</title>
    <link href="https://vercel.com/changelog/a"/>
    <updated>2026-07-22T00:00:00.000Z</updated>
    <content type="xhtml"><div>Hello world feature</div></content>
  </entry>
</feed>`;

describe('parseFeedXml', () => {
  it('解析 RSS 2.0', () => {
    const items = parseFeedXml(RSS);
    expect(items).toHaveLength(2);
    expect(items[0]?.title).toBe('July 2026 Security Release');
    expect(items[0]?.link).toBe('https://example.com/sec');
    expect(items[0]?.date).toBe('2026-07-20');
  });

  it('解析 Atom', () => {
    const items = parseFeedXml(ATOM);
    expect(items).toHaveLength(1);
    expect(items[0]?.title).toContain('AI Gateway');
    expect(items[0]?.link).toContain('vercel.com');
    expect(items[0]?.date).toBe('2026-07-22');
  });
});

describe('guessUpdateType / feedItemToUpdate', () => {
  it('猜测类型', () => {
    expect(guessUpdateType('Pricing update')).toBe('pricing');
    expect(guessUpdateType('API deprecated')).toBe('deprecation');
    expect(guessUpdateType('Security Release')).toBe('policy');
    expect(guessUpdateType('New feature launch')).toBe('feature');
    expect(guessUpdateType('Next.js 15.0 released')).toBe('release');
  });

  it('映射为 EntryUpdate', () => {
    const u = feedItemToUpdate({
      title: 'Hello',
      link: 'https://example.com/x',
      date: '2026-07-01',
      summary: 'world',
    });
    expect(u.date).toBe('2026-07-01');
    expect(u.source).toBe('https://example.com/x');
    expect(u.summary).toContain('Hello');
  });

  it('抽取版本号', () => {
    const u = feedItemToUpdate({
      title: 'Next.js 15.1',
      link: 'https://nextjs.org/blog',
      date: '2026-06-01',
      summary: 'Turbopack GA',
    });
    expect(u.type).toBe('release');
    expect(u.version).toBe('15.1');
  });
});
