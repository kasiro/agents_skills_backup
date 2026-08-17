# Testing with Redux

Паттерны: `Provider` + `configureStore`, хелперы `createMockStore` / `renderWithStore`, `preloadedState`, диспатч экшенов, `toHaveStyle`.

## Компонент: TodoList with Redux

```javascript
// TodoList.jsx
import { useSelector, useDispatch } from 'react-redux';
import { addTodo, toggleTodo, removeTodo } from './todosSlice';
import { useState } from 'react';

export const TodoList = () => {
  const [input, setInput] = useState('');
  const todos = useSelector((state) => state.todos.items);
  const dispatch = useDispatch();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      dispatch(addTodo(input));
      setInput('');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add todo"
        />
        <button type="submit">Add</button>
      </form>

      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => dispatch(toggleTodo(todo.id))}
              aria-label={`Toggle ${todo.text}`}
            />
            <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
              {todo.text}
            </span>
            <button
              onClick={() => dispatch(removeTodo(todo.id))}
              aria-label={`Remove ${todo.text}`}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

## Тесты

```javascript
// TodoList.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { TodoList } from './TodoList';
import todosReducer from './todosSlice';

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      todos: todosReducer,
    },
    preloadedState: initialState,
  });
};

const renderWithStore = (ui, { store = createMockStore() } = {}) => {
  return render(<Provider store={store}>{ui}</Provider>);
};

describe('TodoList with Redux', () => {
  it('adds new todo', async () => {
    const user = userEvent.setup();
    renderWithStore(<TodoList />);

    const input = screen.getByPlaceholderText(/add todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    await user.type(input, 'Buy groceries');
    await user.click(addButton);

    expect(screen.getByText(/buy groceries/i)).toBeInTheDocument();
  });

  it('toggles todo completion', async () => {
    const user = userEvent.setup();
    const initialState = {
      todos: {
        items: [{ id: 1, text: 'Test todo', completed: false }],
      },
    };

    renderWithStore(<TodoList />, { store: createMockStore(initialState) });

    const checkbox = screen.getByRole('checkbox', { name: /toggle test todo/i });
    const text = screen.getByText(/test todo/i);

    expect(checkbox).not.toBeChecked();
    expect(text).toHaveStyle({ textDecoration: 'none' });

    await user.click(checkbox);

    expect(checkbox).toBeChecked();
    expect(text).toHaveStyle({ textDecoration: 'line-through' });
  });

  it('removes todo', async () => {
    const user = userEvent.setup();
    const initialState = {
      todos: {
        items: [{ id: 1, text: 'Test todo', completed: false }],
      },
    };

    renderWithStore(<TodoList />, { store: createMockStore(initialState) });

    expect(screen.getByText(/test todo/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /remove test todo/i }));

    expect(screen.queryByText(/test todo/i)).not.toBeInTheDocument();
  });

  it('clears input after adding todo', async () => {
    const user = userEvent.setup();
    renderWithStore(<TodoList />);

    const input = screen.getByPlaceholderText(/add todo/i);

    await user.type(input, 'New todo');
    await user.click(screen.getByRole('button', { name: /add/i }));

    expect(input).toHaveValue('');
  });
});
```

## Ключевые моменты

- Реальный store через `configureStore` с реальным редьюсером — тесты на уровне интеграции, без моков диспатча.
- `preloadedState` — задаёт начальное состояние для сценариев (toggling/removing).
- Хелперы `createMockStore` / `renderWithStore` — переиспользуемый boilerplate.
- Чекбоксы: `getByRole('checkbox', { name: ... })`, `toBeChecked()`, стили — `toHaveStyle`.
- Вместо моков экшенов — проверка результата в UI (диспатч реальных экшенов в store).
- Асинхронные Redux-экшены (thunks) с сетью — комбинировать с MSW, см. [setup-msw.md](setup-msw.md).
