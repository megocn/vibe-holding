/** CLI 输出：默认人类可读，`--json` 时机器可读。 */

export function printJson(data: unknown): void {
  process.stdout.write(`${JSON.stringify(data, null, 2)}\n`);
}

export function printLines(lines: string[]): void {
  process.stdout.write(`${lines.join('\n')}\n`);
}

export function fail(message: string, code = 1): never {
  process.stderr.write(`错误: ${message}\n`);
  process.exit(code);
}
