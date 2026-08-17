# Testing Timers and Intervals

Паттерны: `jest.useFakeTimers()`, `jest.advanceTimersByTime()`, `userEvent.setup({ delay: null })`, спай на `clearInterval`.

## Компонент: Countdown

```javascript
// Countdown.jsx
import { useState, useEffect } from 'react';

export const Countdown = ({ initialSeconds, onComplete }) => {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    let interval = null;

    if (isActive && seconds > 0) {
      interval = setInterval(() => {
        setSeconds((prev) => prev - 1);
      }, 1000);
    } else if (seconds === 0) {
      onComplete?.();
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, seconds, onComplete]);

  const start = () => setIsActive(true);
  const pause = () => setIsActive(false);
  const reset = () => {
    setIsActive(false);
    setSeconds(initialSeconds);
  };

  return (
    <div>
      <div>{seconds} seconds remaining</div>
      <button onClick={start} disabled={isActive}>
        Start
      </button>
      <button onClick={pause} disabled={!isActive}>
        Pause
      </button>
      <button onClick={reset}>Reset</button>
    </div>
  );
};
```

## Тесты

```javascript
// Countdown.test.jsx
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Countdown } from './Countdown';

describe('Countdown Component', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('displays initial countdown', () => {
    render(<Countdown initialSeconds={10} />);

    expect(screen.getByText(/10 seconds remaining/i)).toBeInTheDocument();
  });

  it('counts down when started', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Countdown initialSeconds={5} />);

    await user.click(screen.getByRole('button', { name: /start/i }));

    act(() => {
      jest.advanceTimersByTime(1000);
    });

    expect(screen.getByText(/4 seconds remaining/i)).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(2000);
    });

    expect(screen.getByText(/2 seconds remaining/i)).toBeInTheDocument();
  });

  it('pauses countdown', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Countdown initialSeconds={10} />);

    await user.click(screen.getByRole('button', { name: /start/i }));

    act(() => {
      jest.advanceTimersByTime(3000);
    });

    expect(screen.getByText(/7 seconds remaining/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /pause/i }));

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    // Should still be 7 after pausing
    expect(screen.getByText(/7 seconds remaining/i)).toBeInTheDocument();
  });

  it('resets countdown', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Countdown initialSeconds={10} />);

    await user.click(screen.getByRole('button', { name: /start/i }));

    act(() => {
      jest.advanceTimersByTime(3000);
    });

    await user.click(screen.getByRole('button', { name: /reset/i }));

    expect(screen.getByText(/10 seconds remaining/i)).toBeInTheDocument();
  });

  it('calls onComplete when countdown reaches zero', async () => {
    const user = userEvent.setup({ delay: null });
    const handleComplete = jest.fn();

    render(<Countdown initialSeconds={3} onComplete={handleComplete} />);

    await user.click(screen.getByRole('button', { name: /start/i }));

    act(() => {
      jest.advanceTimersByTime(3000);
    });

    expect(handleComplete).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/0 seconds remaining/i)).toBeInTheDocument();
  });

  it('cleans up interval on unmount', () => {
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
    const { unmount } = render(<Countdown initialSeconds={10} />);

    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();
  });
});
```

## Ключевые моменты

- `jest.useFakeTimers()` в `beforeEach`, `jest.useRealTimers()` в `afterEach` — изоляция.
- Продвижение времени: `act(() => { jest.advanceTimersByTime(1000); })` — обёртка в `act` обязательна.
- `userEvent.setup({ delay: null })` — отключает внутренние задержки userEvent, иначе они конфликтуют с fake timers.
- Пауза: после `pause` время не влияет на счётчик.
- Колбэк при нуле: `toHaveBeenCalledTimes(1)`.
- Очистка: `jest.spyOn(global, 'clearInterval')` + `unmount()` → `toHaveBeenCalled()`.
