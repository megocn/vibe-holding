import { describe, expect, it } from 'vitest';
import { buildConceptTermRules, linkifyConcepts } from './concept-linkify.ts';

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
];

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

  it('buildConceptTermRules sorts by length desc', () => {
    const rules = buildConceptTermRules(concepts);
    for (let i = 1; i < rules.length; i++) {
      expect(rules[i - 1]!.term.length).toBeGreaterThanOrEqual(rules[i]!.term.length);
    }
  });
});
