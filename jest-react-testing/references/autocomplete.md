# Autocomplete Component

Паттерны: фильтрация по вводу, клавиатурная навигация (Arrow/Enter/Escape), `aria-autocomplete` / `aria-expanded` / `aria-selected`.

## Компонент: Autocomplete

```javascript
// Autocomplete.jsx
import { useState, useEffect, useRef } from 'react';

export const Autocomplete = ({ options, onSelect, placeholder }) => {
  const [input, setInput] = useState('');
  const [filteredOptions, setFilteredOptions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef(null);

  useEffect(() => {
    if (input) {
      const filtered = options.filter((option) =>
        option.toLowerCase().includes(input.toLowerCase())
      );
      setFilteredOptions(filtered);
      setIsOpen(true);
    } else {
      setFilteredOptions([]);
      setIsOpen(false);
    }
  }, [input, options]);

  const handleSelect = (option) => {
    setInput(option);
    setIsOpen(false);
    onSelect(option);
  };

  const handleKeyDown = (e) => {
    if (!isOpen) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev < filteredOptions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : prev));
    } else if (e.key === 'Enter' && highlightedIndex >= 0) {
      handleSelect(filteredOptions[highlightedIndex]);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        aria-autocomplete="list"
        aria-expanded={isOpen}
        aria-controls="autocomplete-list"
      />

      {isOpen && filteredOptions.length > 0 && (
        <ul id="autocomplete-list" role="listbox">
          {filteredOptions.map((option, index) => (
            <li
              key={option}
              role="option"
              aria-selected={index === highlightedIndex}
              onClick={() => handleSelect(option)}
              style={{
                backgroundColor: index === highlightedIndex ? '#eee' : '#fff',
              }}
            >
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

## Тесты

```javascript
// Autocomplete.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Autocomplete } from './Autocomplete';

const options = ['Apple', 'Apricot', 'Banana', 'Cherry', 'Date'];

describe('Autocomplete Component', () => {
  it('filters options based on input', async () => {
    const user = userEvent.setup();

    render(<Autocomplete options={options} onSelect={jest.fn()} />);

    const input = screen.getByRole('textbox');

    await user.type(input, 'ap');

    expect(screen.getByRole('option', { name: /apple/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /apricot/i })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: /banana/i })).not.toBeInTheDocument();
  });

  it('calls onSelect when option clicked', async () => {
    const user = userEvent.setup();
    const handleSelect = jest.fn();

    render(<Autocomplete options={options} onSelect={handleSelect} />);

    await user.type(screen.getByRole('textbox'), 'ban');
    await user.click(screen.getByRole('option', { name: /banana/i }));

    expect(handleSelect).toHaveBeenCalledWith('Banana');
  });

  it('navigates options with arrow keys', async () => {
    const user = userEvent.setup();

    render(<Autocomplete options={options} onSelect={jest.fn()} />);

    const input = screen.getByRole('textbox');

    await user.type(input, 'a');

    const options = screen.getAllByRole('option');

    await user.keyboard('{ArrowDown}');
    expect(options[0]).toHaveAttribute('aria-selected', 'true');

    await user.keyboard('{ArrowDown}');
    expect(options[1]).toHaveAttribute('aria-selected', 'true');

    await user.keyboard('{ArrowUp}');
    expect(options[0]).toHaveAttribute('aria-selected', 'true');
  });

  it('selects option with Enter key', async () => {
    const user = userEvent.setup();
    const handleSelect = jest.fn();

    render(<Autocomplete options={options} onSelect={handleSelect} />);

    const input = screen.getByRole('textbox');

    await user.type(input, 'a');
    await user.keyboard('{ArrowDown}');
    await user.keyboard('{Enter}');

    expect(handleSelect).toHaveBeenCalledWith('Apple');
  });

  it('closes list on Escape key', async () => {
    const user = userEvent.setup();

    render(<Autocomplete options={options} onSelect={jest.fn()} />);

    await user.type(screen.getByRole('textbox'), 'a');

    expect(screen.getByRole('listbox')).toBeInTheDocument();

    await user.keyboard('{Escape}');

    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('case-insensitive filtering', async () => {
    const user = userEvent.setup();

    render(<Autocomplete options={options} onSelect={jest.fn()} />);

    await user.type(screen.getByRole('textbox'), 'APP');

    expect(screen.getByRole('option', { name: /apple/i })).toBeInTheDocument();
  });
});
```

## Ключевые моменты

- Фильтрация: после ввода проверяем отфильтрованный список опций (`getByRole('option')` + отсутствие нерелевантных).
- Клавиатура: `user.keyboard('{ArrowDown}')` / `'{ArrowUp}'` / `'{Enter}'` / `'{Escape}'`.
- Выделение проверяется через `aria-selected` у опций (`getAllByRole('option')[0]`).
- `onSelect` получает выбранное значение: `toHaveBeenCalledWith('Apple')`.
- Регистронезависимость: ввод `'APP'` находит `Apple`.
- Аналогичный listbox-паттерн — у дропдауна, см. [dropdowns-selects.md](dropdowns-selects.md).
