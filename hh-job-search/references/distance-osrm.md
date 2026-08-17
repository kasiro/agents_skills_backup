# Расчёт расстояния до работы (OSRM API + Nominatim)

Используется когда нужно узнать расстояние от домашнего адреса (Горский 39) до адреса работы.
Вызывается из `interview-format.md` при наличии конкретного адреса у вакансии. Если адреса нет — расстояние не проверять.

## Архитектура

Два независимых сервиса, работающих последовательно:

1. **Nominatim** (OpenStreetMap) — геокодирование: адрес → координаты (широта, долгота)
2. **OSRM** (Open Source Routing Machine) — роутинг: координаты → расстояние по дорогам

---

## Nominatim — геокодирование

Преобразует текстовый адрес в координаты.

```
curl "https://nominatim.openstreetmap.org/search?q=Горский+39,+Новосибирск&format=json&limit=1"
```

Ответ:
```json
[{"lat": "55.0302", "lon": "82.9420", "display_name": "Горский, 39, Новосибирск", ...}]
```

**Важно:**
- Обязательно указывать `User-Agent` в запросе (любой, описывающий приложение)
- Rate limit: 1 запрос в секунду (строго). При превышении — бан по IP
- Запросы формулировать максимально конкретно: город + улица + дом, через запятую
- Если адрес не находится — попробовать без дома или с другим названием улицы

---

## OSRM — все эндпоинты

Публичный сервер: `https://router.project-osrm.org`
Версия API: v5.24.0

### Базовые эндпоинты

| Эндпоинт | Назначение | Использование |
|----------|-----------|---------------|
| `/route/v1/{profile}/{coordinates}` | Маршрут и расстояние | **Основной** — расстояние между двумя адресами |
| `/table/v1/{profile}/{coordinates}` | Матрица расстояний | Сравнение нескольких адресов |
| `/nearest/v1/{profile}/{coordinates}` | Ближайшая дорога к точке | Проверка привязки адреса к дороге |
| `/match/v1/{profile}/{coordinates}` | Снаппинг трека к дорогам | Не используется |
| `/trip/v1/{profile}/{coordinates}` | TSP маршрут | Не используется |
| `/tile/v1/{profile}/{z}/{x}/{y}.mvt` | Векторные тайлы | Не используется |

**Профили:** `driving` (на машине), `walking` (пешком), `cycling` (на велосипеде).

### `/route/v1/` — маршрут (основной)

```
GET /route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}[?параметры]
```

**Параметры запроса:**

| Параметр | Описание | Для расстояния |
|----------|----------|----------------|
| `overview=false` | Не возвращать геометрию | ✅ Экономит трафик |
| `overview=simplified` | Упрощённая геометрия | Опционально |
| `overview=full` | Полная геометрия | Не нужно |
| `steps=false` | Не возвращать шаги (повороты) | ✅ Экономит трафик |
| `steps=true` | Детальные манёвры | Не нужно |
| `alternatives=false` | Не искать альтернативы | ✅ Быстрее |
| `alternatives=true` | Искать альтернативные маршруты | Опционально |
| `geometries=geojson` | Геометрия в GeoJSON | По умолчанию polyline |
| `annotations=false` | Без покилограммных данных | ✅ Экономит трафик |
| `continue_straight=true` | Не разрешать развороты в путевых точках | Опционально |
| `exclude=toll,motorway,ferry` | Исключить типы дорог | Можно исключить платные дороги |
| `language=ru` | Названия улиц на русском | Опционально |
| `radiuses={радиус_в_м}` | Радиус поиска дороги от точки | По умолчанию OSRM сам подбирает |
| `bearings={направление},{допуск}` | Ограничить направление подъезда | Опционально |
| `hints={хинт}` | Кэш-токен (из предыдущего ответа) | Ускоряет повторные запросы |
| `snapping=default` | Избегать is_startpoint-сегментов | По умолчанию |
| `snapping=any` | Снаппить на любой сегмент | Для отдалённых точек |

**Для расчёта расстояния оптимально:**
```
GET /route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false&steps=false&alternatives=false
```

**Структура ответа:**

```json
{
  "code": "Ok",
  "routes": [{
    "distance": 705265.9,
    "duration": 29998.9,
    "weight": 29998.9,
    "weight_name": "routability",
    "legs": [{
      "steps": [],
      "distance": 705265.9,
      "duration": 29998.9,
      "summary": "",
      "weight": 29998.9
    }],
    "geometry": ""
  }],
  "waypoints": [{
    "location": [37.616948, 55.756371],
    "name": "Садовая улица",
    "distance": 3.6,
    "hint": "кэш-токен"
  }]
}
```

**Поля:**
- `routes[0].distance` — расстояние в **метрах** (делить на 1000 для км)
- `routes[0].duration` — время в **секундах** (делить на 3600 для часов)
- `waypoints[0].location` — снапнутая координата (куда OSRM привязал точку)
- `waypoints[0].name` — название дороги, к которой привязалась точка
- `waypoints[0].distance` — расстояние от запрошенной точки до дороги (метры)

### `/table/v1/` — матрица расстояний

