---
name: receipt-parser-fns
description: |-
  Парсер фискальных чеков РФ по QR-строке через proverkacheka.com API (HTTP, без браузера) и Playwright. HTTP-клиент работает в Termux (Android). Не требует СМС, регистрации, API-ключей (уже вшит). Вспомогательные скрипты: регистрация аккаунтов, проверка статуса ключа.
  
  ⚠️ СТРОГО: для любых запросов к БД использовать ТОЛЬКО receipts_report.py и proverkacheka_client.py. Никаких кастомных python3 -c "...", sqlite3 вручную.
  
  Examples:
  - user: "Распарси чек по QR" → HTTP-клиент или Playwright парсер
  - user: "Проверь чек" → proverkacheka_client.py с исчерпывающим выводом
  - user: "полная инфа по чеку" → proverkacheka_client.py выдаёт: магазин, адрес, дату, ФН/ФД/ФП, ККТ, смену, чек, кассира, ИНН, все товары с маркировкой, НДС, финансы, OFD
  - user: "Новый API ключ" → prov_account.py --key-only
  - user: "Проверь лимит ключа" → prov_key_stats.py
  - user: "кэш чеков" → proverkacheka_client.py с SQLite кэшем
  - user: "обнови чек" → proverkacheka_client.py --no-cache
  - user: "покажи историю чеков" → proverkacheka_client.py --history
  - user: "добавь старый чек в кэш" → импорт receipt.json
  - user: "отчёт за неделю" → receipts_report.py --period WEEK --balance
  - user: "баланс доход/расход" → receipts_report.py --period ALL --balance
  - user: "статистика по дням" → receipts_report.py --period WEEK --by-day
  - user: "сколько заработал" → receipts_report.py --earnings --summary
  - user: "по категориям" → receipts_report.py --period ALL --by-category
  - user: "категории расходов" → receipts_report.py --period MONTH --by-category
  - user: "покажи статистику" → receipts_report.py --period ALL
  - user: "сколько потратил за неделю" → receipts_report.py --period WEEK --summary
  - user: "категории расходов" → receipts_report.py --period MONTH --by-category
  - user: "баланс доход/расход" → receipts_report.py --period ALL --balance
  - user: "по дням" → receipts_report.py --period WEEK --by-day
  - user: "по магазинам" → receipts_report.py --period MONTH --by-store
  - user: "что купил вчера" → receipts_report.py --from 2026-07-20 --to 2026-07-20 --detail
---

# receipt-parser-fns

Парсер фискальных чеков РФ по QR-строке.

## Состав

```
receipt-parser-fns (скилл)
├── SKILL.md
└── scripts/
    ├── proverkacheka_client.py   ← HTTP-клиент (Termux, Python 3.6+, только stdlib)
    ├── receipts_report.py        ← Отчёты: сводка, баланс, по дням/магазинам/людям, CSV/JSON
    └── playwright_parser.py      ← Playwright парсер (ПК, нужен Firefox)

proverkacheka-parser (проект)
└── /home/kasiro/Документы/python_projects/proverkacheka-parser/
    ├── prov_account.py           ← Регистрация + генерация API-ключа
    └── prov_key_stats.py         ← Проверка состояния ключа / лимита
```

---

## Способ 1: HTTP-клиент (для Termux) ✅

Без Playwright, без браузера, без СМС. Работает везде, где есть Python 3.6+.

```bash
python3 scripts/proverkacheka_client.py "t=20260701T1837&s=673.65&fn=7380440902999217&i=24967&fp=2091778878&n=1"
```

Из stdin:
```bash
echo "t=..." | python3 scripts/proverkacheka_client.py
```

### curl
```bash
curl -s -X POST "https://proverkacheka.com/api/v1/check/get" \
  -H "Content-Type: application/json" \
  -d '{"fn":"...","fd":"...","fp":"...","s":"...","t":"20260701T1837","n":"1","token":"40340.WWBoVvuSZ3qGw0UhS"}'
```

> ⚠️ При использовании curl напрямую — кэш не задействуется. Для кэширования используйте `proverkacheka_client.py`.

### Пример исчерпывающего вывода

