/**
 * 抓取外部客观流行度信号，产出 content/signals/popularity.json。
 *
 * 数据源（均为公开、可复现）：
 *  - GitHub 星标：api.github.com/repos/{owner}/{repo}（未鉴权 60 次/时；设 GITHUB_TOKEN 提额）
 *  - npm 近一月下载量：api.npmjs.org/downloads/point/last-month/{pkg}
 *  - 域名流行度：Tranco 榜（按 officialUrl 的注册域匹配，覆盖全部条目）
 *
 * 标识符来自：entry 的 githubUrl/officialUrl/docsUrl 自动推导 + content/signals/sources.json 种子。
 * 抓取失败/限流时保留旧快照值，绝不清空。
 *
 * 用法：
 *   pnpm gen:popularity                 # 全部来源
 *   pnpm gen:popularity --skip-tranco   # 跳过大列表下载
 *   pnpm gen:popularity --only=github
 */
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import process from 'node:process';

const ROOT = process.cwd();
const CONTENT = join(ROOT, 'content');
const ENTRIES_DIR = join(CONTENT, 'entries');
const SOURCES_FILE = join(CONTENT, 'signals', 'sources.json');
const OUT = join(CONTENT, 'signals', 'popularity.json');

const TODAY = new Date().toISOString().slice(0, 10);

const args = new Set(process.argv.slice(2));
const only = [...args].find((a) => a.startsWith('--only='))?.slice('--only='.length);
const wants = (src: string) => (only ? only === src : !args.has(`--skip-${src}`));

interface GithubSignal {
  repo: string;
  stars: number;
  asOf: string;
}
interface NpmSignal {
  pkg: string;
  downloads: number;
  asOf: string;
}
interface DomainSignal {
  domain: string;
  trancoRank: number;
  asOf: string;
}
interface PopularitySignal {
  github?: GithubSignal;
  npm?: NpmSignal;
  domain?: DomainSignal;
}
interface Snapshot {
  meta?: { generatedAt?: string; note?: string };
  entries: Record<string, PopularitySignal>;
}

interface EntryLite {
  id: string;
  officialUrl?: string;
  githubUrl?: string;
  docsUrl?: string;
}

function readEntries(): EntryLite[] {
  const files = readdirSync(ENTRIES_DIR).filter((f) => f.endsWith('.json'));
  return files.map((f) => JSON.parse(readFileSync(join(ENTRIES_DIR, f), 'utf8')) as EntryLite);
}

function readSeed(): Record<string, { github?: string; npm?: string }> {
  try {
    const raw = JSON.parse(readFileSync(SOURCES_FILE, 'utf8')) as {
      entries?: Record<string, { github?: string; npm?: string }>;
    };
    return raw.entries ?? {};
  } catch {
    return {};
  }
}

function readExisting(): Snapshot {
  try {
    return JSON.parse(readFileSync(OUT, 'utf8')) as Snapshot;
  } catch {
    return { entries: {} };
  }
}

