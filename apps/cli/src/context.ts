import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  type ContentBundle,
  type GraphEngine,
  type SearchIndex,
  buildGraph,
  buildIndex,
} from '@vh/core';
import { loadContent } from '@vh/core/node';

export interface CliContext {
  contentDir: string;
  bundle: ContentBundle;
  graph: GraphEngine;
  index: SearchIndex;
}

function findDefaultContentDir(): string {
  if (process.env.VH_CONTENT_DIR) return resolve(process.env.VH_CONTENT_DIR);

  // apps/cli/src → 仓库根 content/
  const here = dirname(fileURLToPath(import.meta.url));
  const candidates = [
    join(here, '../../../content'),
    join(process.cwd(), 'content'),
    join(process.cwd(), '../content'),
  ];
  for (const c of candidates) {
    if (existsSync(join(c, 'categories.json'))) return resolve(c);
  }
  return resolve(join(here, '../../../content'));
}

let cached: CliContext | null = null;

export async function getContext(): Promise<CliContext> {
  if (cached) return cached;
  const contentDir = findDefaultContentDir();
  if (!existsSync(join(contentDir, 'categories.json'))) {
    throw new Error(
      `找不到内容目录（categories.json）。设置 VH_CONTENT_DIR 或在仓库根运行。尝试路径: ${contentDir}`,
    );
  }
  const bundle = await loadContent(contentDir);
  const graph = buildGraph(bundle);
  const index = buildIndex(bundle);
  cached = { contentDir, bundle, graph, index };
  return cached;
}

export function entryName(bundle: ContentBundle, id: string): string {
  return bundle.entries.get(id)?.name ?? bundle.concepts.get(id)?.name ?? id;
}
