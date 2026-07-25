import { describe, expect, it } from 'vitest';
import {
  buildConceptTermRules,
  isLinkableTerm,
  linkifyConcepts,
} from './concept-linkify.ts';

const concepts = [
  {
    id: 'rag',
    name: 'RAG',
    aliases: ['Retrieval-Augmented Generation', '检索增强生成'],
  },
  {
    id: 'dependency-injection',
    name: 'dependency injection',
    aliases: ['DI', '依赖注入'],
  },
  {
    id: 'llm',
    name: 'LLM',
    aliases: ['大语言模型'],
  },
  {
    id: 'structured-output',
    name: 'structured output',
    aliases: ['结构化输出'],
  },
  {
    id: 'image',
    name: '容器镜像',
    aliases: ['Container Image', 'image', '镜像'],
  },
  {
    id: 'ecosystem',
    name: '技术生态',
    aliases: ['ecosystem', '生态'],
  },
  {
    id: 'workflow',
    name: 'workflow',
    aliases: ['工作流', 'Workflow'],
  },
  {
    id: 'function-calling',
    name: 'function calling',
    aliases: ['工具调用', '函数调用', 'tool calling'],
  },
  {
    id: 'text-to-image',
    name: '文生图',
    aliases: ['text-to-image', 'T2I'],
  },
  {
    id: 'agentic',
    name: 'agentic',
    aliases: ['Agentic'],
  },
  {
    id: 'open-source',
    name: 'open source',
    aliases: ['开源'],
  },
];

describe('isLinkableTerm', () => {
  it('denies ultra-generic short Chinese / bare image', () => {
    expect(isLinkableTerm('生态')).toBe(false);
    expect(isLinkableTerm('镜像')).toBe(false);
    expect(isLinkableTerm('image')).toBe(false);
    expect(isLinkableTerm('工作流')).toBe(false);
    expect(isLinkableTerm('托管')).toBe(false);
  });

  it('allows distinctive short Chinese and domain terms', () => {
    expect(isLinkableTerm('开源')).toBe(true);
    expect(isLinkableTerm('微调')).toBe(true);
    expect(isLinkableTerm('文生图')).toBe(true);
    expect(isLinkableTerm('工具调用')).toBe(true);
    expect(isLinkableTerm('RAG')).toBe(true);
    expect(isLinkableTerm('function calling')).toBe(true);
  });
});

describe('linkifyConcepts', () => {
  it('returns plain text when no match', () => {
    expect(linkifyConcepts('你好世界', concepts)).toEqual([
      { type: 'text', value: '你好世界' },
    ]);
  });

  it('matches aliases and longest first (DI vs dependency injection)', () => {
    const segs = linkifyConcepts(
      '用 dependency injection 或 DI 做 Agent',
      concepts,
    );
    expect(segs).toEqual([
      { type: 'text', value: '用 ' },
      {
        type: 'concept',
        value: 'dependency injection',
        conceptId: 'dependency-injection',
      },
      { type: 'text', value: ' 或 ' },
      { type: 'concept', value: 'DI', conceptId: 'dependency-injection' },
      { type: 'text', value: ' 做 Agent' },
    ]);
  });

  it('matches Chinese aliases literally', () => {
    const segs = linkifyConcepts('采用检索增强生成提升准确率', concepts);
    expect(segs).toEqual([
      { type: 'text', value: '采用' },
      { type: 'concept', value: '检索增强生成', conceptId: 'rag' },
      { type: 'text', value: '提升准确率' },
    ]);
  });

  it('uses word boundary for Latin acronyms', () => {
    const segs = linkifyConcepts('CALLM and LLM and XLLM', concepts);
    expect(segs).toEqual([
      { type: 'text', value: 'CALLM and ' },
      { type: 'concept', value: 'LLM', conceptId: 'llm' },
      { type: 'text', value: ' and XLLM' },
    ]);
  });

  it('prefers longer multi-word term over substring', () => {
    const segs = linkifyConcepts('需要可靠 structured output', concepts);
    expect(segs.some((s) => s.type === 'concept' && s.conceptId === 'structured-output')).toBe(
      true,
    );
  });

  it('does not link bare Image / 生态 / 工作流 in Muse Image prose', () => {
    const text =
      'Muse Image 是 Meta 推出的 agentic 文生图能力，强调工具调用；已在 Meta 生态观察图像工作流。';
    const segs = linkifyConcepts(text, concepts, undefined, {
      protectTexts: ['Muse Image'],
    });
    const hits = segs
      .filter((s): s is Extract<typeof s, { type: 'concept' }> => s.type === 'concept')
      .map((s) => s.conceptId);
    expect(hits).toContain('agentic');
    expect(hits).toContain('text-to-image');
    expect(hits).toContain('function-calling');
    expect(hits).not.toContain('image');
    expect(hits).not.toContain('ecosystem');
    expect(hits).not.toContain('workflow');
  });

  it('protectTexts blocks product-name spans even if term is linkable', () => {
    const segs = linkifyConcepts('Try Muse Image today', concepts, undefined, {
      protectTexts: ['Muse Image'],
    });
    expect(segs.every((s) => s.type === 'text')).toBe(true);
  });

  it('buildConceptTermRules skips denied terms', () => {
    const rules = buildConceptTermRules(concepts);
    const terms = new Set(rules.map((r) => r.term.toLowerCase()));
    expect(terms.has('生态')).toBe(false);
    expect(terms.has('image')).toBe(false);
    expect(terms.has('工作流')).toBe(false);
    expect(terms.has('文生图')).toBe(true);
    expect(terms.has('开源')).toBe(true);
  });

  it('buildConceptTermRules sorts by length desc', () => {
    const rules = buildConceptTermRules(concepts);
    for (let i = 1; i < rules.length; i++) {
      expect(rules[i - 1]!.term.length).toBeGreaterThanOrEqual(rules[i]!.term.length);
    }
  });
});
