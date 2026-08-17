# User Authentication Flow

Паттерны: AuthProvider + useAuth (Context), login/logout, localStorage токена, MSW для POST /api/auth/login, обработка 401. Настройка MSW — см. [setup-msw.md](setup-msw.md).

## Компонент: AuthProvider & useAuth

```javascript
// AuthContext.jsx
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      setUser(data.user);
      localStorage.setItem('token', data.token);

      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

## Тесты

```javascript
// Auth.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { AuthProvider, useAuth } from './AuthContext';

const server = setupServer(
  rest.post('/api/auth/login', async (req, res, ctx) => {
    const { email, password } = await req.json();

    if (email === 'test@example.com' && password === 'password123') {
      return res(
        ctx.json({
          user: { id: 1, email: 'test@example.com', name: 'Test User' },
          token: 'fake-jwt-token',
        })
      );
    }

    return res(ctx.status(401), ctx.json({ message: 'Invalid credentials' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  localStorage.clear();
});
afterAll(() => server.close());

// Test component that uses useAuth
const TestComponent = () => {
  const { user, login, logout, loading, error } = useAuth();

  const handleLogin = async () => {
    await login('test@example.com', 'password123');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {user ? (
        <div>
          <p>Welcome, {user.name}</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <div>
          <p>Please log in</p>
          <button onClick={handleLogin}>Login</button>
        </div>
      )}
      {error && <div role="alert">{error}</div>}
    </div>
  );
};

describe('Authentication Flow', () => {
  it('logs in user successfully', async () => {
    const user = userEvent.setup();

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText(/please log in/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/welcome, test user/i)).toBeInTheDocument();
    });

    expect(localStorage.getItem('token')).toBe('fake-jwt-token');
  });

  it('logs out user', async () => {
    const user = userEvent.setup();

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Login first
    await user.click(screen.getByRole('button', { name: /login/i }));
    await screen.findByText(/welcome, test user/i);

    // Logout
    await user.click(screen.getByRole('button', { name: /logout/i }));

    expect(screen.getByText(/please log in/i)).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('shows error on failed login', async () => {
    const user = userEvent.setup();

    server.use(
      rest.post('/api/auth/login', (req, res, ctx) => {
        return res(ctx.status(401));
      })
    );

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByRole('button', { name: /login/i }));

    const errorMessage = await screen.findByRole('alert');
    expect(errorMessage).toHaveTextContent(/login failed/i);
  });
});
```

## Ключевые моменты

- Хук `useAuth` кидает ошибку вне `AuthProvider` — обёртка теста в Provider обязательна.
- Чистка `localStorage.clear()` в `afterEach` — изоляция между тестами.
- Успешный login: проверяем UI (`welcome, test user`) и токен в localStorage.
- Неудачный login: `server.use(...)` на 401 → `findByRole('alert')` с текстом ошибки.
- Тест-обёртка `TestComponent` рендерит состояние хука в DOM — стандартный приём для контекстных хуков.
