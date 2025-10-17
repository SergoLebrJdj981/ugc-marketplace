'use client';

import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/Button';
import { useTheme } from '@/context';

export function ThemeSwitcher() {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <Button
      type="button"
      variant="outline"
      onClick={toggleTheme}
      className="gap-2"
      aria-label="Переключить тему"
    >
      {theme === 'light' ? '🌞 Светлая тема' : '🌜 Тёмная тема'}
    </Button>
  );
}
