#!/usr/bin/env python3
"""Отчёт по расходам (чеки) и доходам из БД receipt-cache."""

import sqlite3
import csv
import json
import os
import sys
import argparse
import datetime
from collections import defaultdict

# ─── Database ──────────────────────────────────────────────────────────
DB_PATH = os.path.expanduser("~/.local/share/receipt-cache/receipts.db")


def get_db():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: БД не найдена: {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Helpers ───────────────────────────────────────────────────────────

def fmt_money(value):
    """Форматировать сумму: 1 234.56 ₽"""
    if value is None:
        return "—"
    return f"{value:,.2f}".replace(",", " ")


def fmt_short_money(value):
    """Форматировать сумму без копеек, если целая."""
    if value is None:
        return "—"
    if value == int(value):
        return f"{int(value):,}".replace(",", " ")
    return f"{value:,.2f}".replace(",", " ")


def parse_date(date_str: str):
    """Парсить purchase_date (ISO с T или без)."""
    if not date_str:
        return None
    date_str = date_str.strip()
    if "T" in date_str:
        return datetime.datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def detect_person(comment: str) -> str:
    """Определить человека по comment."""
    if not comment:
        return "общее"
    c = comment.lower()
    if "[сэр]" in c or "[ser]" in c:
        return "сэр"
    if "[жена]" in c or "[zhena]" in c or "[ж]" in c:
        return "жена"
    return "общее"


def resolve_date_range(args):
    """Определить (date_from, date_to) по аргументам. Возвращает кортеж (date_from, date_to)."""
    today = datetime.date.today()

    # --period
    if args.period:
        p = args.period.upper()
        if p == "TODAY":
            return today, today
        elif p == "WEEK":
            start = today - datetime.timedelta(days=today.weekday())
            return start, today
        elif p == "MONTH":
            start = today.replace(day=1)
            return start, today
        # ALL — возвращаем None, None (весь диапазон)

    # --days N
    if args.days is not None:
        start = today - datetime.timedelta(days=args.days - 1)
        return start, today

    # --from / --to
    date_from = args.date_from
    date_to = args.date_to
    if date_from or date_to:
        if date_from:
            try:
                date_from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
            except ValueError:
                print(f"ERROR: неверный формат --from: {date_from} (нужно YYYY-MM-DD)", file=sys.stderr)
                sys.exit(1)
        else:
            date_from_dt = datetime.date(2000, 1, 1)

        if date_to:
            try:
                date_to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
            except ValueError:
                print(f"ERROR: неверный формат --to: {date_to} (нужно YYYY-MM-DD)", file=sys.stderr)
                sys.exit(1)
        else:
            date_to_dt = today

        return date_from_dt, date_to_dt

    # По умолчанию — всё
    return None, None


def filter_by_date(rows, date_from, date_to, date_field="date"):
    """Отфильтровать список словарей по полю date_field."""
    if date_from is None and date_to is None:
        return rows
    result = []
    for r in rows:
        d_str = r.get(date_field)
        if not d_str:
            continue
        d = parse_date(d_str) if date_field == "purchase_date" else d_str
        if isinstance(d, str):
            try:
                d = datetime.datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                continue
        if d is None:
            continue
        if date_from and d < date_from:
            continue
        if date_to and d > date_to:
            continue
        result.append(r)
    return result


# ─── Data fetching ─────────────────────────────────────────────────────

def fetch_expenses(cursor, date_from, date_to):
    """Выбрать все расходы (history) за период."""
    rows = []
    cursor.execute("SELECT * FROM history ORDER BY purchase_date DESC")
    for r in cursor.fetchall():
        d = parse_date(r["purchase_date"])
        if d is None:
            continue
        if date_from and d < date_from:
            continue
        if date_to and d > date_to:
            continue
        rows.append({
            "id": r["id"],
            "date": d.isoformat(),
            "date_obj": d,
            "store_name": r["store_name"] or "—",
            "total_sum": r["total_sum"],
            "items_summary": r["items_summary"] or "",
            "comment": r["comment"] or "",
            "qr_string": r["qr_string"] or "",
            "type": "expense",
            "person": detect_person(r["comment"]),
        })
    return rows


def fetch_earnings(cursor, date_from, date_to):
    """Выбрать все доходы (earnings) за период."""
    rows = []
    cursor.execute("SELECT * FROM earnings ORDER BY date DESC")
    for r in cursor.fetchall():
        try:
            d = datetime.datetime.strptime(r["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if date_from and d < date_from:
            continue
        if date_to and d > date_to:
            continue
        rows.append({
            "id": r["id"],
            "date": r["date"],
            "date_obj": d,
            "source": r["source"] or "—",
            "hours": r["hours"],
            "rate": r["rate"],
            "total": r["total"],
            "comment": r["comment"] or "",
            "type": "earning",
            "person": "—",
        })
    return rows


# ─── Print helpers ─────────────────────────────────────────────────────

def build_table(widths):
    """Вернуть функции для отрисовки таблицы с заданными ширинами колонок."""

    def hline(left, mid, right):
        parts = [left]
        for i, w in enumerate(widths):
            parts.append("─" * (w + 2))
            parts.append(mid if i < len(widths) - 1 else right)
        return "".join(parts)

    def row(cells, align=None):
        if align is None:
            align = ["<"] * len(cells)
        parts = ["│"]
        for cell, w, a in zip(cells, widths, align):
            parts.append(f" {cell:>{w}} │" if a == ">" else f" {cell:<{w}} │")
        return "".join(parts)

    return hline, row


def print_summary_block(title, items, total_label="Итого"):
    """Вывести сводный блок с разделителем.

    Элементы items — кортежи (label, value).
    Если label пустая строка — выводится пустая строка (отступ).
    Если value пустая строка — выводится label как есть (для разделителей).
    Если label и value оба непустые — форматируется колонками.
    """
    if not items:
        print(f"  {title}: (нет данных)")
        return

    print(f"  {title}:")
    for entry in items:
        if len(entry) == 1 or (len(entry) == 2 and entry[1] == ""):
            print(f"    {entry[0]}")
        elif len(entry) == 2:
            label, value = entry
            print(f"    {label:<30} {value}")
    print()


# ─── Report builders ───────────────────────────────────────────────────

def build_expense_summary(expenses):
    """Общая сводка по расходам."""
    if not expenses:
        return 0, 0, []
    total = sum(e["total_sum"] or 0 for e in expenses)
    count = len(expenses)
    avg = total / count if count else 0
    return count, total, avg


def build_earning_summary(earnings):
    """Общая сводка по доходам."""
    if not earnings:
        return 0, 0, 0, 0
    total = sum(e["total"] or 0 for e in earnings)
    count = len(earnings)
    avg = total / count if count else 0
    total_hours = sum(e["hours"] or 0 for e in earnings)
    return count, total, avg, total_hours


def group_by_day(expenses, earnings):
    """Сгруппировать по дням."""
    days = defaultdict(lambda: {"expenses": [], "earnings": [], "expense_total": 0.0, "earning_total": 0.0})

    for e in expenses:
        d = e["date"]
        days[d]["expenses"].append(e)
        days[d]["expense_total"] += e["total_sum"] or 0

    for e in earnings:
        d = e["date"]
        days[d]["earnings"].append(e)
        days[d]["earning_total"] += e["total"] or 0

    return sorted(days.items(), key=lambda x: x[0], reverse=True)


def group_by_store(expenses):
    """Сгруппировать по магазинам."""
    stores = defaultdict(lambda: {"count": 0, "total": 0.0})
    for e in expenses:
        name = e["store_name"]
        stores[name]["count"] += 1
        stores[name]["total"] += e["total_sum"] or 0
    return sorted(stores.items(), key=lambda x: -x[1]["total"])


def group_by_person(expenses):
    """Сгруппировать по людям."""
    people = defaultdict(lambda: {"count": 0, "total": 0.0})
    for e in expenses:
        p = e["person"]
        people[p]["count"] += 1
        people[p]["total"] += e["total_sum"] or 0
    return sorted(people.items(), key=lambda x: -x[1]["total"])


# ─── Output modes ──────────────────────────────────────────────────────

def print_summary(expenses, earnings, date_from, date_to):
    """Краткая сводка (режим по умолчанию)."""
    print(f"  Чековый отчёт: {date_from_label(date_from, date_to)}")
    print()

    e_cnt, e_total, e_avg = build_expense_summary(expenses)
    d_cnt, d_total, d_avg, d_hours = build_earning_summary(earnings)

    items = []
    if expenses:
        items.append(("Количество покупок", str(e_cnt)))
        items.append(("Сумма расходов", f"{fmt_money(e_total)} ₽"))
        items.append(("Средний чек", f"{fmt_money(e_avg)} ₽"))
    else:
        items.append(("Расходы", "нет данных"))

    if earnings:
        items.append((""))
        items.append(("Количество смен", str(d_cnt)))
        items.append(("Сумма доходов", f"{fmt_money(d_total)} ₽"))
        items.append(("Средний доход/смена", f"{fmt_money(d_avg)} ₽"))
        items.append(("Всего часов", f"{d_hours:.1f}"))
        items.append(("Средняя ставка", f"{fmt_money(d_total / d_hours if d_hours else 0)} ₽/ч"))
    else:
        items.append(("Доходы", "нет данных"))

    if expenses and earnings:
        balance = d_total - e_total
        items.append((""))
        items.append(("────────────────────────────────", "──────────"))
        if balance >= 0:
            items.append(("Разница учтённых доходов/расходов", f"+{fmt_money(balance)} ₽"))
        else:
            items.append(("Разница учтённых доходов/расходов", f"{fmt_money(balance)} ₽"))

    print_summary_block("Сводка", items)


def print_detail(expenses, earnings):
    """Детальный список всех записей."""
    if expenses:
        print(f"  Расходы ({len(expenses)} записей):")
        print()

        widths = [4, 12, 28, 14, 22]
        hline, row = build_table(widths)
        headers = ["#", "Дата", "Магазин", "Сумма", "Кто"]

        print(hline("┌", "┬", "┐"))
        print(row(headers))
        print(hline("├", "┼", "┤"))
        total = 0.0
        for i, e in enumerate(expenses, 1):
            person_short = {"сэр": "сэр", "жена": "жена", "общее": "общ"}.get(e["person"], e["person"])
            print(row([
                str(i), e["date"],
                e["store_name"][:26],
                fmt_money(e["total_sum"]),
                person_short,
            ], [">", "<", "<", ">", "<"]))
            total += e["total_sum"] or 0

        print(hline("├", "┼", "┤"))
        print(row(["", "", "ИТОГО", fmt_money(total), ""], [">", "<", "<", ">", "<"]))
        print(hline("└", "┴", "┘"))
        print()

    if earnings:
        print(f"  Доходы ({len(earnings)} записей):")
        print()

        widths = [4, 12, 20, 10, 12, 12, 24]
        hline, row = build_table(widths)
        headers = ["#", "Дата", "Источник", "Часы", "Ставка", "Начислено", "Комментарий"]

        print(hline("┌", "┬", "┐"))
        print(row(headers))
        print(hline("├", "┼", "┤"))
        total = 0.0
        for i, e in enumerate(earnings, 1):
            print(row([
                str(i), e["date"], e["source"][:18],
                f"{e['hours']:.1f}", f"{fmt_money(e['rate'])}",
                fmt_money(e["total"]),
                (e["comment"] or "")[:22],
            ], [">", "<", "<", ">", ">", ">", "<"]))
            total += e["total"] or 0

        print(hline("├", "┼", "┤"))
        print(row(["", "", "ИТОГО", "", "", fmt_money(total), ""], [">", "<", "<", ">", ">", ">", "<"]))
        print(hline("└", "┴", "┘"))
        print()


def print_by_day(expenses, earnings):
    """Сводка по дням."""
    days = group_by_day(expenses, earnings)

    if not days:
        print("  (нет данных)")
        return

    widths = [12, 16, 16, 16, 16]
    hline, row = build_table(widths)
    headers = ["Дата", "Расходы", "Доходы", "Разница", "Покупок"]

    print(hline("┌", "┬", "┐"))
    print(row(headers))
    print(hline("├", "┼", "┤"))

    total_exp = 0.0
    total_earn = 0.0
    total_purchases = 0

    for day, data in days:
        exp_total = data["expense_total"]
        earn_total = data["earning_total"]
        exp_count = len(data["expenses"])
        bal = earn_total - exp_total
        bal_str = f"+{fmt_money(bal)}" if bal >= 0 else fmt_money(bal)

        print(row([
            day,
            fmt_money(exp_total),
            fmt_money(earn_total) if earn_total > 0 else "—",
            bal_str,
            str(exp_count),
        ], ["<", ">", ">", ">", ">"]))
        total_exp += exp_total
        total_earn += earn_total
        total_purchases += exp_count

    print(hline("├", "┼", "┤"))
    total_bal = total_earn - total_exp
    total_bal_str = f"+{fmt_money(total_bal)}" if total_bal >= 0 else fmt_money(total_bal)
    print(row([
        "ИТОГО",
        fmt_money(total_exp),
        fmt_money(total_earn) if total_earn > 0 else "—",
        total_bal_str,
        str(total_purchases),
    ], ["<", ">", ">", ">", ">"]))
    print(hline("└", "┴", "┘"))
    print()


def print_by_store(expenses):
    """Сводка по магазинам."""
    stores = group_by_store(expenses)

    if not stores:
        print("  (нет данных)")
        return

    max_name = max(len(s[0][:40]) for s in stores)
    max_name = max(max_name, len("Магазин"))
    widths = [max_name, 10, 16, 12]
    hline, row = build_table(widths)
    headers = ["Магазин", "Покупок", "Сумма", "%"]

    grand_total = sum(s[1]["total"] for s in stores)

    print(hline("┌", "┬", "┐"))
    print(row(headers))
    print(hline("├", "┼", "┤"))

    for name, data in stores:
        pct = (data["total"] / grand_total * 100) if grand_total else 0
        print(row([
            name[:40],
            str(data["count"]),
            fmt_money(data["total"]),
            f"{pct:.1f}%",
        ], ["<", ">", ">", ">"]))

    print(hline("├", "┼", "┤"))
    print(row(["ИТОГО", str(len(expenses)), fmt_money(grand_total), "100.0%"], ["<", ">", ">", ">"]))
    print(hline("└", "┴", "┘"))
    print()


def print_by_person(expenses, earnings):
    """Сводка по людям."""
    people_exp = group_by_person(expenses)

    if not people_exp:
        print("  (нет данных по расходам)")
        return

    widths = [10, 14, 16, 14]
    hline, row = build_table(widths)
    headers = ["Кто", "Покупок", "Сумма", "%"]

    grand_total = sum(p[1]["total"] for p in people_exp)

    print(hline("┌", "┬", "┐"))
    print(row(headers))
    print(hline("├", "┼", "┤"))

    for person, data in people_exp:
        pct = (data["total"] / grand_total * 100) if grand_total else 0
        print(row([
            person,
            str(data["count"]),
            fmt_money(data["total"]),
            f"{pct:.1f}%",
        ], ["<", ">", ">", ">"]))

    print(hline("├", "┼", "┤"))
    print(row(["ИТОГО", str(len(expenses)), fmt_money(grand_total), "100.0%"], ["<", ">", ">", ">"]))
    print(hline("└", "┴", "┘"))
    print()


def print_by_category(cursor, date_from, date_to):
    """Сводка по категориям товаров.

    JOIN history → categories, группировка по категории.
    Если таблицы categories ИЛИ колонки category_id нет — сообщение и return.
    """
    # Проверяем, что таблица categories существует
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
    if not cursor.fetchone():
        print("  Категории: таблица categories не найдена (старая БД)")
        print()
        return

    # Проверяем, что колонка category_id есть в history
    cursor.execute("PRAGMA table_info(history)")
    cols = [row["name"] for row in cursor.fetchall()]
    if "category_id" not in cols:
        print("  Категории: колонка category_id не найдена в history (старая БД)")
        print()
        return

    # Формируем условие по дате
    conditions = []
    params = []
    if date_from:
        conditions.append("h.purchase_date >= ?")
        params.append(date_from.isoformat())
    if date_to:
        conditions.append("h.purchase_date <= ?")
        params.append(date_to.isoformat())

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    # Запрос: категория → сумма, количество
    query = f"""
        SELECT
            COALESCE(c.name, 'Без категории') AS category,
            COUNT(h.id) AS count,
            SUM(h.total_sum) AS total
        FROM history h
        LEFT JOIN categories c ON h.category_id = c.id
        {where}
        GROUP BY c.name
        ORDER BY total DESC
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        print("  Категории: нет данных")
        print()
        return

    grand_total = sum(r["total"] for r in rows if r["total"] is not None) or 0
    if grand_total == 0:
        print("  Категории: суммарные расходы равны нулю")
        print()
        return

    # Определяем ширину колонки категории
    max_cat = max(len(r["category"]) for r in rows)
    max_cat = max(max_cat, len("Категория"))

    widths = [max_cat, 10, 16, 12]
    hline, row = build_table(widths)
    headers = ["Категория", "Покупок", "Сумма", "%"]

    print(hline("┌", "┬", "┐"))
    print(row(headers))
    print(hline("├", "┼", "┤"))

    for r in rows:
        total = r["total"] or 0
        pct = (total / grand_total * 100) if grand_total else 0
        print(row([
            r["category"],
            str(r["count"]),
            fmt_money(total),
            f"{pct:.1f}%",
        ], ["<", ">", ">", ">"]))
        print(hline("├", "┼", "┤"))

    print(row(["ИТОГО", str(sum(r["count"] for r in rows)), fmt_money(grand_total), "100.0%"], ["<", ">", ">", ">"]))
    print(hline("└", "┴", "┘"))
    print()


def print_balance(expenses, earnings):
    """Разница учтённых доходов и расходов."""
    e_cnt, e_total, e_avg = build_expense_summary(expenses)
    d_cnt, d_total, d_avg, d_hours = build_earning_summary(earnings)

    print(f"  Разница учтённых доходов/расходов:")
    print()
    items = []
    if earnings:
        items.append(("Доходы", f"{fmt_money(d_total)} ₽"))
        items.append(("  смен", str(d_cnt)))
        items.append(("  часов", f"{d_hours:.1f}"))
        items.append(("  средняя ставка", f"{fmt_money(d_total / d_hours if d_hours else 0)} ₽/ч"))
        items.append((""))
    if expenses:
        items.append(("Расходы", f"{fmt_money(e_total)} ₽"))
        items.append(("  покупок", str(e_cnt)))
        items.append(("  средний чек", f"{fmt_money(e_avg)} ₽"))
        items.append((""))

    if expenses and earnings:
        balance = d_total - e_total
        items.append(("──────────────────────", "────────────"))
        if balance >= 0:
            items.append(("Разница учтённых доходов/расходов", f"+{fmt_money(balance)} ₽"))
        else:
            items.append(("Разница (записанные доходы − расходы)", f"{fmt_money(balance)} ₽"))
        items.append((""))
        items.append(("Примечание: учитываются только записанные в систему доходы", ""))
        items.append(("(подработки). Полный баланс сэра система не знает.", ""))

    print_summary_block("", items)


def export_csv_data(expenses, earnings, filepath):
    """Экспорт в CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Расходы
        if expenses:
            writer.writerow(["Тип", "Дата", "Магазин", "Сумма", "Кто", "Комментарий", "Товары"])
            for e in expenses:
                writer.writerow([
                    "расход", e["date"], e["store_name"],
                    e["total_sum"], e["person"], e["comment"],
                    e["items_summary"],
                ])
            writer.writerow([])

        # Доходы
        if earnings:
            writer.writerow(["Тип", "Дата", "Источник", "Часы", "Ставка", "Начислено", "Комментарий"])
            for e in earnings:
                writer.writerow([
                    "доход", e["date"], e["source"],
                    e["hours"], e["rate"], e["total"],
                    e["comment"],
                ])

    rows_count = len(expenses) + len(earnings)
    print(f"Экспортировано: {len(expenses)} расходов + {len(earnings)} доходов = {rows_count} записей → {filepath}")


def build_json_output(expenses, earnings, date_from, date_to, args):
    """Построить словарь для JSON-вывода."""
    e_cnt, e_total, e_avg = build_expense_summary(expenses)
    d_cnt, d_total, d_avg, d_hours = build_earning_summary(earnings)

    out = {
        "meta": {
            "date_from": date_from.isoformat() if date_from else "all",
            "date_to": date_to.isoformat() if date_to else "all",
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "expenses_count": e_cnt,
            "expenses_total": round(e_total, 2),
            "expenses_avg": round(e_avg, 2),
            "earnings_count": d_cnt,
            "earnings_total": round(d_total, 2),
            "earnings_avg": round(d_avg, 2),
            "earnings_hours": round(d_hours, 1),
        },
    }

    if args.detail or args.by_day or args.by_store or args.by_person:
        out["expenses"] = [
            {
                "id": e["id"],
                "date": e["date"],
                "store_name": e["store_name"],
                "total_sum": e["total_sum"],
                "person": e["person"],
                "comment": e["comment"],
                "items_summary": e["items_summary"],
            }
            for e in expenses
        ]
        out["earnings"] = [
            {
                "id": e["id"],
                "date": e["date"],
                "source": e["source"],
                "hours": e["hours"],
                "rate": e["rate"],
                "total": e["total"],
                "comment": e["comment"],
            }
            for e in earnings
        ]

    if expenses and earnings:
        out["meta"]["balance"] = round(d_total - e_total, 2)

    if args.by_day:
        days = group_by_day(expenses, earnings)
        out["by_day"] = [
            {
                "date": day,
                "expenses_count": len(data["expenses"]),
                "expenses_total": round(data["expense_total"], 2),
                "earnings_count": len(data["earnings"]),
                "earnings_total": round(data["earning_total"], 2),
                "balance": round(data["earning_total"] - data["expense_total"], 2),
            }
            for day, data in days
        ]

    if args.by_store:
        stores = group_by_store(expenses)
        grand = sum(s[1]["total"] for s in stores) or 1
        out["by_store"] = [
            {
                "store_name": name,
                "count": data["count"],
                "total": round(data["total"], 2),
                "percent": round(data["total"] / grand * 100, 1),
            }
            for name, data in stores
        ]

    if args.by_person:
        people = group_by_person(expenses)
        grand = sum(p[1]["total"] for p in people) or 1
        out["by_person"] = [
            {
                "person": person,
                "count": data["count"],
                "total": round(data["total"], 2),
                "percent": round(data["total"] / grand * 100, 1),
            }
            for person, data in people
        ]

    if args.by_category:
        # Требуется live cursor — открываем соединение повторно
        conn2 = get_db()
        c2 = conn2.cursor()

        # Проверяем существование таблицы и колонки
        c2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        has_table = c2.fetchone() is not None
        if has_table:
            c2.execute("PRAGMA table_info(history)")
            cols = [row["name"] for row in c2.fetchall()]
            has_column = "category_id" in cols
        else:
            has_column = False

        if has_table and has_column:
            conditions = []
            params = []
            if date_from:
                conditions.append("h.purchase_date >= ?")
                params.append(date_from.isoformat())
            if date_to:
                conditions.append("h.purchase_date <= ?")
                params.append(date_to.isoformat())
            where = ""
            if conditions:
                where = "WHERE " + " AND ".join(conditions)

            query = f"""
                SELECT
                    COALESCE(c.name, 'Без категории') AS category,
                    COUNT(h.id) AS count,
                    SUM(h.total_sum) AS total
                FROM history h
                LEFT JOIN categories c ON h.category_id = c.id
                {where}
                GROUP BY c.name
                ORDER BY total DESC
            """
            c2.execute(query, params)
            cat_rows = c2.fetchall()
            total_all = sum(r["total"] for r in cat_rows if r["total"]) or 1
            out["by_category"] = [
                {
                    "category": r["category"],
                    "count": r["count"],
                    "total": round(r["total"], 2) if r["total"] else 0,
                    "percent": round((r["total"] or 0) / total_all * 100, 1),
                }
                for r in cat_rows
            ]
        conn2.close()

    return out


def print_json_data(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def date_from_label(date_from, date_to):
    """Подпись периода."""
    if date_from and date_to:
        if date_from == date_to:
            return date_from.isoformat()
        return f"{date_from.isoformat()} → {date_to.isoformat()}"
    return "всё время"


# ─── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Отчёт по расходам (чеки) и доходам из БД receipt-cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Примеры:
  %(prog)s                                    Сводка (всё время)
  %(prog)s --period WEEK                      За неделю
  %(prog)s --period MONTH                     За месяц
  %(prog)s --days 3                           Последние 3 дня
  %(prog)s --from 2026-07-15 --to 2026-07-16  Произвольный период
  %(prog)s --period MONTH --balance            Баланс за месяц
  %(prog)s --period WEEK --by-day             По дням за неделю
  %(prog)s --period MONTH --by-store          По магазинам
  %(prog)s --period MONTH --by-person         По людям
  %(prog)s --period MONTH --by-category       По категориям
  %(prog)s --period ALL --detail              Все записи детально
  %(prog)s --period MONTH --json              В JSON
  %(prog)s --period ALL --csv report.csv      Экспорт в CSV
  %(prog)s --earnings                         Только доходы
  %(prog)s --expenses                         Только расходы
        """
    )

    # Период
    period_g = parser.add_argument_group("Период")
    period_g.add_argument("--period", metavar="PERIOD",
                          choices=["TODAY", "WEEK", "MONTH", "ALL"],
                          help="Период: TODAY, WEEK, MONTH, ALL")
    period_g.add_argument("--days", type=int, metavar="N",
                          help="Последние N дней")
    period_g.add_argument("--from", dest="date_from", metavar="YYYY-MM-DD",
                          help="Начало периода")
    period_g.add_argument("--to", dest="date_to", metavar="YYYY-MM-DD",
                          help="Конец периода")

    # Фильтры
    filter_g = parser.add_argument_group("Фильтры")
    filter_g.add_argument("--expenses", action="store_true", default=False,
                          help="Только расходы")
    filter_g.add_argument("--earnings", action="store_true", default=False,
                          help="Только доходы")

    # Режимы вывода
    mode_g = parser.add_argument_group("Режимы вывода")
    mode_g.add_argument("--summary", action="store_true", default=False,
                        help="Краткая сводка (по умолчанию)")
    mode_g.add_argument("--detail", action="store_true", default=False,
                        help="Детальный список всех записей")
    mode_g.add_argument("--balance", action="store_true", default=False,
                        help="Разница учтённых доходов и расходов")
    mode_g.add_argument("--by-day", "--by_day", action="store_true", default=False,
                        help="Сводка по дням")
    mode_g.add_argument("--by-store", "--by_store", action="store_true", default=False,
                        help="Сводка по магазинам")
    mode_g.add_argument("--by-person", "--by_person", action="store_true", default=False,
                        help="Сводка по людям (сэр/жена/общее)")
    mode_g.add_argument("--by-category", "--by_category", action="store_true", default=False,
                        help="Сводка по категориям товаров")

    # Вывод
    output_g = parser.add_argument_group("Вывод")
    output_g.add_argument("--csv", metavar="FILE",
                          help="Экспорт в CSV")
    output_g.add_argument("--json", action="store_true", default=False,
                          help="Вывод в JSON")

    args = parser.parse_args()

    # Если ничего не указано — краткая сводка
    if not (args.summary or args.detail or args.balance or args.by_day or args.by_store or args.by_person or args.by_category or args.csv or args.json):
        args.summary = True

    # По умолчанию показываем и расходы, и доходы
    if not args.expenses and not args.earnings:
        args.expenses = True
        args.earnings = True

    # Определяем даты
    date_from, date_to = resolve_date_range(args)

    # Подключаемся к БД
    conn = get_db()
    cursor = conn.cursor()

    # Выборка
    expenses = []
    earnings = []

    if args.expenses:
        expenses = fetch_expenses(cursor, date_from, date_to)
    if args.earnings:
        earnings = fetch_earnings(cursor, date_from, date_to)

    # Вывод
    if args.json:
        data = build_json_output(expenses, earnings, date_from, date_to, args)
        print_json_data(data)
        return

    if args.csv:
        export_csv_data(expenses, earnings, os.path.expanduser(args.csv))
        return

    # Если данных нет
    if not expenses and not earnings:
        print(f"  Нет данных за период: {date_from_label(date_from, date_to)}")
        return

    if args.summary:
        print_summary(expenses, earnings, date_from, date_to)

    if args.balance and not args.summary:
        print_balance(expenses, earnings)
    elif args.balance:
        print_balance(expenses, earnings)

    if args.detail:
        print_detail(expenses, earnings)

    if args.by_day:
        print(f"  Сводка по дням:")
        print_by_day(expenses, earnings)

    if args.by_store and expenses:
        print(f"  Сводка по магазинам:")
        print_by_store(expenses)

    if args.by_person and expenses:
        print(f"  Сводка по людям:")
        print_by_person(expenses, earnings)

    if args.by_category:
        print(f"  Сводка по категориям:")
        print_by_category(cursor, date_from, date_to)

    conn.close()


if __name__ == "__main__":
    main()
