import type { Edge, EdgeType, Id } from '@vh/core';
import { Edge as EdgeSchema, isSymmetric } from '@vh/core';

export interface EdgeValidationIssue {
  code: string;
  path?: string;
  message: string;
}

/**
 * 客户端边校验（对齐 SPEC §6 / validate-content 边相关规则）。
 * `existing` 为合并后的全部边；`editingId` 为正在编辑的边（排除自身重复检测）。
 */
export function validateEdgeDraft(
  candidate: unknown,
  opts: {
    nodeIds: Set<string>;
    existing: Edge[];
    editingId?: string | null;
  },
): { ok: true; edge: Edge } | { ok: false; issues: EdgeValidationIssue[] } {
  const issues: EdgeValidationIssue[] = [];
  const parsed = EdgeSchema.safeParse(candidate);
  if (!parsed.success) {
    for (const issue of parsed.error.issues) {
      issues.push({
        code: 'E_SCHEMA',
        path: issue.path.join('.') || undefined,
        message: issue.message,
      });
    }
    return { ok: false, issues };
  }
  const edge = parsed.data;
  const { nodeIds, existing, editingId } = opts;

  if (!nodeIds.has(edge.from))
    issues.push({ code: 'E_REF', path: 'from', message: `from "${edge.from}" 不存在` });
  if (!nodeIds.has(edge.to))
    issues.push({ code: 'E_REF', path: 'to', message: `to "${edge.to}" 不存在` });
  if (edge.from === edge.to)
    issues.push({ code: 'E_SELF_LOOP', path: 'to', message: '边不能为自环' });

  const others = existing.filter((e) => e.id !== editingId && e.id !== edge.id);

  if (others.some((e) => e.id === edge.id) && editingId !== edge.id) {
    issues.push({ code: 'E_DUP_ID', path: 'id', message: `边 id "${edge.id}" 已存在` });
  }

  const exact = `${edge.from}|${edge.type}|${edge.to}`;
  if (others.some((e) => `${e.from}|${e.type}|${e.to}` === exact)) {
    issues.push({ code: 'E_DUP_EDGE', message: `已存在相同方向与类型的边 ${exact}` });
  }

  if (isSymmetric(edge.type)) {
    const sortedPair = [edge.from, edge.to].sort().join('~');
    const dupSym = others.some(
      (e) => e.type === edge.type && [e.from, e.to].sort().join('~') === sortedPair,
    );
    if (dupSym) {
      issues.push({
        code: 'E_DUP_SYM',
        message: `对称边 ${edge.type} (${sortedPair}) 已存在`,
      });
    }
  }

  // conflicts_with ↔ commonly_used_with 互斥
  if (edge.type === 'conflicts_with' || edge.type === 'commonly_used_with') {
    const sortedPair = [edge.from, edge.to].sort().join('~');
    const opposite: EdgeType =
      edge.type === 'conflicts_with' ? 'commonly_used_with' : 'conflicts_with';
    const clash = others.some(
      (e) => e.type === opposite && [e.from, e.to].sort().join('~') === sortedPair,
    );
    if (clash) {
      issues.push({
        code: 'E_CONFLICT_PARADOX',
        path: 'type',
        message: `节点对 ${sortedPair} 不可同时存在 conflicts_with 与 commonly_used_with`,
      });
    }
  }

  if (issues.length) return { ok: false, issues };
  return { ok: true, edge };
}

export function newEdgeId(from: Id, to: Id, type: string): string {
  const slug = `e-${from}-${type.replace(/_/g, '-')}-${to}`.toLowerCase();
  return slug.replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-');
}

export { todayIso } from './intel.ts';
