# Accessibility Testing

Паттерны: доступная структура формы, `toHaveAccessibleName`, ARIA-атрибуты (`aria-required`, `aria-invalid`, `aria-describedby`, `aria-live`).

## Компонент: AccessibleForm

```javascript
// AccessibleForm.jsx
export const AccessibleForm = ({ onSubmit }) => {
  const [name, setName] = useState('');
  const [errors, setErrors] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!name) {
      setErrors({ name: 'Name is required' });
      return;
    }

    onSubmit({ name });
  };

  return (
    <form onSubmit={handleSubmit} aria-labelledby="form-title">
      <h2 id="form-title">User Information</h2>

      <div>
        <label htmlFor="name-input">
          Full Name <span aria-label="required">*</span>
        </label>
        <input
          id="name-input"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          aria-required="true"
          aria-invalid={errors.name ? 'true' : 'false'}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <div id="name-error" role="alert" aria-live="polite">
            {errors.name}
          </div>
        )}
      </div>

      <button type="submit" aria-label="Submit form">
        Submit
      </button>
    </form>
  );
};
```

## Тесты

```javascript
// AccessibleForm.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AccessibleForm } from './AccessibleForm';

describe('AccessibleForm - Accessibility', () => {
  it('has accessible form structure', () => {
    render(<AccessibleForm onSubmit={jest.fn()} />);

    const form = screen.getByRole('form');
    expect(form).toHaveAccessibleName('User Information');
  });

  it('has accessible form fields', () => {
    render(<AccessibleForm onSubmit={jest.fn()} />);

    const input = screen.getByLabelText(/full name/i);
    expect(input).toHaveAttribute('aria-required', 'true');
    expect(input).toHaveAttribute('id', 'name-input');
  });

  it('associates errors with input fields', async () => {
    const user = userEvent.setup();
    render(<AccessibleForm onSubmit={jest.fn()} />);

    await user.click(screen.getByRole('button', { name: /submit form/i }));

    const input = screen.getByLabelText(/full name/i);
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', 'name-error');

    const error = screen.getByRole('alert');
    expect(error).toHaveAttribute('id', 'name-error');
  });

  it('has accessible button', () => {
    render(<AccessibleForm onSubmit={jest.fn()} />);

    const button = screen.getByRole('button', { name: /submit form/i });
    expect(button).toHaveAttribute('type', 'submit');
  });

  it('announces errors to screen readers', async () => {
    const user = userEvent.setup();
    render(<AccessibleForm onSubmit={jest.fn()} />);

    await user.click(screen.getByRole('button'));

    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'polite');
    expect(alert).toHaveTextContent(/name is required/i);
  });
});
```

## Ключевые моменты

- `getByRole('form')` + `toHaveAccessibleName('User Information')` — имя формы из `aria-labelledby`.
- `getByLabelText(/full name/i)` — поиск поля по label.
- Связь ошибки с полем: `aria-invalid="true"` + `aria-describedby` → `id` элемента ошибки.
- Озвучка ошибок: `role="alert"` + `aria-live="polite"`.
- Доступная кнопка: `aria-label="Submit form"` + `type="submit"` (поиск по aria-имени).
- A11y-паттерны для модалок (aria-modal) — см. [modals.md](modals.md).
