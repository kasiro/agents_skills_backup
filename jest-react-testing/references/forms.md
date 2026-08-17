# Form Testing with Validation

Паттерны: `getByLabelText`, `user.type`, submit с валидацией, `aria-invalid` / `aria-describedby`, очистка полей после сабмита.

## Компонент: LoginForm

```javascript
// LoginForm.jsx
import { useState } from 'react';

export const LoginForm = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const newErrors = validate();

    if (Object.keys(newErrors).length === 0) {
      onSubmit({ email, password });
      setEmail('');
      setPassword('');
    } else {
      setErrors(newErrors);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <span id="email-error" role="alert">
            {errors.email}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-invalid={errors.password ? 'true' : 'false'}
          aria-describedby={errors.password ? 'password-error' : undefined}
        />
        {errors.password && (
          <span id="password-error" role="alert">
            {errors.password}
          </span>
        )}
      </div>

      <button type="submit">Login</button>
    </form>
  );
};
```

## Тесты

```javascript
// LoginForm.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm Component', () => {
  it('renders form fields', () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn();

    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    });
  });

  it('shows validation error for empty email', async () => {
    const user = userEvent.setup();

    render(<LoginForm onSubmit={jest.fn()} />);

    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  });

  it('shows validation error for invalid email format', async () => {
    const user = userEvent.setup();

    render(<LoginForm onSubmit={jest.fn()} />);

    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(screen.getByText(/email is invalid/i)).toBeInTheDocument();
  });

  it('shows validation error for short password', async () => {
    const user = userEvent.setup();

    render(<LoginForm onSubmit={jest.fn()} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'short');
    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
  });

  it('clears form after successful submission', async () => {
    const user = userEvent.setup();

    render(<LoginForm onSubmit={jest.fn()} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(emailInput).toHaveValue('');
    expect(passwordInput).toHaveValue('');
  });
});
```

## Ключевые моменты

- Ввод текста: `await user.type(screen.getByLabelText(/email/i), '...')`.
- Валидация ошибок: ошибки рендерятся с `role="alert"` → проверка `getByText`.
- Проверка вызова onSubmit с данными: `toHaveBeenCalledWith({ email, password })`.
- `toHaveValue('')` — проверка очистки поля после успешного сабмита.
- Многошаговые формы (wizard) — см. [multi-step-form.md](multi-step-form.md).
