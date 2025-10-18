'use client';

export interface ModerationUser {
  id: string;
  email: string;
  full_name?: string | null;
  role: string;
  admin_level: string;
  is_active: boolean;
  status: 'active' | 'blocked';
  created_at?: string | null;
}

export interface ModerationCampaign {
  id: string;
  title: string;
  status: string;
  is_blocked: boolean;
  moderation_state: 'active' | 'blocked' | 'under_review';
  brand_id: string;
  brand_name?: string | null;
  created_at?: string | null;
}

export interface AdminActionLog {
  id: string;
  admin_id: string;
  target_id: string;
  action_type: string;
  description?: string | null;
  created_at?: string | null;
}
