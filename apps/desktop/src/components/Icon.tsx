import * as Phosphor from '@phosphor-icons/react';
import type { ComponentType } from 'react';

type IconWeight = 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';

interface IconProps {
  name: string;
  size?: number;
  weight?: IconWeight;
  color?: string;
}

const registry = Phosphor as unknown as Record<
  string,
  ComponentType<{ size?: number; weight?: IconWeight; color?: string }> | undefined
>;

export function Icon({ name, size = 20, weight = 'regular', color }: IconProps) {
  const Cmp = registry[name] ?? registry.Circle;
  if (!Cmp) return null;
  return <Cmp size={size} weight={weight} color={color} />;
}
