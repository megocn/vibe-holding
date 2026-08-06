import { describe, expect, it } from 'vitest';
import { Category, leavesOfSection, sectionIdOf } from './meta.ts';

const cats = [
  Category.parse({ id: 'ui-library', code: 'F', name: 'UI', kind: 'section', order: 6 }),
  Category.parse({
    id: 'ui-kits',
    name: '完整组件库',
    kind: 'leaf',
    parent: 'ui-library',
    order: 1,
  }),
  Category.parse({
    id: 'ui-icons',
    name: '图标库',
    kind: 'leaf',
    parent: 'ui-library',
    order: 2,
  }),
];

describe('category hierarchy', () => {
  it('sectionIdOf resolves leaf → section', () => {
    expect(sectionIdOf(cats, 'ui-icons')).toBe('ui-library');
    expect(sectionIdOf(cats, 'ui-library')).toBe('ui-library');
  });

  it('leavesOfSection lists ordered leaves', () => {
    expect(leavesOfSection(cats, 'ui-library').map((c) => c.id)).toEqual([
      'ui-kits',
      'ui-icons',
    ]);
  });

  it('leaf may carry usageMd; section rejects it', () => {
    expect(
      Category.parse({
        id: 'ui-icons',
        name: '图标库',
        kind: 'leaf',
        parent: 'ui-library',
        order: 2,
        usageMd: '界面定稿后统一上图标时用。\n\n要给应用装一套可检索的图标系统。\n\n选型后按组件体系引用，避免混用多套字重规范。',
      }).usageMd,
    ).toContain('图标');
    expect(() =>
      Category.parse({
        id: 'ui-library',
        code: 'F',
        name: 'UI',
        kind: 'section',
        order: 6,
        usageMd: '不该出现',
      }),
    ).toThrow(/usageMd/);
  });
});
