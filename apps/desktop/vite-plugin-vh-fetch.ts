import type { Plugin } from 'vite';

/**
 * 开发态抓取代理：绕过浏览器 CORS，供情报 RSS 抓取使用。
 * GET /__vh_fetch?url=<encoded>
 */
export function vhFetchProxy(): Plugin {
  return {
    name: 'vh-fetch-proxy',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
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
