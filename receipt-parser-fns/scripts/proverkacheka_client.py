#!/usr/bin/env python3
"""
proverkacheka_client — HTTP-клиент для proverkacheka.com API.
Работает в Termux! Без Playwright, без СМС, без браузера.
"""

import json
import sys
from urllib.request import Request, urlopen
import hashlib
import sqlite3
import os
import os.path
from datetime import datetime, timezone, timedelta

API_URL = "https://proverkacheka.com/api/v1/check/get"
API_TOKEN = "40340.WWBoVvuSZ3qGw0UhS"

CACHE_DIR = os.path.expanduser("~/.local/share/receipt-cache")
CACHE_DB = os.path.join(CACHE_DIR, "receipts.db")

# Новосибирск — UTC+7 (MSK+4)
NSK_TZ = timezone(timedelta(hours=7))


def parse_qr(qr_string: str) -> dict:
    """Распарсить QR-строку в параметры для API."""
    params = {}
    for part in qr_string.split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
            params[k] = v
    return params


def get_ticket(fn: str, fd: str, fp: str, total: str, dt: str, token: str = API_TOKEN) -> dict:
    """Получить данные чека через API proverkacheka.com.
    
    dt может быть в формате:
      - YYYYMMDDTHHMM (из QR-строки, отправляется как есть)
      - DD.MM.YYYY HH:MM (конвертируется в YYYYMMDDTHHMM)
    """
    # Конвертировать дату если в формате DD.MM.YYYY HH:MM → YYYYMMDDTHHMM
    if "." in dt:
        import re
        m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})", dt)
        if m:
            dt = f"{m.group(3)}{m.group(2)}{m.group(1)}T{m.group(4)}{m.group(5)}"
    
    payload = json.dumps({
        "fn": fn, "fd": fd, "fp": fp,
        "s": total, "t": dt, "n": "1",
        "token": token,
    }).encode()
    
    req = Request(API_URL, data=payload, 
        headers={"Content-Type": "application/json"})
    
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def init_db():
    """Инициализировать SQLite базу для кэша."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_hash TEXT UNIQUE NOT NULL,
            qr_string TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_hash TEXT NOT NULL,
            qr_string TEXT NOT NULL,
            store_name TEXT,
            store_address TEXT,
            total_sum REAL,
            purchase_date TEXT,
            items_summary TEXT,
            comment TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (qr_hash) REFERENCES receipts(qr_hash)
        )
    """)
    conn.commit()
    conn.close()


def qr_hash(qr_string: str) -> str:
    """Вычислить SHA256 хэш от fn+fd+fp."""
    params = parse_qr(qr_string)
    key = f"{params.get('fn','')}|{params.get('i','')}|{params.get('fp','')}"
    return hashlib.sha256(key.encode()).hexdigest()


def check_cache(qr_string: str) -> dict | None:
    """Проверить кэш по QR-строке."""
    h = qr_hash(qr_string)
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.execute(
        "SELECT response FROM receipts WHERE qr_hash = ?", (h,)
    )
    row = cursor.fetchone()
    if row:
        conn.execute(
            "UPDATE receipts SET last_accessed = CURRENT_TIMESTAMP WHERE qr_hash = ?",
            (h,)
        )
        conn.commit()
        conn.close()
        return json.loads(row[0])
    conn.close()
    return None


def save_to_cache(qr_string: str, response_dict: dict) -> None:
    """Сохранить ответ в кэш."""
    h = qr_hash(qr_string)
    conn = sqlite3.connect(CACHE_DB)
    conn.execute(
        "INSERT OR REPLACE INTO receipts (qr_hash, qr_string, response) VALUES (?, ?, ?)",
        (h, qr_string, json.dumps(response_dict, ensure_ascii=False))
    )
    conn.commit()
    conn.close()


def get_ticket_from_qr(qr_string: str, token: str = API_TOKEN, use_cache: bool = True) -> dict:
    """Получить чек по QR-строке.
    
    QR-строка уже содержит t=YYYYMMDDTHHMM — передаём как есть.
    API сам принимает этот формат.
    
    Если use_cache=True, сначала проверяет кэш SQLite.
    """
    if use_cache:
        cached = check_cache(qr_string)
        if cached is not None:
            return cached
    
    params = parse_qr(qr_string)
    ticket = get_ticket(
        fn=params.get("fn", ""),
        fd=params.get("i", ""),
        fp=params.get("fp", ""),
        total=params.get("s", "0"),
        dt=params.get("t", ""),
        token=token,
    )
    
    if use_cache:
        save_to_cache(qr_string, ticket)
    
    # Сохранить в историю
    if ticket.get("code") == 1:
        save_history(qr_string, ticket)
    
    return ticket


def _copecks_to_rub(copecks) -> str:
    """Перевести копейки в рубли."""
    try:
        val = float(copecks) / 100
        return f"{val:.2f}"
    except (ValueError, TypeError):
        return str(copecks)


