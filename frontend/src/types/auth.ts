export type UserRole = 'creator' | 'brand' | 'admin';

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string | null;
  role: UserRole | string;
}
