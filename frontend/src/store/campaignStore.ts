import { create } from 'zustand';

interface Campaign {
  id: string;
  title: string;
  status: 'draft' | 'active' | 'paused';
  budget: number;
}

interface CampaignState {
  campaigns: Campaign[];
  setCampaigns: (campaigns: Campaign[]) => void;
  addCampaign: (campaign: Campaign) => void;
}

export const useCampaignStore = create<CampaignState>((set) => ({
  campaigns: [],
  setCampaigns: (campaigns) => set({ campaigns }),
  addCampaign: (campaign) =>
    set((state) => ({ campaigns: [...state.campaigns, campaign] }))
}));
