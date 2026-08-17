# Testing with Context API

Паттерны: Provider + `useContext`, проверка значения и переключения, тест ошибки «хук вне провайдера».

## Компонент: Theme Context

```javascript
// ThemeContext.jsx
import { createContext, useContext, useState } from 'react';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemedButton = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      style={{
        backgroundColor: theme === 'light' ? '#fff' : '#333',
        color: theme === 'light' ? '#000' : '#fff',
      }}
    >
      Toggle Theme (Current: {theme})
    </button>
  );
};
```

## Тесты

```javascript
// ThemeContext.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, ThemedButton, useTheme } from './ThemeContext';

describe('Theme Context', () => {
  it('provides default theme', () => {
    render(
      <ThemeProvider>
        <ThemedButton />
      </ThemeProvider>
    );

    expect(screen.getByRole('button')).toHaveTextContent(/current: light/i);
  });

  it('toggles theme', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <ThemedButton />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');

    expect(button).toHaveTextContent(/current: light/i);
    expect(button).toHaveStyle({ backgroundColor: '#fff', color: '#000' });

    await user.click(button);

    expect(button).toHaveTextContent(/current: dark/i);
    expect(button).toHaveStyle({ backgroundColor: '#333', color: '#fff' });
  });

  it('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const InvalidComponent = () => {
      useTheme(); // Will throw
      return null;
    };

    expect(() => render(<InvalidComponent />)).toThrow(
      /useTheme must be used within ThemeProvider/i
    );

    spy.mockRestore();
  });
});
```

## Ключевые моменты

- Компонент, использующий контекст, оборачивается в Provider при рендере.
- `toHaveStyle({ backgroundColor: '#fff' })` — проверка стилей, зависящих от контекста.
- Ошибка «хук вне провайдера»: `expect(() => render(...)).toThrow(...)`.
- Подавление `console.error` через `jest.spyOn(console, 'error')` + `mockRestore()` — чтобы тест не был зашумлён.
- Тот же паттерн обёртки — для auth-контекста, см. [auth-flow.md](auth-flow.md).
