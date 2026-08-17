# MSW (Mock Service Worker) — настройка и паттерны

Базовый boilerplate для мокирования HTTP-запросов в Jest через MSW. Используется в [async-fetching.md](async-fetching.md) и [auth-flow.md](auth-flow.md).

## Установка

```bash
npm install -D msw
# для node-среды (Jest): моки работают через setupServer из msw/node
```

## Стандартный скелет

```javascript
import { rest } from 'msw';
import { setupServer } from 'msw/node';

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
```

## Ключевые приёмы

- `server.listen()` — включить моки перед всеми тестами.
- `server.resetHandlers()` — сбросить переопределения `server.use()` после каждого теста.
- `server.close()` — выключить моки после всех тестов.
- `server.use(handler)` — временно переопределить хендлер для конкретного теста (например, вернуть ошибку):

```javascript
server.use(
  rest.get('/api/users/:userId', (req, res, ctx) => {
    return res(ctx.status(500));
  })
);
```

- Параметры пути: `req.params` (например, `userId` для `/api/users/:userId`).
- Тело POST-запроса: `await req.json()`.
- Ответ: `res(ctx.json(...))` или `res(ctx.status(code), ctx.json({ message }))`.

## POST-хендлер с валидацией (из auth-flow)

```javascript
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
  localStorage.clear(); // чистим localStorage в тестах с авторизацией
});
afterAll(() => server.close());
```

## Сопутствующие инструменты

- **WebSocket**: для мокирования WS используется `jest-websocket-mock`, а не MSW — см. [websockets.md](websockets.md).
- **Проверка отсутствия async-элементов**: `waitFor` / `findBy*` — см. [async-fetching.md](async-fetching.md).