def get_items_summary(response_dict: dict) -> str:
    """Сформировать краткую сводку товаров из ответа API."""
    j = response_dict.get("data", {}).get("json", {})
    items = j.get("items", [])
    parts = []
    for item in items[:5]:  # максимум 5 товаров
        name = item.get("name", "—")
        qty = item.get("quantity", 1)
        summ = _copecks_to_rub(item.get("sum", 0))
        parts.append(f"{name} {qty}×{summ}₽")
    if len(items) > 5:
        parts.append(f"...и ещё {len(items)-5} позиций")
    return " | ".join(parts)


def save_history(qr_string: str, response_dict: dict, comment: str = ""):
    """Сохранить запись в истории чеков."""
    d = response_dict.get("data", {}).get("json", {})
    store = d.get("user", "")
    address = d.get("retailPlaceAddress", "")
    total = 0
    try:
        total = float(d.get("totalSum", 0)) / 100
    except (ValueError, TypeError):
        pass
    purchase_date = d.get("dateTime", "")
    items = get_items_summary(response_dict)
    h = qr_hash(qr_string)

    conn = sqlite3.connect(CACHE_DB)
    conn.execute("""
        INSERT OR IGNORE INTO history (qr_hash, qr_string, store_name, store_address, total_sum, purchase_date, items_summary, comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (h, qr_string, store, address, total, purchase_date, items, comment))
    conn.commit()
    conn.close()


def show_history(limit: int = 20):
    """Показать историю чеков."""
    conn = sqlite3.connect(CACHE_DB)
    rows = conn.execute("""
        SELECT id, store_name, store_address, total_sum, purchase_date, items_summary, comment, created_at
        FROM history ORDER BY created_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    if not rows:
        return "📭 История чеков пуста"

    lines = ["📋 ИСТОРИЯ ЧЕКОВ", "═" * 50]
    for r in rows:
        lines.append(f"\n#{r[0]} | {r[4] or '—'}")
        lines.append(f"  🏪 {r[1] or '—'}")
        lines.append(f"  📍 {r[2] or '—'}")
        lines.append(f"  💰 {r[3]:.2f}₽" if r[3] else "")
        lines.append(f"  📦 {r[5] or '—'}")
        if r[6]:
            lines.append(f"  💬 {r[6]}")
        added_raw = str(r[7]) if r[7] else ""
        try:
            added_dt = datetime.fromisoformat(added_raw.replace('Z', '+00:00').replace(' ', 'T'))
            # Если нет часового пояса — считаем что это UTC
            if added_dt.tzinfo is None:
                added_dt = added_dt.replace(tzinfo=timezone.utc)
            added_nsk = added_dt.astimezone(NSK_TZ)
            lines.append(f"  🕐 Добавлен: {added_nsk.strftime('%Y-%m-%d %H:%M:%S')} НСК")
        except:
            lines.append(f"  🕐 Добавлен: {r[7]}")
    return "\n".join(lines)


def _taxation_name(code) -> str:
    """Название системы налогообложения по коду."""
    names = {
        0: "ОСН (общая)",
        1: "УСН (упрощённая) — доход",
        2: "УСН (упрощённая) — доход минус расход",
        3: "ЕНВД",
        4: "ЕСХН",
        5: "ПСН (патентная)",
    }
    return names.get(code, f"код {code}")


def pretty_print(ticket: dict) -> str:
    """Исчерпывающий вывод чека."""
    lines = []
    d = ticket.get("data", {})
    j = d.get("json", {})
    
    lines.append("🧾 ЧЕК (proverkacheka.com)")
    lines.append("═" * 50)
    
    # Продавец
    lines.append(f'🏪 Продавец: {j.get("user", "—")}')
    lines.append(f'📍 Адрес: {j.get("retailPlaceAddress", "—")}')
    dt_raw = j.get("dateTime", "")
    if dt_raw:
        try:
            dt = datetime.fromisoformat(dt_raw)
            dt_nsk = dt.astimezone(NSK_TZ)
            lines.append(f'📅 Дата/время: {dt_nsk.strftime("%Y-%m-%d %H:%M:%S")} НСК (UTC+7)')
        except:
            lines.append(f'📅 Дата/время: {dt_raw}')
    else:
        lines.append('📅 Дата/время: —')
    lines.append(f'🏬 Магазин: {j.get("retailPlace", "—")}')
    lines.append("")
    
    # Реквизиты чека
    lines.append("📄 РЕКВИЗИТЫ:")
    lines.append(f'  ФН: {j.get("fiscalDriveNumber", "—")}')
    lines.append(f'  ФД: {j.get("fiscalDocumentNumber", "—")}')
    lines.append(f'  ФП: {j.get("fiscalSign", "—")}')
    lines.append(f'  ККТ: {j.get("numberKkt", "—")} (рег. № {j.get("kktRegId", "—")})')
    lines.append(f'  Смена: {j.get("shiftNumber", "—")}  |  Чек: {j.get("requestNumber", "—")}')
    lines.append(f'  ИНН: {j.get("userInn", "—")}')
    lines.append(f'  Кассир: {j.get("operator", "—")}')
    lines.append(f'  Тип: {"ПРИХОД" if j.get("operationType") == 1 else "РАСХОД"}')
    lines.append(f'  Налог: {_taxation_name(j.get("appliedTaxationType"))}')
    lines.append("")
    
    # Товары
    items = j.get("items", [])
    if items:
        lines.append(f"📦 ТОВАРЫ ({len(items)} позиций):")
        lines.append(f'  {"№":<3} {"Наименование":<48} {"Цена":<8} {"Кол-во":<7} {"Сумма":<8} {"Марк":<5}')
        lines.append("  " + "─" * 80)
        for i, item in enumerate(items, 1):
            name = item.get("name", "—")
            price = _copecks_to_rub(item.get("price", 0))
            qty = item.get("quantity", "1")
            summ = _copecks_to_rub(item.get("sum", 0))
            marked = "✅" if item.get("productCodeNew") else "—"
            # Обрезаем длинное имя
            name_trunc = name if len(name) <= 47 else name[:44] + "..."
            lines.append(f'  {i:<3} {name_trunc:<48} {price:<8} {qty:<7} {summ:<8} {marked:<5}')
        lines.append("")
    
    # НДС
    nds10 = j.get("nds10", 0)
    nds18 = j.get("nds18", 0)
    nds20 = j.get("nds20", 0)
    nds0 = j.get("nds0", 0)
    nds_no = j.get("ndsCalculated108", 0)
    amounts = j.get("amountsReceiptNds", {}).get("amountsNds", [])
    
    lines.append("🧾 НДС:")
    if amounts:
        nds_names = {1: "НДС 20%", 2: "НДС 10%", 3: "НДС 18%", 4: "НДС 10/110", 5: "НДС 20/120", 6: "НДС 0%", 7: "без НДС"}
        for a in amounts:
            nds_type = nds_names.get(a.get("nds"), f"НДС ставка {a.get('nds')}")
            nds_sum = _copecks_to_rub(a.get("ndsSum", 0))
            lines.append(f'  {nds_type}: {nds_sum}₽')
    if nds10 > 0:
        lines.append(f'  НДС 10%: {_copecks_to_rub(nds10)}₽')
    if nds20 > 0:
        lines.append(f'  НДС 20%: {_copecks_to_rub(nds20)}₽')
    if nds0 > 0:
        lines.append(f'  НДС 0%: {_copecks_to_rub(nds0)}₽')
    lines.append("")
    
    # Финансы
    total = _copecks_to_rub(j.get("totalSum", 0))
    cash = _copecks_to_rub(j.get("cashTotalSum", 0))
    ecash = _copecks_to_rub(j.get("ecashTotalSum", 0))
    
    lines.append("💰 ФИНАНСЫ:")
    lines.append(f'  Итого: {total}₽')
    if float(cash) > 0:
        lines.append(f'  Наличные: {cash}₽')
    if float(ecash) > 0:
        lines.append(f'  Карта: {ecash}₽')
    lines.append("")
    
    # Метаданные
    meta = j.get("metadata", {})
    if meta:
        lines.append("🔍 СЛУЖЕБНАЯ ИНФОРМАЦИЯ:")
        lines.append(f'  OFD: {meta.get("ofdId", "—")}')
        lines.append(f'  ID в ОФД: {meta.get("id", "—")}')
        lines.append(f'  Дата получения ОФД: {meta.get("receiveDate", "—")}')
    
    # Ссылка на PDF
    fp = j.get("fiscalSign", "")
    fd_num = j.get("fiscalDocumentNumber", "")
    # Формируем ID чека из метаданных
    meta_id = meta.get("id", "") if meta else ""
    if meta_id:
        import hashlib
        # Ссылка не гарантирована, но попробуем сформировать
        pass
    
    return "\n".join(filter(None, lines))


def add_manual_receipt(total: float, items_desc: str, store: str = "", 
                       date: str = "", comment: str = "", qr_string: str = ""):
    """Добавить ручную запись в историю (без QR, для чеков без кода).

    Если ручная запись с таким total+items уже существует — обновляет её,
    а не создаёт дубликат. Это позволяет исправлять дату, комментарий и магазин.
    """
    # Хэш БЕЗ даты — чтобы при изменении даты обновлялась та же запись
    h = hashlib.sha256(f"manual:{total}:{items_desc}".encode()).hexdigest()[:16]
    qs = qr_string or f"manual:{date}"
    
    conn = sqlite3.connect(CACHE_DB)
    existing = conn.execute(
        "SELECT id FROM history WHERE qr_hash = ? AND qr_string LIKE 'manual:%'",
        (h,)
    ).fetchone()
    
    if existing:
        conn.execute("""
            UPDATE history 
            SET store_name=?, total_sum=?, purchase_date=?, 
                items_summary=?, comment=?, qr_string=?
            WHERE id=?
        """, (store, total, date, items_desc, comment, qs, existing[0]))
    else:
        conn.execute("""
            INSERT INTO history 
                (qr_hash, qr_string, store_name, total_sum, 
                 purchase_date, items_summary, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (h, qs, store, total, date, items_desc, comment))
    
    conn.commit()
    conn.close()


def main():
    args = sys.argv[1:]
    
    # Обработка --history
    if args and args[0] == "--history":
        init_db()
        limit = 20
        if len(args) > 1 and args[1].isdigit():
            limit = int(args[1])
        print(show_history(limit))
        return

    if args and args[0] == "--add":
        # python3 proverkacheka_client.py --add СУММА "ТОВАР×..." [МАГАЗИН] [КОММЕНТАРИЙ] [ДАТА]
        # Также поддерживает именованные: --add 9 "Товар" --date 2026-07-15 --store Магнит --comment "[сэр]"
        init_db()
        total = float(args[1]) if len(args) > 1 else 0
        items = args[2] if len(args) > 2 else ""
        store = ""
        comment = ""
        purchase_date = datetime.now(NSK_TZ).strftime("%Y-%m-%d")

        # Сначала пробуем именованные аргументы
        i = 3
        named_mode = any(a.startswith("--") for a in args[3:])
        if named_mode:
            while i < len(args):
                if args[i] == "--store" and i + 1 < len(args):
                    store = args[i + 1]; i += 2
                elif args[i] == "--comment" and i + 1 < len(args):
                    comment = args[i + 1]; i += 2
                elif args[i] == "--date" and i + 1 < len(args):
                    purchase_date = args[i + 1]; i += 2
                else:
                    i += 1  # неизвестный флаг — пропускаем
        else:
            # Fallback: позиционные (старый формат)
            store = args[3] if len(args) > 3 else ""
            comment = args[4] if len(args) > 4 else ""
            purchase_date = args[5] if len(args) > 5 else datetime.now(NSK_TZ).strftime("%Y-%m-%d")

        add_manual_receipt(total, items, store, purchase_date, comment)
        print(f"✅ Добавлена ручная запись: {purchase_date} | {total}₽ — {items}")
        return

    if not args:
        print("")
        print("Ручное добавление (--add): указывай количество через ×")
        print("  Пример: --add 687 \"картошка×1кг, морковь×3шт, лук×3шт, хлеб×1шт, сигареты×1п, молоко×1шт, сахар×1кг\"")
        print("  С датой: --add 9 \"Пакет-майка 5кг×1\" --date 2026-07-15 --comment \"[сэр]\" --store Магнит")
        print("  Или позиционно: --add 9 \"Товар\" \"Магазин\" \"[коммент]\" 2026-07-15")
        print("")
        print("Использование:")
        print("  python3 proverkacheka_client.py \"t=...&s=...&fn=...&i=...&fp=...&n=1\"")
        print("  echo \"t=...\" | python3 proverkacheka_client.py")
        print("  python3 proverkacheka_client.py --no-cache \"t=...\"")
        print("  python3 proverkacheka_client.py --history [N]")
        print("  python3 proverkacheka_client.py --add СУММА \"ТОВАР×КОЛ-ВО, ...\" [МАГАЗИН] [КОММЕНТАРИЙ] [ГГГГ-ММ-ДД]")
        sys.exit(1)
    
    use_cache = True
    qr_args = list(args)
    if qr_args and qr_args[0] == "--no-cache":
        use_cache = False
        qr_args.pop(0)
    
    qr = qr_args[0] if qr_args else sys.stdin.read().strip()
    
    init_db()
    
    print(f"🧾 Проверка чека через proverkacheka.com API...")
    
    ticket = None
    
    if use_cache:
        print("🔍 Проверка кэша...")
        ticket = check_cache(qr)
    
    if ticket is not None:
        print("✅ Найден в кэше!")
    else:
        print("🌐 Запрос к API...")
        ticket = get_ticket_from_qr(qr, use_cache=use_cache)
    
    if ticket.get("code") == 1:
        print(pretty_print(ticket))
    else:
        print(f"❌ Ошибка: {ticket}")
    
    # Сохранить JSON
    with open("receipt.json", "w", encoding="utf-8") as f:
        json.dump(ticket, f, ensure_ascii=False, indent=2)
    print(f"\n📁 Сохранён: receipt.json")


if __name__ == "__main__":
    main()