```
🧾 ЧЕК (proverkacheka.com)
══════════════════════════════════════════════════
🏪 Продавец: АКЦИОНЕРНОЕ ОБЩЕСТВО "ТАНДЕР"
📍 Адрес: 630032, Новосибирская обл, Новосибирск г, Планировочная ул, дом № 58,  б
📅 Дата/время: 2026-07-01T18:37:00
🏬 Магазин: Магазин  Магнит  Шрифт
📄 РЕКВИЗИТЫ:
  ФН: 7380440902999217           ФД: 24967
  ФП: 2091778878                 ККТ: 00109528393045
  Смена: 107  |  Чек: 89
  ИНН: 2310031475                Кассир: Директор магазина Козулькова
  Тип: ПРИХОД                    Налог: УСН (упрощённая)
📦 ТОВАРЫ (6 позиций):
  №   Наименование                          Цена     Кол-во  Сумма    Марк
  ─────────────────────────────────────────────────────────────────────────
  1   ТОМАТЫ 1кг                            158.99   0.556   88.40    —
  2   ЗЕЛЕНЬ АССОРТИ лук/укроп/петрушка     94.99    1       94.99    ✅
  3   МАГНИТ Молоко паст 2,5% 827мл         75.99    1       75.99    ✅
  4   Огурцы Среднеплодные 1кг              49.99    0.586   29.29    —
  5   ЗЕЛЕНЫЙ ЛУГ Сметана 15% 300г          84.99    1       84.99    ✅
  6   TIDE Color Стир порош Автомат         299.99   1       299.99   ✅
🧾 НДС:  НДС ставка 11: 54.10₽  |  НДС 10%: 33.98₽
💰 Итого: 673.65₽  |  Карта: 673.65₽
🔍 OFD: ofd26  |  ID: 6424094188938888705
```

### API-ключ
```
40340.WWBoVvuSZ3qGw0UhS
```
Передаётся в теле как `"token"`.

---

## Кэширование чеков (SQLite) 🗄️

Скрипт `proverkacheka_client.py` автоматически кэширует результаты в SQLite.

**Где хранится:** `~/.local/share/receipt-cache/receipts.db`

**Как работает:**
1. Перед запросом к API — проверка кэша по хэшу (SHA256 от fn+fd+fp)
2. Если чек найден в кэше — возврат без запроса к API
3. Если нет — запрос к API, сохранение результата в кэш

**Статусы при запуске:**
- `🔍 Проверка кэша...` — поиск в БД
- `✅ Найден в кэше!` — данные из локального хранилища
- `🌐 Запрос к API...` — обращение к proverkacheka.com

**Флаги:**
- `--no-cache` — принудительно игнорировать кэш и сделать новый запрос:
  ```bash
  python3 scripts/proverkacheka_client.py --no-cache "t=20260701T1837&s=673.65&fn=..."
  ```

**Преимущества:**
- Экономит лимит API (~15 запросов/сутки на бесплатном ключе)
- Работает офлайн для уже проверенных чеков
- Не требует дополнительных зависимостей (sqlite3 — встроен в Python)

---

### История чеков 📋

Каждый новый запрос к API автоматически сохраняется в историю.

**Команды:**
- `--history [N]` — показать последние N записей (по умолчанию 20):
  ```bash
  python3 scripts/proverkacheka_client.py --history
  python3 scripts/proverkacheka_client.py --history 5   # последние 5
  ```

**Формат вывода:**
- `🏪 Название магазина`
- `📍 Адрес`
- `💰 Сумма`
- `📦 Список товаров (до 5 позиций)`
- `💬 Комментарий`

**Пример:**
```
📋 ИСТОРИЯ ЧЕКОВ
═══════════════════════════════════════
#2 | 2026-07-05T21:46:00
  🏪 АКЦИОНЕРНОЕ ОБЩЕСТВО "ТАНДЕР"
  📍 Новосибирск, Планировочная 58
  💰 1058.69₽
  📦 Цыпленок бройлер охл. 5.27×1058.69₽
```

> 💡 **Совет:** старые чеки (receipt.json) можно импортировать в кэш и историю запустив `proverkacheka_client.py` с их QR-строкой — они автоматически добавятся в историю.

### Ручное добавление покупок (без QR)

```bash
python3 proverkacheka_client.py --add СУММА "ТОВАР×КОЛ-ВО, ТОВАР×КОЛ-ВО, ..." [МАГАЗИН] [КОММЕНТАРИЙ]
```

**ВАЖНО:** Количество каждого товара обязательно — пиши через × (крестик-умножение).

**Пример:**
```bash
python3 proverkacheka_client.py --add 687 "картошка×1кг, морковь×3шт, лук×3шт, хлеб×1шт, сигареты×1п, молоко×1шт, сахар×1кг" "Магнит" "Было 2200₽"
```

> 📌 **Часовой пояс:** всё время в чеках и истории отображается в **Новосибирском времени (UTC+7 / MSK+4)**.

---

### База данных покупок (расходы + доходы) 📊

Вся информация в `~/.local/share/receipt-cache/receipts.db`.

**Таблицы:**
- `history` — все покупки (QR-чеки + ручные записи)
- `earnings` — доходы (подработки, зарплата)

**Структура `earnings`:** id, date, source, hours, rate, total, comment

---

### Отчёты и статистика 📈

> ⚠️ **ВАЖНО: для любых запросов к БД использовать ТОЛЬКО этот скрипт!** 
> Запрещается писать кастомные python3 -c "..." запросы, прямой sqlite3 в консоли, 
> или любые другие обходные пути. Все данные — через receipts_report.py.

Скрипт: `scripts/receipts_report.py`

**Периоды:**
- `--period TODAY|WEEK|MONTH|ALL` — готовые периоды
- `--days N` — последние N дней
- `--from YYYY-MM-DD --to YYYY-MM-DD` — произвольный

