import { readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Plugin } from 'vite';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const aquaReportsDir = path.join(repoRoot, 'private/aqua/reports');

/**
 * 开发态抓取代理：绕过浏览器 CORS，供情报 RSS 抓取使用。
 * GET /__vh_fetch?url=<encoded>
 *
 * 活水 review 同步（仅本地）：
 * GET /__vh_aqua_review → 最新 private/aqua/reports/review-*.json
 */
export function vhFetchProxy(): Plugin {
  return {
    name: 'vh-fetch-proxy',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url?.startsWith('/__vh_aqua_review')) {
          void (async () => {
            try {
              const files = readdirSync(aquaReportsDir)
                .filter((f) => /^review-\d{4}-\d{2}-\d{2}\.json$/.test(f))
                .sort();
              const latest = files.at(-1);
              if (!latest) {
                res.statusCode = 404;
                res.setHeader('Content-Type', 'application/json; charset=utf-8');
                res.end(
                  JSON.stringify({
                    error: '未找到 review-*.json。先跑 pnpm aqua run --tier=daily',
                  }),
                );
                return;
              }
              const full = path.join(aquaReportsDir, latest);
              const drafts = JSON.parse(readFileSync(full, 'utf8')) as unknown;
              const count = Array.isArray(drafts) ? drafts.length : 0;
              res.statusCode = 200;
              res.setHeader('Content-Type', 'application/json; charset=utf-8');
              res.setHeader('Cache-Control', 'no-store');
              res.end(
                JSON.stringify({
                  file: `private/aqua/reports/${latest}`,
                  generatedAt: latest.slice('review-'.length, -'.json'.length),
                  count,
                  drafts,
                }),
              );
            } catch (err) {
              res.statusCode = 502;
              res.setHeader('Content-Type', 'application/json; charset=utf-8');
              res.end(
                JSON.stringify({
                  error: err instanceof Error ? err.message : String(err),
                }),
              );
            }
          })();
          return;
        }

        if (!req.url?.startsWith('/__vh_fetch')) {
          next();
          return;
        }

        void (async () => {
          try {
            const u = new URL(req.url ?? '', 'http://vh.local');
            const target = u.searchParams.get('url');
            if (!target) {
              res.statusCode = 400;
              res.end('missing url');
              return;
            }
            let parsed: URL;
            try {
              parsed = new URL(target);
            } catch {
              res.statusCode = 400;
              res.end('invalid url');
              return;
            }
            if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
              res.statusCode = 400;
              res.end('only http(s)');
              return;
            }

            const upstream = await fetch(parsed.toString(), {
              redirect: 'follow',
              headers: {
                Accept: 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*',
                'User-Agent': 'VibeHolding-Intel/0.1 (+local-dev-proxy)',
              },
            });
            const body = await upstream.text();
            res.statusCode = upstream.status;
            res.setHeader('Content-Type', upstream.headers.get('content-type') ?? 'text/plain');
            res.setHeader('Cache-Control', 'no-store');
            res.end(body);
          } catch (err) {
            res.statusCode = 502;
            res.end(err instanceof Error ? err.message : String(err));
          }
        })();
      });
    },
  };
}
