# Multi-step Form Wizard

Паттерны: пошаговая форма (steps), `onNext` / `onBack`, сбор данных со всех шагов, `role="progressbar"` + `aria-valuenow`.

## Компонент: FormWizard

```javascript
// FormWizard.jsx
import { useState } from 'react';

export const FormWizard = ({ steps, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});

  const handleNext = (stepData) => {
    const updatedData = { ...formData, ...stepData };
    setFormData(updatedData);

    if (currentStep === steps.length - 1) {
      onComplete(updatedData);
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(0, prev - 1));
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div>
      <div>
        Step {currentStep + 1} of {steps.length}: {steps[currentStep].title}
      </div>

      <div role="progressbar" aria-valuenow={currentStep + 1} aria-valuemax={steps.length}>
        Progress: {Math.round(((currentStep + 1) / steps.length) * 100)}%
      </div>

      <CurrentStepComponent
        onNext={handleNext}
        onBack={handleBack}
        initialData={formData}
        isFirstStep={currentStep === 0}
        isLastStep={currentStep === steps.length - 1}
      />
    </div>
  );
};
```

## Тесты

```javascript
// FormWizard.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FormWizard } from './FormWizard';

// Mock step components
const Step1 = ({ onNext, isFirstStep }) => (
  <div>
    <h2>Step 1 Content</h2>
    <button onClick={() => onNext({ step1Data: 'value1' })}>
      {isFirstStep ? 'Next' : 'Continue'}
    </button>
  </div>
);

const Step2 = ({ onNext, onBack }) => (
  <div>
    <h2>Step 2 Content</h2>
    <button onClick={onBack}>Back</button>
    <button onClick={() => onNext({ step2Data: 'value2' })}>Next</button>
  </div>
);

const Step3 = ({ onNext, isLastStep }) => (
  <div>
    <h2>Step 3 Content</h2>
    <button onClick={() => onNext({ step3Data: 'value3' })}>
      {isLastStep ? 'Submit' : 'Next'}
    </button>
  </div>
);

const steps = [
  { title: 'Personal Info', component: Step1 },
  { title: 'Address', component: Step2 },
  { title: 'Review', component: Step3 },
];

describe('FormWizard Component', () => {
  it('renders first step', () => {
    render(<FormWizard steps={steps} onComplete={jest.fn()} />);

    expect(screen.getByText(/step 1 of 3: personal info/i)).toBeInTheDocument();
    expect(screen.getByText(/step 1 content/i)).toBeInTheDocument();
  });

  it('advances to next step', async () => {
    const user = userEvent.setup();
    render(<FormWizard steps={steps} onComplete={jest.fn()} />);

    await user.click(screen.getByRole('button', { name: /next/i }));

    expect(screen.getByText(/step 2 of 3: address/i)).toBeInTheDocument();
    expect(screen.getByText(/step 2 content/i)).toBeInTheDocument();
  });

  it('goes back to previous step', async () => {
    const user = userEvent.setup();
    render(<FormWizard steps={steps} onComplete={jest.fn()} />);

    await user.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText(/step 2 content/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /back/i }));
    expect(screen.getByText(/step 1 content/i)).toBeInTheDocument();
  });

  it('completes wizard and calls onComplete with all data', async () => {
    const user = userEvent.setup();
    const handleComplete = jest.fn();

    render(<FormWizard steps={steps} onComplete={handleComplete} />);

    // Step 1
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 2
    await user.click(screen.getAllByRole('button', { name: /next/i })[1]);

    // Step 3 - Submit
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(handleComplete).toHaveBeenCalledWith({
      step1Data: 'value1',
      step2Data: 'value2',
      step3Data: 'value3',
    });
  });

  it('shows correct progress', async () => {
    const user = userEvent.setup();
    render(<FormWizard steps={steps} onComplete={jest.fn()} />);

    expect(screen.getByText(/progress: 33%/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /next/i }));

    expect(screen.getByText(/progress: 67%/i)).toBeInTheDocument();
  });

  it('has accessible progressbar', () => {
    render(<FormWizard steps={steps} onComplete={jest.fn()} />);

    const progressbar = screen.getByRole('progressbar');
    expect(progressbar).toHaveAttribute('aria-valuenow', '1');
    expect(progressbar).toHaveAttribute('aria-valuemax', '3');
  });
});
```

## Ключевые моменты

- Шаги передаются как `[{ title, component }]`; шаг-компонент получает `onNext` / `onBack` / `initialData` / `isFirstStep` / `isLastStep`.
- Сбор данных: каждый шаг возвращает свои данные через `onNext({ step1Data: 'value1' })` — мержатся в `formData`.
- Завершение: на последнем шаге `onComplete(updatedData)` со всеми данными (`toHaveBeenCalledWith({ step1Data, step2Data, step3Data })`).
- Множественные кнопки Next на разных шагах: `getAllByRole('button', { name: /next/i })[1]`.
- Прогресс: `role="progressbar"` с `aria-valuenow` / `aria-valuemax` + текстовый процент.
- Обычные формы с валидацией — см. [forms.md](forms.md).
