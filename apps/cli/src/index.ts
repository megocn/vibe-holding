import { Command } from 'commander';
import {
  registerAlt,
  registerIntel,
  registerRecipe,
  registerRelated,
  registerSearch,
  registerShow,
  registerStack,
} from './commands.ts';
import { getContext } from './context.ts';
import { fail, printJson, printLines } from './format.ts';

const program = new Command();

program.name('vh').description('VibeHolding CLI — 知识库查询与 stack 校验').version('0.0.0');

program
  .command('info')
  .description('显示内容库概况')
  .option('--json', 'JSON 输出', false)
  .action(async (opts: { json?: boolean }) => {
    const { contentDir, bundle } = await getContext();
    const summary = {
      contentDir,
      entries: bundle.entries.size,
      edges: bundle.edges.length,
      vendors: bundle.vendors.size,
      concepts: bundle.concepts.size,
      recipes: bundle.recipes.size,
      categories: bundle.categories.length,
    };
    if (opts.json) {
      printJson(summary);
      return;
    }
    printLines([
      `内容目录: ${summary.contentDir}`,
      `条目 ${summary.entries} · 边 ${summary.edges} · 厂商 ${summary.vendors} · 概念 ${summary.concepts}`,
      `方案 ${summary.recipes} · 分类 ${summary.categories}`,
    ]);
  });

registerSearch(program);
registerShow(program);
registerRelated(program);
registerAlt(program);
registerRecipe(program);
registerStack(program);
registerIntel(program);

program.parseAsync(process.argv).catch((e: unknown) => {
  fail(e instanceof Error ? e.message : String(e));
});
