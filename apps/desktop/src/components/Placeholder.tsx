import { EmptyState } from './EmptyState.tsx';

export function Placeholder({ icon, title }: { icon: string; title: string }) {
  return (
    <EmptyState
      icon={icon}
      title={title}
      hint="此卷尚在装裱。可先从知识库与图谱游历，或用 ⌘K 直达已备好的航路。"
    />
  );
}
