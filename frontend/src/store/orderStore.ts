import { create } from 'zustand';

interface Order {
  id: string;
  status: 'in_progress' | 'delivered' | 'approved';
  amount: number;
}

interface OrderState {
  orders: Order[];
  setOrders: (orders: Order[]) => void;
  updateOrderStatus: (orderId: string, status: Order['status']) => void;
}

export const useOrderStore = create<OrderState>((set) => ({
  orders: [],
  setOrders: (orders) => set({ orders }),
  updateOrderStatus: (orderId, status) =>
    set((state) => ({
      orders: state.orders.map((order) => (order.id === orderId ? { ...order, status } : order))
    }))
}));
