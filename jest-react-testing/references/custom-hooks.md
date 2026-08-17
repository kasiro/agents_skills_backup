# Testing Custom Hooks

Паттерны: `renderHook`, `act`, `result.current`, `rerender` с `initialProps`.

## Hook: useLocalStorage

```javascript
// useLocalStorage.js
import { useState, useEffect } from 'react';

export const useLocalStorage = (key, initialValue) => {
  const [value, setValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  }, [key, value]);

  return [value, setValue];
};
```

## Тесты

```javascript
// useLocalStorage.test.js
import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from './useLocalStorage';

describe('useLocalStorage Hook', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns initial value when localStorage is empty', () => {
    const { result } = renderHook(() => useLocalStorage('testKey', 'initial'));

    expect(result.current[0]).toBe('initial');
  });

  it('returns value from localStorage if it exists', () => {
    localStorage.setItem('testKey', JSON.stringify('stored'));

    const { result } = renderHook(() => useLocalStorage('testKey', 'initial'));

    expect(result.current[0]).toBe('stored');
  });

  it('updates localStorage when value changes', () => {
    const { result } = renderHook(() => useLocalStorage('testKey', 'initial'));

    act(() => {
      result.current[1]('updated');
    });

    expect(localStorage.getItem('testKey')).toBe(JSON.stringify('updated'));
    expect(result.current[0]).toBe('updated');
  });

  it('handles objects', () => {
    const { result } = renderHook(() =>
      useLocalStorage('testKey', { name: 'John' })
    );

    act(() => {
      result.current[1]({ name: 'Jane', age: 30 });
    });

    expect(result.current[0]).toEqual({ name: 'Jane', age: 30 });
    expect(JSON.parse(localStorage.getItem('testKey'))).toEqual({
      name: 'Jane',
      age: 30,
    });
  });

  it('handles arrays', () => {
    const { result } = renderHook(() => useLocalStorage('todos', []));

    act(() => {
      result.current[1]([{ id: 1, text: 'Todo 1' }]);
    });

    expect(result.current[0]).toEqual([{ id: 1, text: 'Todo 1' }]);
  });

  it('updates when key changes', () => {
    localStorage.setItem('key1', JSON.stringify('value1'));
    localStorage.setItem('key2', JSON.stringify('value2'));

    const { result, rerender } = renderHook(
      ({ key }) => useLocalStorage(key, 'default'),
      { initialProps: { key: 'key1' } }
    );

    expect(result.current[0]).toBe('value1');

    rerender({ key: 'key2' });

    expect(result.current[0]).toBe('value2');
  });
});
```

## Ключевые моменты

- `renderHook(() => useLocalStorage(...))` — рендер хука без компонента.
- `result.current` — текущее возвращаемое значение хука (для пары `[value, setValue]` — индекс 0 и 1).
- Обновление состояния внутри `act()` — обязательная обёртка для setState.
- `rerender` с `initialProps` — проверка реакции на смену пропсов (здесь — смена `key`).
- `localStorage.clear()` в `beforeEach` — изоляция тестов.
- Хуки, требующие Provider (Redux/Context), тестируются обёрткой — см. [context-api.md](context-api.md) и [redux.md](redux.md).
