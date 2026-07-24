/**
 * 从 @vh/core 的 Zod 定义导出 JSON Schema，供编辑器（VS Code 等）自动补全与实时校验。
 * 用法：pnpm gen:schema
 * 产物：content/schema/*.schema.json（由 .vscode/settings.json 的 json.schemas 关联到内容文件）。
 *
 * 单条目录（entries/edges/vendors/concepts/recipes）为「一条一文件」，schema 直接对应对象；
 * 根数组文件（categories.json / ranking-systems.json）导出为数组 schema。
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import process from 'node:process';
import { Category, Concept, Edge, Entry, RankingSystem, StackRecipe, Vendor } from '@vh/core';
import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';

const OUT_DIR = join(process.cwd(), 'content', 'schema');
mkdirSync(OUT_DIR, { recursive: true });

const targets: { file: string; name: string; schema: z.ZodTypeAny }[] = [
  { file: 'entry.schema.json', name: 'Entry', schema: Entry },
  { file: 'edge.schema.json', name: 'Edge', schema: Edge },
  { file: 'vendor.schema.json', name: 'Vendor', schema: Vendor },
  { file: 'concept.schema.json', name: 'Concept', schema: Concept },
  { file: 'recipe.schema.json', name: 'StackRecipe', schema: StackRecipe },
  { file: 'categories.schema.json', name: 'Categories', schema: z.array(Category) },
  {
    file: 'ranking-systems.schema.json',
    name: 'RankingSystems',
    schema: z.array(RankingSystem),
  },
];

for (const { file, name, schema } of targets) {
  const json = zodToJsonSchema(schema, { name, target: 'jsonSchema7' });
  writeFileSync(join(OUT_DIR, file), `${JSON.stringify(json, null, 2)}\n`, 'utf8');
  console.log(`✓ content/schema/${file}`);
}

console.log(`\n已生成 ${targets.length} 个 JSON Schema → content/schema/`);
