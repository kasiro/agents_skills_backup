#!/usr/bin/env python3
"""
playwright_parser — парсинг чеков РФ через Playwright + Chromium (headless).
Обходит JS-защиту proverkacheka.com, извлекает товары в JSON.
"""

import json
import sys
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def parse_qr(qr_string: str, headless: bool = True, timeout: int = 40000) -> dict:
    import json

    result = {"success": False, "qr": qr_string, "data": None, "raw_html": "", "error": ""}

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            locale="ru-RU",
            timezone_id="Asia/Novosibirsk",
        )
        page = context.new_page()
        page.set_default_timeout(timeout)

        try:
            # 1. Загрузить страницу
            page.goto("https://proverkacheka.com", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 2. Найти вкладку "Строка" по [role="tab"]
            try:
                page.wait_for_selector('[role="tab"]', timeout=10000)
            except:
                result["error"] = "Табы не загрузились"
                browser.close()
                return result

            tab_found = page.evaluate("""
                () => {
                    const tabs = document.querySelectorAll('[role="tab"]');
                    for (const t of tabs) {
                        if (t.textContent.trim() === 'Строка') {
                            t.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)

            if not tab_found:
                result["error"] = "Вкладка 'Строка' не найдена"
                browser.close()
                return result

            # 3. Ждать появления textarea
            page.wait_for_timeout(1500)
            try:
                page.wait_for_selector("textarea#b-checkform_qrraw", state="attached", timeout=15000)
                page.wait_for_timeout(500)
            except:
                result["error"] = "Поле textarea не появилось"
                browser.close()
                return result

            # 4. Ввести QR-строку — page.fill НЕ РАБОТАЕТ с textarea в этом DOM
            # Используем evaluate с dispatchEvent
            fill_result = page.evaluate(f"""
                () => {{
                    const el = document.getElementById('b-checkform_qrraw');
                    if (!el) return 'textarea not found';

                    // Click to focus
                    el.focus();

                    // Set value via native setter
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(el, {json.dumps(qr_string)});

                    // Dispatch events that the page listens to
                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    el.dispatchEvent(new Event('blur', {{bubbles: true}}));

                    return el.value;
                }}
            """)

            if not fill_result or len(fill_result) < 10:
                result["error"] = f"QR не вставился (value={fill_result!r})"
                browser.close()
                return result

            page.wait_for_timeout(300)

            # 5. Найти и кликнуть кнопку "Проверить"
            btn_found = page.evaluate("""
                () => {
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {
                        if (b.textContent.trim() === 'Проверить') {
                            b.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)

            if not btn_found:
                result["error"] = "Кнопка 'Проверить' не найдена"
                browser.close()
                return result

            # 6. Ждать результат — диалог "Внимание!" или таблица
            page.wait_for_timeout(5000)

            # 7. Проверить диалог "Внимание!" — чек недоступен
            try:
                has_warning = page.evaluate("""
                    () => {
                        const dialog = document.querySelector('dialog[open]');
                        if (dialog) return true;
                        const heading = document.querySelector('h4');
                        return heading && heading.textContent.includes('Внимание!');
                    }
                """)

                if has_warning:
                    result["error"] = "Чек не найден в базе ФНС (информация недоступна)"
                    # Закрыть диалог
                    try:
                        page.evaluate("""
                            () => {
                                const closeBtn = document.querySelector('button.b-close, button:has-text("Закрыть"), dialog[open] button:last-child');
                                if (closeBtn) closeBtn.click();
                            }
                        """)
                    except:
                        pass
                    browser.close()
                    return result
            except:
                pass

            # 8. Если нет диалога — ждать таблицу с результатом
            try:
                page.wait_for_selector("table.table, .b-check_table, .b-check_center", timeout=20000)
                page.wait_for_timeout(2000)
            except:
                pass

            # 9. Извлечь HTML
            html = page.content()
            result["raw_html"] = html

            # 10. Распарсить
            data = _extract_data(page, html)
            if data:
                result["data"] = data
                result["success"] = True
            elif html and not result["error"]:
                result["error"] = "Чек найден, но не удалось распарсить"

        except Exception as e:
            result["error"] = str(e)
            try:
                result["raw_html"] = page.content()
            except:
                pass
        finally:
            browser.close()

    return result


def _extract_data(page, html: str) -> dict | None:
    """Извлечь структурированные данные из HTML страницы с результатом.

    Алгоритм: парсим таблицу .b-check_table через BeautifulSoup,
    потом доизвлекаем регулярками из inner_text body для подстраховки.
    """
    data = {}

    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.b-check_table") or soup.select_one("table.table")
    if not table:
        return None

    rows = table.find_all("tr")

    items = []
    current_item = None
    header_phase = True  # пока не встретили строку-заголовок таблицы

    for tr in rows:
        classes = set(tr.get_attribute_list("class"))
        tds = tr.find_all("td")
        if not tds:
            continue

        # Проверка colspan=5
        is_colspan5 = len(tds) == 1 and tds[0].get("colspan") == "5"

        # Текст ячейки (первой, или всех — по ситуации)
        def cell_text(idx=0):
            return tds[idx].get_text(strip=True) if idx < len(tds) else ""

        # ========== HEADER СТРОКИ (до заголовков таблицы) ==========
        if header_phase:
            # Строка-заголовок таблицы (№, Название, Цена, Кол., Сумма — с <strong>)
            if tds[0].find("strong"):
                header_phase = False
                continue

            # Если colspan=5 и класс b-check_center — header чековой информации
            if is_colspan5:
                text = cell_text()
                if not text:
                    continue

                # ИНН
                m = re.search(r"ИНН\s*(\d{10,12})", text)
                if m:
                    data["user_inn"] = m.group(1)
                    continue

                # Дата и время
                m = re.search(r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})", text)
                if m:
                    data["datetime"] = m.group(1)
                    continue

                # Чек №
                m = re.search(r"Чек\s*№\s*(\d+)", text)
                if m:
                    data["check_no"] = m.group(1)
                    continue

                # Смена №
                m = re.search(r"Смена\s*№\s*(\d+)", text)
                if m:
                    data["shift_no"] = m.group(1)
                    continue

                # Кассир
                m = re.search(r"Кассир\s+(.*)", text)
                if m:
                    data["cashier"] = m.group(1).strip()
                    continue

                # Тип чека (Приход, Возврат прихода, Расход, Возврат расхода)
                if re.match(r"^(Приход|Возврат прихода|Расход|Возврат расхода)$", text):
                    data["receipt_type"] = text
                    continue

                # Название организации (первая содержательная строка)
                if "shop_name" not in data:
                    data["shop_name"] = text
                elif "address" not in data and re.match(r"^\d{6}", text):
                    data["address"] = text
                continue

            # Строка с одним td без colspan (адрес мог не попасть в header)
            if len(tds) == 1 and re.match(r"^\d{6}", cell_text()):
                data["address"] = cell_text()
                continue

            # Пропускаем прочие строки в header-фазе
            continue

        # ========== ТЕЛО ТАБЛИЦЫ (header_phase = False) ==========

        # --- ИТОГО (b-check_itogo) ---
        itogo_td = tds[0].find(class_="b-check_itogo") if len(tds) > 0 else None
        if itogo_td and "ИТОГО" in itogo_td.get_text().upper():
            for td in tds:
                val = td.get_text(strip=True)
                if re.match(r"^[\d]+\.[\d]+$", val):
                    data["total"] = val
                    break
            continue

        # --- Наличные / Карта ---
        label = cell_text(0)
        if label == "Наличные":
            # значение в последнем td
            data["cash"] = tds[-1].get_text(strip=True)
            continue
        if label == "Карта":
            data["ecash"] = tds[-1].get_text(strip=True)
            continue

        # --- Footer colspan=5 строки ---
        if is_colspan5:
            text = cell_text()
            m = re.search(r"ФН:\s*(\d+)", text)
            if m:
                data["fn"] = m.group(1)
                continue
            m = re.search(r"ФД:\s*(\d+)", text)
            if m:
                data["fd"] = m.group(1)
                continue
            m = re.search(r"ФПД#?:\s*(\d+)", text)
            if m:
                data["fpd"] = m.group(1)
                continue
            m = re.search(r"ВИД НАЛОГООБЛОЖЕНИЯ:\s*(\S+)", text)
            if m:
                data["tax_system"] = m.group(1)
                continue
            m = re.search(r"Место расчета:\s*(.+)", text)
            if m:
                data["payment_place"] = m.group(1).strip()
                continue
            m = re.search(r"РЕГ\.НОМЕР ККТ:\s*(\d+)", text)
            if m:
                data["kkt_regno"] = m.group(1)
                continue
            continue  # прочие footer-строки пропускаем

        # --- Товары (b-check_item) ---
        if "b-check_item" in classes:
            # Строка начала товара (b-check_vblock-first)
            if "b-check_vblock-first" in classes:
                # Завершить предыдущий незакрытый товар
                if current_item:
                    items.append(current_item)
                    current_item = None

                if len(tds) >= 5:
                    current_item = {
                        "name": cell_text(1),
                        "price": cell_text(2),
                        "quantity": cell_text(3),
                        "sum": cell_text(4),
                    }
                else:
                    current_item = None

            # Строка НДС (b-check_vblock-last) — прикрепляем к текущему товару
            if "b-check_vblock-last" in classes:
                if current_item and "vat" not in current_item:
                    vat_text = cell_text(0)
                    if "НДС" in vat_text:
                        current_item["vat"] = vat_text
                # Если last без first — это одиночный товар (одна строка на товар)
                if "b-check_vblock-first" not in classes:
                    if current_item:
                        items.append(current_item)
                        current_item = None
                elif current_item and "vat" in current_item:
                    # first+last вместе (товар с НДС в той же строке)
                    items.append(current_item)
                    current_item = None
        else:
            # Не товарная строка — но мог остаться незакрытый товар
            if current_item:
                items.append(current_item)
                current_item = None

    # Добавить последний товар
    if current_item:
        items.append(current_item)

    # Отфильтровать мусор (заголовки)
    items = [
        it for it in items
        if it.get("name") and it["name"] not in ("Название", "№", "")
    ]

    if items:
        data["items"] = items

    # --- Fallback: доизвлечь недостающие поля из body text ---
    try:
        body_text = page.inner_text("body")
    except Exception:
        body_text = ""

    for key, pattern in [
        ("fn", r"ФН:\s*(\d+)"),
        ("fd", r"ФД:\s*(\d+)"),
        ("fpd", r"ФПД#?:\s*(\d+)"),
        ("user_inn", r"ИНН\s*(\d{10,12})"),
        ("total", r"ИТОГО:\s*([\d.]+)"),
        ("cash", r"Наличные[:\s]*([\d.]+)"),
        ("ecash", r"Карта[:\s]*([\d.]+)"),
    ]:
        if key not in data or not data.get(key):
            m = re.search(pattern, body_text)
            if m:
                data[key] = m.group(1)

    return data if (data.get("items") or data.get("user_inn") or data.get("fn")) else None


def save_json(result: dict, path: Path = Path("receipt.json")):
    """Сохранить результат в JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    args = sys.argv[1:]

    if not args:
        print("Использование:")
        print("  python3 playwright_parser.py \"t=20260701T1837&s=673.65&fn=...&i=...&fp=...&n=1\"")
        print("  python3 playwright_parser.py --visible \"t=...\"  # показать браузер")
        print("  cat qr.txt | python3 playwright_parser.py        # из stdin")
        sys.exit(1)

    qr_string = args[0] if not args[0].startswith("--") else sys.stdin.read().strip()
    headless = "--visible" not in args

    print(f"Проверка чека через proverkacheka.com (Chromium)...")
    print(f"   QR: {qr_string[:70]}...\n")

    result = parse_qr(qr_string, headless=headless)

    if result["success"] and result["data"]:
        print("Чек получен!")
        print(json.dumps(result["data"], ensure_ascii=False, indent=2))
    elif result["success"]:
        print("Результат без структуры. Смотри raw_html или receipt.json")
    else:
        print(f"Ошибка: {result.get('error', 'неизвестная')}")

    save_json(result)
    print(f"\nПолный результат: {Path('receipt.json').absolute()}")


if __name__ == "__main__":
    main()
