import type { StackIssue, StackRecipe } from '@vh/core';

export function formatStackMarkdown(
  stack: Partial<StackRecipe>,
  opts: {
    resolveName: (id: string) => string;
    catName: (cat: string) => string;
    issues: StackIssue[];
    note?: string;
    rating?: number | null;
  },
): string {
  const lines: string[] = [];
  lines.push(`# ${stack.name ?? stack.id ?? '未命名技术栈'}`);
  if (stack.target) lines.push('', stack.target);
  if (opts.rating != null) lines.push('', `评分：${opts.rating}/5`);
  if (opts.note?.trim()) lines.push('', `备注：${opts.note.trim()}`);
  lines.push('', '## 层级');
  for (const [cat, id] of Object.entries(stack.layers ?? {})) {
    lines.push(`- **${opts.catName(cat)}**（\`${cat}\`）：${opts.resolveName(id)} (\`${id}\`)`);
  }
  if (stack.estimatedCost) lines.push('', `估算成本：${stack.estimatedCost}`);
  if (stack.rationaleMd) lines.push('', '## 选型理由', '', stack.rationaleMd);
  if (stack.caveats && stack.caveats.length > 0) {
    lines.push('', '## 注意事项');
    for (const c of stack.caveats) lines.push(`- ${c}`);
  }
  lines.push('', '## 校验');
  if (opts.issues.length === 0) {
    lines.push('- 通过 validateStack');
  } else {
    for (const i of opts.issues) {
      if (i.kind === 'conflict') {
        lines.push(
          `- 冲突：${opts.resolveName(i.a)} (\`${i.a}\`) ↔ ${opts.resolveName(i.b)} (\`${i.b}\`)`,
        );
      } else {
        lines.push(`- 供应商集中：\`${i.vendorId}\` ×${i.count}`);
      }
    }
  }
  lines.push('', '---', '_Exported from VibeHolding_');
  return lines.join('\n');
}

export function downloadJson(filename: string, data: unknown): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}
