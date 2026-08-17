---
name: vk-reg-nso
description: |-
  Автоматизация записи к врачу через чат-бот «Мое здоровье НСО» (ВКонтакте). ДКБ 4 им. Гераськова, Новосибирск.
  
  Examples:
  - user: "запиши к педиатру" → запустить скрипт с параметрами
  - user: "запись к врачу" → vk-reg-nso скрипт
  - user: "запись в ДКБ" → автоматизация через VK бота
---

# VK Запись к врачу (НСО)

Автоматизация записи к врачу через чат-бот «Мое здоровье НСО» (ВКонтакте).
ДКБ 4 им. Гераськова, Новосибирск.

## Использование

Скрипт: `~/Документы/python_projects/vk-reg-nso/vk_reg.py`
Репозиторий: https://github.com/kasiro/vk-reg-nso (PRIVATE)

Все флаги обязательные (кроме --token — см. Получение токена):

| Флаг | Описание |
|------|----------|
| `--specialty` | Специальность врача (напр. педиатр) |
| `--fio` | ФИО пациента |
| `--birth` | Дата рождения (ДД.ММ.ГГГГ) |
| `--date` | Желаемая дата посещения (ДД.ММ.ГГГГ) |
| `--time` | Желаемое время (ЧЧ:ММ) |
| `--confirm` | true — подтвердить запись, false — только показать |
| `--wait` | Секунд ждать между шагами (default: 6) |
| `--token TOKEN` | VK токен (если не указан — читается из ~/.config/vk-reg-nso/token.txt) |
| `--save-token TOKEN` | Сохранить новый VK токен в файл и выйти |
| `--check` | Проверить валидность токена и выйти |

## Получение VK токена

Токен **не вшит** в скрипт. Он хранится в `~/.config/vk-reg-nso/token.txt`.
Приоритет: `--token` > `VK_TOKEN` env > файл `~/.config/vk-reg-nso/token.txt`.

### Через vkhost.github.io (рекомендуемый способ)

1. Открыть в браузере https://vkhost.github.io/
2. Нажать **Kate Mobile** (app_id=2685278)
3. Авторизоваться в VK (если требуется)
4. Разрешить приложению доступ
5. После редиректа на `https://oauth.vk.com/blank.html#access_token=...`
   — скопировать значение `access_token` из адресной строки (между `access_token=` и `&expires_in=`)
6. Сохранить токен:
   ```bash
   cd ~/Документы/python_projects/vk-reg-nso
   uv run python vk_reg.py --save-token "vk1.a.скопированный_токен"
   ```

### Через Chrome DevTools MCP (когда доступен браузер через MCP)

1. Открыть страницу https://vkhost.github.io/ через Chrome DevTools
2. Нажать кнопку «Kate Mobile»
3. Пройти авторизацию VK
4. Дождаться редиректа на `blank.html`
5. Извлечь `access_token` из URL-фрагмента
6. Сохранить:
   ```bash
   cd ~/Документы/python_projects/vk-reg-nso
   uv run python vk_reg.py --save-token "извлеченный_токен"
   ```

### Проверка токена

```bash
cd ~/Документы/python_projects/vk-reg-nso
uv run python vk_reg.py --check
```

### Альтернатива: vk_reg_web.py (логин/пароль)

Резервный скрипт, не требующий токена — использует авторизацию по логину/паролю
через веб-версию VK (al_im.php):

```bash
cd ~/Документы/python_projects/vk-reg-nso
uv run python vk_reg_web.py --specialty педиатр --fio "..." --birth ... --date ... --time ... --confirm false
```

Подробнее: `uv run python vk_reg_web.py --help`

## Примеры

```bash
cd ~/Документы/python_projects/vk-reg-nso

# Тестовый прогон (без подтверждения)
uv run python vk_reg.py --specialty педиатр --fio "Каширских Савелий Данилович" --birth 05.10.2023 --date 30.06.2026 --time 16:00 --confirm false

# Полная запись с подтверждением
uv run python vk_reg.py --specialty педиатр --fio "Каширских Савелий Данилович" --birth 05.10.2023 --date 30.06.2026 --time 16:00 --confirm true
```

## Принцип работы

1. Начинает новый диалог с ботом (кнопка ✅ Начать новый диалог)
2. Отправляет «Записаться к врачу»
3. Передаёт специальность → ФИО → дату рождения → дату → время
4. Если --confirm true — подтверждает запись
5. Возвращает JSON с результатом (success, appointment, doctor)
