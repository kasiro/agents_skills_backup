# Dropdown and Select Testing

Паттерны: кастомный дропдаун с `role="listbox"` / `role="option"`, `aria-haspopup` / `aria-expanded`, клик вне элемента (click outside).

## Компонент: Dropdown

```javascript
// Dropdown.jsx
import { useState, useRef, useEffect } from 'react';

export const Dropdown = ({ options, value, onChange, placeholder, label }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOption = options.find(opt => opt.value === value);

  const handleSelect = (option) => {
    onChange(option.value);
    setIsOpen(false);
  };

  return (
    <div ref={dropdownRef} className="dropdown">
      <label id="dropdown-label">{label}</label>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby="dropdown-label"
      >
        {selectedOption ? selectedOption.label : placeholder}
      </button>

      {isOpen && (
        <ul role="listbox" aria-labelledby="dropdown-label">
          {options.map((option) => (
            <li
              key={option.value}
              role="option"
              aria-selected={option.value === value}
              onClick={() => handleSelect(option)}
            >
              {option.label}
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
// Dropdown.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Dropdown } from './Dropdown';

const options = [
  { value: 'apple', label: 'Apple' },
  { value: 'banana', label: 'Banana' },
  { value: 'cherry', label: 'Cherry' },
];

describe('Dropdown Component', () => {
  it('renders with placeholder', () => {
    render(
      <Dropdown
        options={options}
        value=""
        onChange={jest.fn()}
        placeholder="Select a fruit"
        label="Fruit"
      />
    );

    expect(screen.getByText(/select a fruit/i)).toBeInTheDocument();
  });

  it('shows selected value', () => {
    render(
      <Dropdown
        options={options}
        value="banana"
        onChange={jest.fn()}
        placeholder="Select a fruit"
        label="Fruit"
      />
    );

    expect(screen.getByText('Banana')).toBeInTheDocument();
  });

  it('opens dropdown on button click', async () => {
    const user = userEvent.setup();

    render(
      <Dropdown
        options={options}
        value=""
        onChange={jest.fn()}
        placeholder="Select a fruit"
        label="Fruit"
      />
    );

    const button = screen.getByRole('button');
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();

    await user.click(button);

    expect(screen.getByRole('listbox')).toBeInTheDocument();
  });

  it('displays all options when open', async () => {
    const user = userEvent.setup();

    render(
      <Dropdown
        options={options}
        value=""
        onChange={jest.fn()}
        placeholder="Select a fruit"
        label="Fruit"
      />
    );

    await user.click(screen.getByRole('button'));

    expect(screen.getByRole('option', { name: /apple/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /banana/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /cherry/i })).toBeInTheDocument();
  });

  it('calls onChange when option selected', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    render(
      <Dropdown
        options={options}
        value=""
        onChange={handleChange}
        placeholder="Select a fruit"
        label="Fruit"
      />
    );

    await user.click(screen.getByRole('button'));
    await user.click(screen.getByRole('option', { name: /banana/i }));

    expect(handleChange).toHaveBeenCalledWith('banana');
  });

  it('closes dropdown after selection', async () => {
    const user = userEvent.setup();

    render(
      <Dropdown
        options={options}
        value=""
        onChange={jest.fn()}
        placeholder="Select a fruit"
        label="Fruit"
      />
    );

    await user.click(screen.getByRole('button'));
    expect(screen.getByRole('listbox')).toBeInTheDocument();

    await user.click(screen.getByRole('option', { name: /apple/i }));

    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });
});
```

## Ключевые моменты

- Список опций — `role="listbox"`, элементы — `role="option"` с `aria-selected`.
- Проверка открытия/закрытия: `queryByRole('listbox')` до клика и после выбора.
- `onChange` получает `value` выбранной опции: `toHaveBeenCalledWith('banana')`.
- Закрытие по клику вне — логика click outside, тестируется через взаимодействие с документом.
- Похожая механика (listbox + option + клавиатура) — у автокомплита, см. [autocomplete.md](autocomplete.md).
