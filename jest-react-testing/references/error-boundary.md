# Error Boundary Testing

Паттерны: классовый ErrorBoundary (`getDerivedStateFromError`, `componentDidCatch`), fallback UI, callback `onError`.

## Компонент: ErrorBoundary

```javascript
// ErrorBoundary.jsx
import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div role="alert">
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Тесты

```javascript
// ErrorBoundary.test.jsx
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from './ErrorBoundary';

const ThrowError = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary Component', () => {
  // Suppress console.error for these tests
  const originalError = console.error;

  beforeAll(() => {
    console.error = jest.fn();
  });

  afterAll(() => {
    console.error = originalError;
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Child component</div>
      </ErrorBoundary>
    );

    expect(screen.getByText(/child component/i)).toBeInTheDocument();
  });

  it('renders error UI when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/test error/i)).toBeInTheDocument();
  });

  it('renders custom fallback', () => {
    const fallback = <div>Custom error message</div>;

    render(
      <ErrorBoundary fallback={fallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText(/custom error message/i)).toBeInTheDocument();
  });

  it('calls onError callback', () => {
    const handleError = jest.fn();

    render(
      <ErrorBoundary onError={handleError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(handleError).toHaveBeenCalled();
    expect(handleError.mock.calls[0][0]).toEqual(expect.any(Error));
  });
});
```

## Ключевые моменты

- Провоцирование ошибки: дочерний компонент `ThrowError`, который кидает Error при `shouldThrow`.
- Дефолтный fallback — `role="alert"` с текстом «Something went wrong» и сообщением ошибки.
- Кастомный fallback: проверка через проп `fallback`.
- `onError` callback: `toHaveBeenCalled()` + первый аргумент — `expect.any(Error)`.
- `console.error` мокается на `beforeAll`/`afterAll` — React логирует ошибки в консоль, тесты должны быть чистыми.
