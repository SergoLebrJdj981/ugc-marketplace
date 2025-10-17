import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import renderer from 'react-test-renderer';

import { Button } from '@/components/ui/Button';
import { ThemeSwitcher } from '@/components/ui/ThemeSwitcher';
import { ThemeProvider } from '@/context/theme-context';

describe('UI Components', () => {
  it('renders Button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('renders ThemeSwitcher inside ThemeProvider', () => {
    render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('toggles theme when ThemeSwitcher clicked', () => {
    render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );
    const button = screen.getByRole('button');
    const initialText = button.textContent;
    fireEvent.click(button);
    expect(button.textContent).not.toEqual(initialText);
  });

  it('Button snapshot matches', () => {
    const tree = renderer.create(<Button>Snapshot</Button>).toJSON();
    expect(tree).toMatchInlineSnapshot(`
<button
  className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 bg-brand text-white hover:bg-brand-dark focus-visible:ring-brand"
  type="button"
>
  Snapshot
</button>
`);
  });
});
