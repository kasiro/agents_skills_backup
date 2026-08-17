---
name: price-parser-magnit
description: |-
  Парсинг цен Магнита через агрегаторы (proshoper.ru, catalog-ceny.ru, magnit-stores.ru).
  Использовать когда нужны актуальные цены на товары в Магните.
  
  Sources:
  - catalog-ceny.ru/magnit/ — каталог с ценами (данные 2023-2024, требуют корректировки на инфляцию ~15-25%)
  - proshoper.ru/actions/magnit-magazin/ — актуальные акции по регионам
  - magnit-stores.ru/catalog/ — каталог по городам (например, magnit-stores.ru/catalog/in/g-novosibirsk)
  - edadeal.ru — агрегатор акций и скидок
  
  Examples:
  - user: "цены в Магните на картошку и лук" → проверить catalog-ceny.ru и proshoper.ru
  - user: "сколько стоит молоко в Магните" → найти через catalog-ceny.ru/magnit/
  - user: "акции Магнит Новосибирск" → proshoper.ru/actions/magnit-magazin/
---
# Парсер цен Магнита

## Методы получения цен

### 1. catalog-ceny.ru (базовый каталог)

Работает через lightpanda. URL категорий:
- Молоко: https://catalog-ceny.ru/magnit/moloko-syr-yayca/moloko-2-1/
- Мясо птицы: https://catalog-ceny.ru/magnit/myaso-ptica/myaso-pticy/
- Овощи: https://catalog-ceny.ru/magnit/ovoschi-i-frukty-1/ovoschi-1/
- Хлеб/выпечка: https://catalog-ceny.ru/magnit/vypechka-1-1-1-1/ (если категория существует)
- Крупы/бакалея: https://catalog-ceny.ru/magnit/krupy-bobovye/

**Важно:** Данные на catalog-ceny.ru обновлялись в 2023-2024 гг. Для корректировки на инфляцию применяй коэффициент ~1.15-1.25.

### 2. proshoper.ru (акции по регионам)

URL для Новосибирска: https://novosibirsk.proshoper.ru/actions/magnit-magazin/
Парсится через lightpanda, показывает актуальные акции с ценами и скидками.

### 3. magnit-stores.ru

Пример: https://magnit-stores.ru/catalog/in/g-novosibirsk
Содержит каталог товаров с ценами по городам.

## Порядок действий для получения цен

1. Проверить proshoper.ru на акции в регионе (Новосибирск)
2. Проверить catalog-ceny.ru для базовых цен
3. Если данные catalog-ceny.ru старше 6 месяцев — применить корректировку на инфляцию
4. Для точных цен — рекомендовать проверить в приложении Магнит или на сайте magnit.ru
