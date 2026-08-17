# File Upload Component

Паттерны: `user.upload`, конструктор `File`, валидация размера, состояния uploading/disabled.

## Компонент: FileUpload

```javascript
// FileUpload.jsx
import { useState } from 'react';

export const FileUpload = ({ onUpload, accept = '*', maxSize = 5 * 1024 * 1024 }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError(null);

    if (!selectedFile) return;

    if (selectedFile.size > maxSize) {
      setError(`File size must be less than ${maxSize / 1024 / 1024}MB`);
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await onUpload(file);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={handleFileChange}
        accept={accept}
        aria-label="File input"
      />

      {file && <p>Selected: {file.name}</p>}

      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>

      {error && <div role="alert">{error}</div>}
    </div>
  );
};
```

## Тесты

```javascript
// FileUpload.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileUpload } from './FileUpload';

describe('FileUpload Component', () => {
  it('displays selected file name', async () => {
    const user = userEvent.setup();
    render(<FileUpload onUpload={jest.fn()} />);

    const file = new File(['hello'], 'hello.png', { type: 'image/png' });
    const input = screen.getByLabelText(/file input/i);

    await user.upload(input, file);

    expect(screen.getByText(/selected: hello.png/i)).toBeInTheDocument();
  });

  it('uploads file successfully', async () => {
    const user = userEvent.setup();
    const handleUpload = jest.fn(() => Promise.resolve());

    render(<FileUpload onUpload={handleUpload} />);

    const file = new File(['content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/file input/i);

    await user.upload(input, file);
    await user.click(screen.getByRole('button', { name: /upload/i }));

    expect(handleUpload).toHaveBeenCalledWith(file);
  });

  it('shows error for files exceeding max size', async () => {
    const user = userEvent.setup();
    const maxSize = 1024; // 1KB

    render(<FileUpload onUpload={jest.fn()} maxSize={maxSize} />);

    const largeFile = new File(['x'.repeat(2000)], 'large.txt', {
      type: 'text/plain',
    });

    const input = screen.getByLabelText(/file input/i);

    await user.upload(input, largeFile);

    expect(screen.getByRole('alert')).toHaveTextContent(/file size must be less than/i);
  });

  it('shows uploading state', async () => {
    const user = userEvent.setup();
    const handleUpload = jest.fn(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<FileUpload onUpload={handleUpload} />);

    const file = new File(['content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/file input/i);

    await user.upload(input, file);
    const uploadButton = screen.getByRole('button', { name: /upload/i });

    await user.click(uploadButton);

    expect(screen.getByRole('button')).toHaveTextContent(/uploading/i);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('disables upload button when no file selected', () => {
    render(<FileUpload onUpload={jest.fn()} />);

    expect(screen.getByRole('button', { name: /upload/i })).toBeDisabled();
  });
});
```

## Ключевые моменты

- Файл создаётся конструктором `new File(['content'], 'name.txt', { type: 'text/plain' })`.
- Загрузка файла в input: `await user.upload(input, file)`.
- Валидация размера: `new File(['x'.repeat(2000)], ...)` с `maxSize` → `role="alert"`.
- Промис-мок: `jest.fn(() => Promise.resolve())` / отложенное разрешение — для проверки состояния uploading.
- `toBeDisabled()` — кнопка неактивна без файла и во время загрузки.