**Режимы вывода:**
- `--summary` — сводка (по умолчанию)
- `--balance` — доходы vs расходы с % дефицита/сбережений
- `--by-day` — таблица по дням
- `--by-store` — по магазинам
- `--by-person` — по людям (сэр/жена)
- `--by-category` — по категориям товаров
- `--detail` — все записи детально
- `--csv FILE` — экспорт в CSV
- `--json` — вывод в JSON
- `--expenses` / `--earnings` — только расходы/доходы

**Примеры:**
```bash
# Баланс за всё время
python3 scripts/receipts_report.py --period ALL --balance

# По дням за неделю
python3 scripts/receipts_report.py --period WEEK --by-day

# Сводка за последние 3 дня
python3 scripts/receipts_report.py --days 3 --summary

# Детально за конкретный день
python3 scripts/receipts_report.py --from 2026-07-19 --to 2026-07-19 --detail

# По магазинам за месяц
python3 scripts/receipts_report.py --period MONTH --by-store

# По категориям за всё время
python3 scripts/receipts_report.py --period ALL --by-category
```

**Теги людей:** сэр — тег `[сэр]`, жена — тег `[жена]`. Общие расходы (QR-чеки и записи без тега) считаются как `[общее]`.

---

## Способ 2: Playwright (ПК, не для Termux)

```bash
pip install playwright beautifulsoup4 lxml
playwright install firefox
python3 scripts/playwright_parser.py "t=...&s=...&fn=...&i=...&fp=...&n=1"
```

---

## Скрипты управления аккаунтом

### Регистрация + API-ключ (prov_account.py)
```bash
cd /home/kasiro/Документы/python_projects/proverkacheka-parser
uv run python3 prov_account.py --email new@mail.ru --password Pass123!
```

После активации email получить ключ:
```bash
uv run python3 prov_account.py --email user@mail.ru --password Pass123! --key-only
```

### Проверка состояния ключа (prov_key_stats.py)
```bash
uv run python3 prov_key_stats.py
```

---

## Лимиты API

| Тип | Лимит |
|-----|:-----:|
| Бесплатный ключ | ~15 запросов/сутки (рекомендательный) |
| Платная подписка | от 86₽/мес (детали в ЛК) |
| Код превышения | `"code": 3` в ответе API |

---

## Формат ответа API

| Поле | Описание | Пример |
|------|----------|--------|
| `code` | Код результата (1=успех, 3=лимит) | 1 |
| `data.user` | Название магазина | "АО ТАНДЕР" |
| `data.userInn` | ИНН | "2310031475" |
| `data.retailPlaceAddress` | Адрес | "Новосибирск, Планировочная 58" |
| `data.dateTime` | Дата/время | "2026-07-01T18:37:00" |
| `data.totalSum` | Сумма итого (копейки) | 67365 |
| `data.cashTotalSum` | Наличные (копейки) | 0 |
| `data.ecashTotalSum` | Безнал (копейки) | 67365 |
| `data.fiscalDriveNumber` | ФН | "7380440902999217" |
| `data.fiscalDocumentNumber` | ФД | 24967 |
| `data.fiscalSign` | ФП | 2091778878 |
| `data.operationType` | Тип (1=приход) | 1 |
| `data.appliedTaxationType` | Налоговая система | "OSN" |
| `data.items[].name` | Название товара | "ТОМАТЫ 1кг" |
| `data.items[].price` | Цена (копейки) | 15899 |
| `data.items[].quantity` | Количество | 0.556 |
| `data.items[].sum` | Сумма (копейки) | 8840 |

> ⚠️ **Суммы в копейках!** 67365 = 673.65₽. В скрипте `proverkacheka_client.py` конвертация уже встроена.

---

## Коды ответа API

| Код | Значение |
|:---:|---------|
| 0 | Чек некорректен (не найден в базе) |
| 1 | ✅ Успех — данные получены |
| 2 | Данные ещё не получены (попробуйте позже) |
| 3 | ❌ **Превышен лимит запросов** |
| 4 | Ожидание перед повторным запросом |
| 5 | Прочее (данные не получены) |

---

## Требования

- Python 3.6+
- HTTP-клиент: **ничего** — только urllib, json, hashlib, sqlite3 (все встроены в Python)
- Playwright: `pip install playwright beautifulsoup4 lxml && playwright install firefox`
- prov_account.py: `pip install playwright pycryptodome`
- prov_key_stats.py: **ничего** — только стандартная библиотека

---

## 📋 Референс покупателя

| Кто | |
|:----|:---|
| 👤 **Сэр** | Все покупки семьи (основная история) |
| 👩 **Жена** | Энергетики, алкоголь |
| 🧒 **Саве (сын)** | Дюшес, соки |

> ⚠️ **Все референсы относятся только к сэру и его семье (сэр, жена, сын Саве).**

### Референс-файлы
- Сигареты — `references/cigarette-history.md`
- Энергетики — `references/energy-drinks-history.md`
- История алкоголя сэра — `references/alcohol-history.md`