Для сравнения нескольких адресов сразу (например, дом vs 3 работы):

```
GET /table/v1/driving/{lon1},{lat1};{lon2},{lat2};{lon3},{lat3}?annotations=distance
```

Ответ:
```json
{
  "code": "Ok",
  "distances": [[0, 705265.9, 342000], [705000, 0, 530000]],
  "durations": [[0, 29998, 15000], [30000, 0, 22000]],
  "sources": [{...}],
  "destinations": [{...}]
}
```

- `distances[i][j]` — расстояние от i-й точки до j-й в метрах
- `durations[i][j]` — время от i-й до j-й в секундах
- `sources`/`destinations` — снапнутые координаты точек

**Максимум:** ~25 координат (зависит от сложности графа).

### `/nearest/v1/` — проверка привязки

Если сомневаетесь, что адрес правильно привязался к дороге:

```
GET /nearest/v1/driving/{lon},{lat}
```

Ответ покажет, на какой дороге оказалась точка и расстояние до неё.

---

## Коды ошибок

| Код | Причина | Решение |
|-----|---------|---------|
| `Ok` | Успех | — |
| `InvalidUrl` | Неверный URL или параметры | Проверить запрос |
| `InvalidService` | Неизвестный эндпоинт | Использовать route/table/nearest/match |
| `InvalidVersion` | Неверная версия API | Использовать v1 |
| `InvalidOptions` | Неверные параметры | Проверить имена параметров |
| `InvalidQuery` | Неверный формат координат | Проверить: lon,lat;lon,lat |
| `InvalidValue` | Неверное значение параметра | Проверить профиль/параметры |
| `NoSegment` | Точка не привязалась к дороге | Слишком далеко от дорог (>км) |
| `TooBig` | Превышен лимит координат | Уменьшить количество точек |
| `NoMatch` | Трек не сопоставлен (match) | Добавить timestamps |

---

## Пример полного цикла (адрес → расстояние)

```bash
# Шаг 1: геокодирование домашнего адреса
HOME=$(curl -s "https://nominatim.openstreetmap.org/search?q=Горский+39,+Новосибирск&format=json&limit=1" | jq -r '.[0] | "\(.lon),\(.lat)"')

# Шаг 2: геокодирование адреса работы
WORK=$(curl -s "https://nominatim.openstreetmap.org/search?q=ул.+Ленина+1,+Новосибирск&format=json&limit=1" | jq -r '.[0] | "\(.lon),\(.lat)"')

# Шаг 3: расстояние по дорогам
curl -s "https://router.project-osrm.org/route/v1/driving/$HOME;$WORK?overview=false&steps=false&alternatives=false" | jq '.routes[0].distance / 1000 | floor'
```

## Пример на Python (для скриптов)

```python
import requests

def geocode(address):
    """Преобразует адрес в координаты (lon, lat). 
    Возвращает (lon, lat) или None."""
    r = requests.get("https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json", "limit": 1},
        headers={"User-Agent": "HH-Job-Search/1.0"})
    if not r.json():
        return None
    return float(r.json()[0]["lon"]), float(r.json()[0]["lat"])

def road_distance_km(addr1, addr2):
    """Расстояние по дорогам между двумя адресами в км.
    Возвращает float (км) или None при ошибке."""
    c1, c2 = geocode(addr1), geocode(addr2)
    if not c1 or not c2:
        return None
    lon1, lat1 = c1
    lon2, lat2 = c2
    try:
        r = requests.get(
            f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}",
            params={"overview": "false", "steps": "false", "alternatives": "false"},
            timeout=10
        )
        if r.json()["code"] != "Ok":
            return None
        return round(r.json()["routes"][0]["distance"] / 1000, 1)
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        return None

def nearest_road(lon, lat):
    """Проверить, привязалась ли точка к дороге.
    Возвращает (lon, lat, distance_m, road_name) или None."""
    try:
        r = requests.get(
            f"https://router.project-osrm.org/nearest/v1/driving/{lon},{lat}",
            timeout=10
        )
        if r.json()["code"] != "Ok":
            return None
        wp = r.json()["waypoints"][0]
        return (wp["location"][0], wp["location"][1], wp["distance"], wp["name"])
    except:
        return None
```

## Ограничения публичного сервера OSRM

| Параметр | Значение |
|----------|----------|
| Rate limit | Формально нет, но при >1 запр/сек могут заблокировать по IP |
| Профили | driving, walking, cycling |
| Геокодинг | НЕ поддерживается — нужен Nominatim |
| Координат в /route | До ~100 |
| Координат в /table | До ~25 |
| Таймаут ответа | Зависит от сложности маршрута (обычно <1 сек) |
| Бесплатно | Да |
| Регистрация/ключ | Не нужны |
| Работает в РФ | Да |

## Альтернативы

Если публичный OSRM сервер недоступен:
1. **OSRM self-hosted** — Docker контейнер с данными РФ (~4 GB), нужен VPS 4 GB RAM (~1000 ₽/мес)
2. **OpenRouteService API** — бесплатно 2000 запросов/день, регистрация через GitHub, работает в РФ
3. **2GIS API** — российский сервис, есть demo key на 30 дней
