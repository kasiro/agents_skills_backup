---
name: jest-react-testing
description: |-
  Comprehensive collection of real-world Jest testing examples for React. Covers component testing, forms, async data, hooks, routing, Redux, Context API, accessibility, timers, WebSockets, and multi-step forms.
  
  Examples:
  - user: "напиши тест для компонента" → используй паттерны из скилла
  - user: "как тестировать хуки" → React hooks testing patterns
  - user: "тесты с Redux" → Redux integration testing
---

# Jest React Testing Examples

Коллекция реальных примеров тестирования Jest + React Testing Library, разбитая по темам (progressive disclosure). Каждая тема — полный рабочий пример: компонент + тесты + ключевые приёмы.

## Темы

| # | Тема | Reference |
|---|------|-----------|
| 1 | Базовые компоненты: render, getByRole, toHaveClass, disabled | [references/basic-components.md](references/basic-components.md) |
| 2 | Формы: ввод, submit, валидация, aria-invalid | [references/forms.md](references/forms.md) |
| 3 | Async-данные: fetch, loading/error, waitFor, findBy | [references/async-fetching.md](references/async-fetching.md) |
| 4 | Авторизация: AuthProvider/useAuth, login/logout, localStorage | [references/auth-flow.md](references/auth-flow.md) |
| 5 | Модальные окна: createPortal, Escape, overlay | [references/modals.md](references/modals.md) |
| 6 | Дропдауны/select: listbox, option, click outside | [references/dropdowns-selects.md](references/dropdowns-selects.md) |
| 7 | Кастомные хуки: renderHook, act, rerender | [references/custom-hooks.md](references/custom-hooks.md) |
| 8 | React Router: MemoryRouter, navigate, useLocation | [references/react-router.md](references/react-router.md) |
| 9 | Redux: configureStore, preloadedState, dispatch | [references/redux.md](references/redux.md) |
| 10 | Context API: Provider, хуки вне провайдера | [references/context-api.md](references/context-api.md) |
| 11 | Загрузка файлов: user.upload, File, maxSize | [references/file-upload.md](references/file-upload.md) |
| 12 | Автокомплит: фильтрация, клавиатура, aria-selected | [references/autocomplete.md](references/autocomplete.md) |
| 13 | Infinite scroll: IntersectionObserver mock, пагинация | [references/infinite-scroll.md](references/infinite-scroll.md) |
| 14 | Error Boundary: fallback, onError | [references/error-boundary.md](references/error-boundary.md) |
| 15 | Доступность: toHaveAccessibleName, ARIA-атрибуты | [references/accessibility.md](references/accessibility.md) |
| 16 | Таймеры: fake timers, advanceTimersByTime | [references/timers.md](references/timers.md) |
| 17 | WebSocket: jest-websocket-mock, сообщения | [references/websockets.md](references/websockets.md) |
| 18 | Многошаговые формы (wizard): progressbar | [references/multi-step-form.md](references/multi-step-form.md) |
| — | MSW: настройка сервера, server.use, POST/params | [references/setup-msw.md](references/setup-msw.md) |

## Общие правила

- **Стек**: `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom` (матчеры `toBeInTheDocument`, `toHaveClass`, `toHaveStyle` и др. — подключается в setupFilesAfterEach).
- **userEvent**: всегда `const user = userEvent.setup()` и `await` перед взаимодействиями (`user.click`, `user.type`, `user.keyboard`, `user.upload`). С fake timers — `userEvent.setup({ delay: null })` (см. [timers.md](references/timers.md)).
- **Запросы**:
  - `getByRole('button', { name: /.../i })` — как видит пользователь/скринридер.
  - `getByLabelText(/.../i)` — для полей форм с label.
  - `queryBy*` — проверка отсутствия (`not.toBeInTheDocument()`).
  - `findBy*` / `waitFor` — ожидание async-элементов.
- **Сеть**: HTTP — MSW ([setup-msw.md](references/setup-msw.md)); WebSocket — `jest-websocket-mock` ([websockets.md](references/websockets.md)); IntersectionObserver — мок через `window.IntersectionObserver = jest.fn()` ([infinite-scroll.md](references/infinite-scroll.md)).
- **Изоляция**: `localStorage.clear()` в afterEach для тестов с хранилищем; `jest.useRealTimers()` после fake timers; подавление `console.error` через `jest.spyOn` при тестах ошибок.
- **Хелперы-обёртки**: `renderWithRouter` (MemoryRouter), `renderWithStore` (Provider + configureStore) — переиспользуемые boilerplate, см. соответствующие references.

## Структура директории

- `SKILL.md` — этот файл (навигация + общие правила).
- `references/` — тематические примеры (компонент + тесты + ключевые приёмы).
- `SKILL.md.bak-20260816` — бэкап исходной версии (2682 строки).
