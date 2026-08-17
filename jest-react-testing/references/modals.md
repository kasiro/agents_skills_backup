# Modal and Dialog Testing

Паттерны: `createPortal`, открытие/закрытие, клик по оверлею и контенту (stopPropagation), клавиша Escape, accessibility-атрибуты.

## Компонент: Modal

```javascript
// Modal.jsx
import { useEffect } from 'react';
import { createPortal } from 'react-dom';

export const Modal = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="modal-overlay"
      onClick={onClose}
    >
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 id="modal-title">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="close-button"
          >
            ×
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>,
    document.body
  );
};
```

## Тесты

```javascript
// Modal.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from './Modal';

describe('Modal Component', () => {
  it('does not render when closed', () => {
    render(
      <Modal isOpen={false} onClose={jest.fn()} title="Test Modal">
        Content
      </Modal>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('renders when open', () => {
    render(
      <Modal isOpen={true} onClose={jest.fn()} title="Test Modal">
        Modal Content
      </Modal>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('closes when close button clicked', async () => {
    const user = userEvent.setup();
    const handleClose = jest.fn();

    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Modal">
        Content
      </Modal>
    );

    await user.click(screen.getByRole('button', { name: /close modal/i }));

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('closes when overlay clicked', async () => {
    const user = userEvent.setup();
    const handleClose = jest.fn();

    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Modal">
        Content
      </Modal>
    );

    const overlay = screen.getByRole('dialog');
    await user.click(overlay);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('does not close when content clicked', async () => {
    const user = userEvent.setup();
    const handleClose = jest.fn();

    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Modal">
        <button>Content Button</button>
      </Modal>
    );

    await user.click(screen.getByRole('button', { name: /content button/i }));

    expect(handleClose).not.toHaveBeenCalled();
  });

  it('closes on Escape key press', async () => {
    const user = userEvent.setup();
    const handleClose = jest.fn();

    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Modal">
        Content
      </Modal>
    );

    await user.keyboard('{Escape}');

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('has correct accessibility attributes', () => {
    render(
      <Modal isOpen={true} onClose={jest.fn()} title="Accessible Modal">
        Content
      </Modal>
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
  });
});
```

## Ключевые моменты

- Закрытый модал: `queryByRole('dialog')` → `not.toBeInTheDocument()`.
- Оверлей и контент: клик по оверлею закрывает, клик по контенту — нет (проверка через stopPropagation).
- Escape: `await user.keyboard('{Escape}')` — клавиатурные события эмулируются целиком.
- A11y: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` — проверяем `toHaveAttribute`.
