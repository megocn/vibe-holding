import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import type { z } from 'zod';
import { Edge } from './schema/edge.ts';
import { Entry } from './schema/entry.ts';
import { Category, Concept, Vendor } from './schema/meta.ts';
import { RankingSystem } from './schema/ranking.ts';
import { StackRecipe } from './schema/recipe.ts';
import type { ContentBundle } from './types.ts';

async function readJsonDir<S extends z.ZodTypeAny>(dir: string, schema: S): Promise<z.output<S>[]> {
  let files: string[];
  try {
    files = (await readdir(dir)).filter((f) => f.endsWith('.json'));
  } catch {
    return [];
  }
  const out: z.output<S>[] = [];
  for (const file of files) {
    const raw = await readFile(join(dir, file), 'utf8');
    const data = JSON.parse(raw);
    const arr = Array.isArray(data) ? data : [data];
    for (const item of arr) {
      out.push(schema.parse(item));
    }
  }
  return out;
}

/**
 * 从内容目录加载并校验为 ContentBundle。
 * 目录结构见 SPEC §4：entries/ edges/ vendors/ concepts/ recipes/ categories.json / ranking-systems.json
 */
export async function loadContent(dir: string): Promise<ContentBundle> {
  const [entries, edges, vendors, concepts, recipes] = await Promise.all([
    readJsonDir(join(dir, 'entries'), Entry),
    readJsonDir(join(dir, 'edges'), Edge),
    readJsonDir(join(dir, 'vendors'), Vendor),
    readJsonDir(join(dir, 'concepts'), Concept),
    readJsonDir(join(dir, 'recipes'), StackRecipe),
  ]);

  let categories: Category[] = [];
  try {
    const raw = await readFile(join(dir, 'categories.json'), 'utf8');
    categories = (JSON.parse(raw) as unknown[]).map((c) => Category.parse(c));
  } catch {
    categories = [];
  }

  let rankingSystems: RankingSystem[] = [];
  try {
    const raw = await readFile(join(dir, 'ranking-systems.json'), 'utf8');
    rankingSystems = (JSON.parse(raw) as unknown[]).map((r) => RankingSystem.parse(r));
  } catch {
    rankingSystems = [];
  }

  return {
    entries: new Map(entries.map((e) => [e.id, e])),
    edges,
    vendors: new Map(vendors.map((v) => [v.id, v])),
    categories,
    concepts: new Map(concepts.map((c) => [c.id, c])),
    recipes: new Map(recipes.map((r) => [r.id, r])),
    rankingSystems: new Map(rankingSystems.map((r) => [r.id, r])),
  };
}
