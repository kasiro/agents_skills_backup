# Async API Data Fetching

Паттерны: fetch-запросы в `useEffect`, состояния loading/error, `waitFor`, `findBy*`, MSW-моки, refetch при смене пропсов. Настройка MSW — см. [setup-msw.md](setup-msw.md).

## Компонент: UserProfile

```javascript
// UserProfile.jsx
import { useState, useEffect } from 'react';

export const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/users/${userId}`);

        if (!response.ok) {
          throw new Error('Failed to fetch user');
        }

        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  if (loading) {
    return <div>Loading user profile...</div>;
  }

  if (error) {
    return <div role="alert">Error: {error}</div>;
  }

  if (!user) {
    return <div>No user found</div>;
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <p>Email: {user.email}</p>
      <p>Role: {user.role}</p>
    </div>
  );
};
```

## Тесты с MSW

```javascript
// UserProfile.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { UserProfile } from './UserProfile';

const server = setupServer(
  rest.get('/api/users/:userId', (req, res, ctx) => {
    const { userId } = req.params;

    return res(
      ctx.json({
        id: userId,
        name: 'John Doe',
        email: 'john@example.com',
        role: 'Admin',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserProfile Component', () => {
  it('shows loading state initially', () => {
    render(<UserProfile userId="1" />);

    expect(screen.getByText(/loading user profile/i)).toBeInTheDocument();
  });

  it('displays user data after loading', async () => {
    render(<UserProfile userId="1" />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    expect(screen.getByRole('heading', { name: /john doe/i })).toBeInTheDocument();
    expect(screen.getByText(/email: john@example.com/i)).toBeInTheDocument();
    expect(screen.getByText(/role: admin/i)).toBeInTheDocument();
  });

  it('uses findBy for async elements', async () => {
    render(<UserProfile userId="1" />);

    // findBy automatically waits for element
    const heading = await screen.findByRole('heading', { name: /john doe/i });
    expect(heading).toBeInTheDocument();
  });

  it('displays error message on fetch failure', async () => {
    server.use(
      rest.get('/api/users/:userId', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<UserProfile userId="1" />);

    const errorMessage = await screen.findByRole('alert');
    expect(errorMessage).toHaveTextContent(/failed to fetch user/i);
  });

  it('refetches when userId changes', async () => {
    const { rerender } = render(<UserProfile userId="1" />);

    await screen.findByRole('heading', { name: /john doe/i });

    // Update server to return different user
    server.use(
      rest.get('/api/users/:userId', (req, res, ctx) => {
        return res(
          ctx.json({
            id: '2',
            name: 'Jane Smith',
            email: 'jane@example.com',
            role: 'User',
          })
        );
      })
    );

    rerender(<UserProfile userId="2" />);

    const newHeading = await screen.findByRole('heading', { name: /jane smith/i });
    expect(newHeading).toBeInTheDocument();
  });
});
```

## Ключевые моменты

- Loading-состояние проверяется синхронно (до завершения fetch), данные — асинхронно.
- `waitFor` — ждём, пока условие станет истинным (например, исчезнет loading).
- `findBy*` — асинхронная версия `getBy*`: сам ждёт появления элемента.
- Ошибка: `server.use(...)` переопределяет хендлер на 500 → проверяем `role="alert"`.
- Refetch: `rerender` с новым пропсом + обновлённый `server.use`.
- Параметры пути в MSW: `req.params` (см. setup-msw.md).