/** 从 URL 抽取 owner/repo（github.com）。 */
function repoFromUrl(url: string | undefined): string | undefined {
  if (!url || !url.includes('github.com/')) return undefined;
  const m = url.match(/github\.com\/([^/]+)\/([^/#?]+)/);
  if (!m) return undefined;
  const repo = `${m[1]}/${m[2]}`.replace(/\.git$/, '');
  // 排除非仓库路径
  if (['sponsors', 'orgs', 'topics', 'features', 'about'].includes(m[1])) return undefined;
  return repo;
}

/** 代码/包托管等共享域：其 Tranco 排名代表平台本身而非产品，须排除。 */
const EXCLUDED_DOMAINS = new Set([
  'github.com',
  'gitlab.com',
  'bitbucket.org',
  'sourceforge.net',
  'npmjs.com',
  'pypi.org',
  'huggingface.co',
  'gitee.com',
  'readthedocs.io',
  'vercel.app',
  'netlify.app',
  'pages.dev',
  'notion.site',
  'gitbook.io',
]);

const TWO_PART_TLDS = new Set([
  'com.cn',
  'net.cn',
  'org.cn',
  'gov.cn',
  'com.hk',
  'com.tw',
  'co.uk',
  'co.jp',
  'com.au',
  'co.kr',
]);

/** hostname → 注册域（PLD），与 Tranco filterPLD 对齐。 */
function registrableDomain(url: string | undefined): string | undefined {
  if (!url) return undefined;
  let host: string;
  try {
    host = new URL(url).hostname.toLowerCase();
  } catch {
    return undefined;
  }
  host = host.replace(/^www\./, '');
  const parts = host.split('.');
  const lastTwo = parts.slice(-2).join('.');
  const lastThree = parts.slice(-3).join('.');
  const pld = parts.length <= 2 ? host : TWO_PART_TLDS.has(lastTwo) ? lastThree : lastTwo;
  return EXCLUDED_DOMAINS.has(pld) ? undefined : pld;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** 取（或初始化）某条目的信号对象。 */
function sigOf(out: Snapshot, id: string): PopularitySignal {
  let sig = out.entries[id];
  if (!sig) {
    sig = {};
    out.entries[id] = sig;
  }
  return sig;
}

async function fetchGithubStars(
  repos: Map<string, string>, // entryId -> repo
  out: Snapshot,
): Promise<void> {
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  const headers: Record<string, string> = {
    Accept: 'application/vnd.github+json',
    'User-Agent': 'vibeholding-popularity',
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let ok = 0;
  let fail = 0;
  const uniqueRepos = [...new Set(repos.values())];
  console.log(
    `  GitHub：${repos.size} 条目 / ${uniqueRepos.length} 仓库${token ? '（已鉴权）' : '（未鉴权，限 60 次/时）'}`,
  );
  const starByRepo = new Map<string, number>();

  for (const repo of uniqueRepos) {
    try {
      const res = await fetch(`https://api.github.com/repos/${repo}`, { headers });
      if (res.status === 403 || res.status === 429) {
        console.warn(`  ⚠ GitHub 限流（${res.status}），停止抓取，保留旧值。`);
        break;
      }
      if (!res.ok) {
        fail++;
        continue;
      }
      const data = (await res.json()) as { stargazers_count?: number };
      if (typeof data.stargazers_count === 'number') {
        starByRepo.set(repo, data.stargazers_count);
        ok++;
      }
    } catch {
      fail++;
    }
    if (!token) await sleep(1200);
  }

  for (const [id, repo] of repos) {
    const stars = starByRepo.get(repo);
    if (stars == null) continue;
    sigOf(out, id).github = { repo, stars, asOf: TODAY };
  }
  console.log(`  GitHub：成功 ${ok} / 失败 ${fail}`);
}

async function fetchNpmDownloads(pkgs: Map<string, string>, out: Snapshot): Promise<void> {
  let ok = 0;
  console.log(`  npm：${pkgs.size} 包`);
  for (const [id, pkg] of pkgs) {
    try {
      const res = await fetch(
        `https://api.npmjs.org/downloads/point/last-month/${encodeURIComponent(pkg)}`,
      );
      if (!res.ok) continue;
      const data = (await res.json()) as { downloads?: number };
      if (typeof data.downloads === 'number' && data.downloads > 0) {
        sigOf(out, id).npm = { pkg, downloads: data.downloads, asOf: TODAY };
        ok++;
      }
    } catch {
      // 忽略单包失败
    }
  }
  console.log(`  npm：成功 ${ok}`);
}

async function fetchTranco(domains: Map<string, string>, out: Snapshot): Promise<void> {
  console.log(`  Tranco：${new Set(domains.values()).size} 个域名待匹配，下载最新榜…`);
  let listUrl: string;
  try {
    const meta = (await (await fetch('https://tranco-list.eu/api/lists/date/latest')).json()) as {
      download?: string;
      list_id?: string;
    };
    listUrl = meta.download ?? `https://tranco-list.eu/download/${meta.list_id}/1000000`;
  } catch (e) {
    console.warn(`  ⚠ 取 Tranco 榜地址失败，跳过：${String(e)}`);
    return;
  }

  let csv: string | undefined;
  for (let attempt = 1; attempt <= 3 && csv == null; attempt++) {
    try {
      const res = await fetch(listUrl, { signal: AbortSignal.timeout(120_000) });
      if (!res.ok) {
        console.warn(`  ⚠ Tranco 下载失败 HTTP ${res.status}（第 ${attempt} 次）`);
        await sleep(2000);
        continue;
      }
      csv = await res.text();
    } catch (e) {
      console.warn(`  ⚠ Tranco 下载异常（第 ${attempt} 次）：${String(e)}`);
      await sleep(2000);
    }
  }
  if (csv == null) {
    console.warn('  ⚠ Tranco 三次均失败，保留旧域名值，跳过。');
    return;
  }

  const wanted = new Set(domains.values());
  const rankByDomain = new Map<string, number>();
  for (const line of csv.split('\n')) {
    const comma = line.indexOf(',');
    if (comma < 0) continue;
    const domain = line.slice(comma + 1).trim();
    if (!wanted.has(domain)) continue;
    const rank = Number.parseInt(line.slice(0, comma), 10);
    if (Number.isFinite(rank) && !rankByDomain.has(domain)) rankByDomain.set(domain, rank);
    if (rankByDomain.size === wanted.size) break;
  }

  let ok = 0;
  for (const [id, domain] of domains) {
    const rank = rankByDomain.get(domain);
    if (rank == null) continue;
    sigOf(out, id).domain = { domain, trancoRank: rank, asOf: TODAY };
    ok++;
  }
  console.log(`  Tranco：匹配 ${ok} / ${domains.size}`);
}

async function main(): Promise<void> {
  const entries = readEntries();
  const seed = readSeed();
  const out = readExisting();

  const repos = new Map<string, string>();
  const pkgs = new Map<string, string>();
  const domains = new Map<string, string>();

  for (const e of entries) {
    const seeded = seed[e.id];
    const repo =
      seeded?.github ??
      repoFromUrl(e.githubUrl) ??
      repoFromUrl(e.officialUrl) ??
      repoFromUrl(e.docsUrl);
    if (repo) repos.set(e.id, repo);
    if (seeded?.npm) pkgs.set(e.id, seeded.npm);
    const domain = registrableDomain(e.officialUrl);
    if (domain) domains.set(e.id, domain);
  }

  // 共享域名（多个条目落在同一注册域，如 *.amazon.com / *.google.com）无法区分产品，
  // 其 Tranco 排名代表母品牌而非单品 → 丢弃，避免云大厂子产品被母域名顶上去。
  const domainUsers = new Map<string, number>();
  for (const d of domains.values()) domainUsers.set(d, (domainUsers.get(d) ?? 0) + 1);
  for (const [id, d] of [...domains]) {
    if ((domainUsers.get(d) ?? 0) > 1) domains.delete(id);
  }

  console.log(
    `外部信号抓取：条目 ${entries.length} · github ${repos.size} · npm ${pkgs.size} · 域名 ${domains.size}`,
  );

  // 清除不再适用的旧域名信号（如被排除的托管域）
  for (const [id, sig] of Object.entries(out.entries)) {
    if (sig.domain && domains.get(id) !== sig.domain.domain) sig.domain = undefined;
  }

  if (wants('github')) await fetchGithubStars(repos, out);
  if (wants('npm')) await fetchNpmDownloads(pkgs, out);
  if (wants('tranco')) await fetchTranco(domains, out);

  // 清理：丢弃已删除条目、以及清空后的空信号；稳定按 id 排序
  const validIds = new Set(entries.map((e) => e.id));
  const cleaned: Snapshot = {
    meta: {
      generatedAt: TODAY,
      note: '外部客观流行度快照，由 scripts/fetch-popularity.ts 生成；请勿手工编辑。',
    },
    entries: {},
  };
  for (const id of Object.keys(out.entries).sort()) {
    if (!validIds.has(id)) continue;
    const src = out.entries[id];
    if (!src) continue;
    const next: PopularitySignal = {};
    if (src.github) next.github = src.github;
    if (src.npm) next.npm = src.npm;
    if (src.domain) next.domain = src.domain;
    if (next.github || next.npm || next.domain) cleaned.entries[id] = next;
  }

  mkdirSync(dirname(OUT), { recursive: true });
  writeFileSync(OUT, `${JSON.stringify(cleaned, null, 2)}\n`, 'utf8');
  const withSig = Object.keys(cleaned.entries).length;
  console.log(`已写入 ${OUT}\n  有信号条目 ${withSig} / ${entries.length}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
