# Basic Component Testing

Базовые паттерны: рендер, `getByRole` / `queryByRole`, `toHaveClass`, `userEvent.click`, проверка disabled-состояния.

## Компонент: Button

```javascript
// Button.jsx
export const Button = ({
  children,
  variant = 'primary',
  disabled = false,
  onClick
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

## Тесты

```javascript
// Button.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button Component', () => {
  it('renders with children text', () => {
    render(<Button>Click Me</Button>);

    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('applies correct variant class', () => {
    render(<Button variant="secondary">Secondary</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-secondary');
  });

  it('applies primary variant by default', () => {
    render(<Button>Default</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-primary');
  });

  it('calls onClick handler when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<Button onClick={handleClick}>Click</Button>);

    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<Button onClick={handleClick} disabled>Disabled</Button>);

    const button = screen.getByRole('button');

    // Verify button is disabled
    expect(button).toBeDisabled();

    // Try to click - should not work
    await user.click(button);

    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

## Ключевые моменты

- Запросы по роли: `getByRole('button', { name: /click me/i })` — так же, как видит пользователь/скринридер.
- `userEvent.setup()` перед использованием, все взаимодействия — `await`.
- `toHaveClass`, `toBeDisabled`, `toHaveBeenCalledTimes` / `not.toHaveBeenCalled` — матчеры jest-dom.
- `queryByRole` используется для проверки отсутствия элемента (`not.toBeInTheDocument()`).
