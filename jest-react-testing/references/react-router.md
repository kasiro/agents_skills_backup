# Testing with React Router

Паттерны: `MemoryRouter`, хелпер `renderWithRouter`, `Routes` + `Route`, `useNavigate`, `useLocation`, проверка `href` у ссылок.

## Компонент: Navigation

```javascript
// Navigation.jsx
import { Link, useNavigate, useLocation } from 'react-router-dom';

export const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleProfileClick = () => {
    navigate('/profile');
  };

  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/about">About</Link>
      <Link to="/products">Products</Link>
      <button onClick={handleProfileClick}>Profile</button>
      <span>Current: {location.pathname}</span>
    </nav>
  );
};
```

## Тесты

```javascript
// Navigation.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Navigation } from './Navigation';

const renderWithRouter = (ui, { initialEntries = ['/'] } = {}) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route path="*" element={ui} />
      </Routes>
    </MemoryRouter>
  );
};

describe('Navigation Component', () => {
  it('renders all navigation links', () => {
    renderWithRouter(<Navigation />);

    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /about/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /products/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /profile/i })).toBeInTheDocument();
  });

  it('displays current pathname', () => {
    renderWithRouter(<Navigation />, { initialEntries: ['/about'] });

    expect(screen.getByText(/current: \/about/i)).toBeInTheDocument();
  });

  it('has correct href attributes', () => {
    renderWithRouter(<Navigation />);

    expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: /about/i })).toHaveAttribute('href', '/about');
    expect(screen.getByRole('link', { name: /products/i })).toHaveAttribute('href', '/products');
  });
});
```

## Ключевые моменты

- Вместо `BrowserRouter` в тестах — `MemoryRouter` (без истории браузера).
- Хелпер `renderWithRouter(ui, { initialEntries })` — переиспользуемый boilerplate; `initialEntries` задаёт стартовый URL.
- `Route path="*"` — перехватывает любой путь, тестируемый UI рендерится внутри.
- `useLocation().pathname` — проверка текущего пути (`current: /about`).
- `toHaveAttribute('href', ...)` — проверка целевых адресов ссылок.
- Навигация по клику (navigate) — эмулируется `userEvent.click`, состояние роута проверяется через location.
