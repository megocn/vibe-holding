export type Theme = 'light' | 'dark';
export type Density = 'comfortable' | 'compact';

const THEME_KEY = 'vh-theme';
const DENSITY_KEY = 'vh-density';

export function initialTheme(): Theme {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'light' || saved === 'dark') return saved;
  return 'dark';
}

export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem(THEME_KEY, theme);
}

export function initialDensity(): Density {
  return localStorage.getItem(DENSITY_KEY) === 'compact' ? 'compact' : 'comfortable';
}

export function applyDensity(density: Density): void {
  document.documentElement.dataset.density = density;
  localStorage.setItem(DENSITY_KEY, density);
}
