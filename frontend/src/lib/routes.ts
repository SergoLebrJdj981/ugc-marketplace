export const DASHBOARD_ROUTES: Record<string, string> = {
  creator: '/creator',
  brand: '/brand',
  admin: '/admin',
  agent: '/agent',
  factory: '/factory'
};

export function resolveDashboardRoute(role?: string): string {
  if (!role) return '/';
  return DASHBOARD_ROUTES[role] ?? '/';
}
