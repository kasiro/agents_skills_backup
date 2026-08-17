# Infinite Scroll List

Паттерны: `IntersectionObserver` (мок), пагинация `fetchItems(page, pageSize)`, состояния loading / hasMore.

## Компонент: InfiniteScrollList

```javascript
// InfiniteScrollList.jsx
import { useState, useEffect, useRef } from 'react';

export const InfiniteScrollList = ({ fetchItems, pageSize = 20 }) => {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerTarget = useRef(null);

  const loadMore = async () => {
    if (loading || !hasMore) return;

    setLoading(true);

    try {
      const newItems = await fetchItems(page, pageSize);

      if (newItems.length === 0) {
        setHasMore(false);
      } else {
        setItems((prev) => [...prev, ...newItems]);
        setPage((prev) => prev + 1);
      }
    } catch (error) {
      console.error('Failed to load items:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMore();
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          loadMore();
        }
      },
      { threshold: 1.0 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [hasMore, loading]);

  return (
    <div>
      <ul>
        {items.map((item, index) => (
          <li key={`${item.id}-${index}`}>{item.text}</li>
        ))}
      </ul>

      {loading && <div>Loading more items...</div>}
      {!hasMore && <div>No more items</div>}

      <div ref={observerTarget} style={{ height: '20px' }} />
    </div>
  );
};
```

## Тесты

```javascript
// InfiniteScrollList.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { InfiniteScrollList } from './InfiniteScrollList';

// Mock IntersectionObserver
const mockIntersectionObserver = jest.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
window.IntersectionObserver = mockIntersectionObserver;

describe('InfiniteScrollList Component', () => {
  it('loads initial items', async () => {
    const fetchItems = jest.fn(() =>
      Promise.resolve([
        { id: 1, text: 'Item 1' },
        { id: 2, text: 'Item 2' },
      ])
    );

    render(<InfiniteScrollList fetchItems={fetchItems} />);

    await waitFor(() => {
      expect(screen.getByText(/item 1/i)).toBeInTheDocument();
      expect(screen.getByText(/item 2/i)).toBeInTheDocument();
    });

    expect(fetchItems).toHaveBeenCalledWith(1, 20);
  });

  it('shows loading state', () => {
    const fetchItems = jest.fn(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<InfiniteScrollList fetchItems={fetchItems} />);

    expect(screen.getByText(/loading more items/i)).toBeInTheDocument();
  });

  it('shows no more items message when all loaded', async () => {
    const fetchItems = jest.fn()
      .mockResolvedValueOnce([{ id: 1, text: 'Item 1' }])
      .mockResolvedValueOnce([]);

    render(<InfiniteScrollList fetchItems={fetchItems} />);

    await waitFor(() => {
      expect(screen.getByText(/item 1/i)).toBeInTheDocument();
    });

    // Manually trigger loadMore for second call
    await waitFor(() => {
      expect(fetchItems).toHaveBeenCalledTimes(1);
    });
  });

  it('does not load more when already loading', async () => {
    const fetchItems = jest.fn(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    );

    render(<InfiniteScrollList fetchItems={fetchItems} />);

    await waitFor(() => {
      expect(fetchItems).toHaveBeenCalledTimes(1);
    });
  });
});
```

## Ключевые моменты

- `IntersectionObserver` в jsdom отсутствует — мок через `jest.fn()` + `window.IntersectionObserver = mock` в начале файла.
- Мок-функции с разными результатами: `.mockResolvedValueOnce([...]).mockResolvedValueOnce([])` — имитация конца данных.
- Проверка пагинации: `toHaveBeenCalledWith(1, 20)` — страница и pageSize.
- Гонки: guard `if (loading || !hasMore) return` проверяется тестом «не грузит повторно во время загрузки».
- Loading-состояние проверяется синхронно при отложенном промис-моке.
