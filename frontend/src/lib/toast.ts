import { toast, type ToastOptions } from 'react-toastify';

const defaultOptions: ToastOptions = {
  position: 'bottom-right',
  autoClose: 4000
};

export const notify = {
  success(message: string, options?: ToastOptions) {
    toast.success(message, { ...defaultOptions, ...options });
  },
  error(message: string, options?: ToastOptions) {
    toast.error(message, { ...defaultOptions, ...options });
  },
  info(message: string, options?: ToastOptions) {
    toast.info(message, { ...defaultOptions, ...options });
  }
};
