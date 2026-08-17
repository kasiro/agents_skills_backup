#!/usr/bin/env python3
"""
ses — Session Search для OpenCode

Утилита для просмотра и поиска по сессиям OpenCode через SQLite с FTS5.
Поддерживает: список сессий, полнотекстовый поиск, инспекцию, статистику.

Использование:
  ses list                  — список сессий
  ses search <query>        — поиск по содержимому
  ses fts <query>           — полнотекстовый поиск (FTS5)
  ses inspect <id>          — детали сессии
  ses stats                 — статистика
  ses db                    — информация о БД
  ses ocdb <args>           — передача аргументов в ocdb
  ses ocdb-check            — проверка ocdb
  ses help                  — справка
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# ─── Конфигурация ────────────────────────────────────────────────────────────

DB_PATH = os.path.expanduser("~/.local/share/opencode/opencode.db")
OCDB_PATH = os.path.expanduser("~/.local/bin/ocdb")
FTS_TABLE = "sessions_fts"
HOME = os.path.expanduser("~")

# ─── Утилиты ──────────────────────────────────────────────────────────────────


def get_db_path():
    """Определяет путь к БД OpenCode."""
    # Проверка env var
    env_db = os.environ.get("OPENCODE_DB")
    if env_db and os.path.exists(env_db):
        return env_db
    # Стандартный путь
    if os.path.exists(DB_PATH):
        return DB_PATH
    # Поиск других opencode*.db
    db_dir = os.path.dirname(DB_PATH)
    if os.path.isdir(db_dir):
        dbs = sorted(
            [f for f in os.listdir(db_dir) if f.startswith("opencode") and f.endswith(".db")],
            key=lambda f: os.path.getmtime(os.path.join(db_dir, f)),
            reverse=True,
        )
        if dbs:
            return os.path.join(db_dir, dbs[0])
    return DB_PATH


def short_id(session_id, length=12, force_full=False):
    """Укорачивает ID сессии для отображения (только если force_full=False)."""
    if force_full:
        return session_id or ""
    if session_id and len(session_id) > length + 3:
        return session_id[:length] + "..."
    return session_id or ""


def fmt_time(ts_ms):
    """Форматирует timestamp в читаемую дату."""
    if not ts_ms:
        return ""
    try:
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - dt
        if diff.days == 0:
            if diff.seconds < 60:
                return "только что"
            elif diff.seconds < 3600:
                mins = diff.seconds // 60
                return f"{mins}м назад"
            else:
                hours = diff.seconds // 3600
                return f"{hours}ч назад"
        elif diff.days == 1:
            return "вчера"
        elif diff.days < 7:
            return f"{diff.days}д назад"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks}н назад"
        else:
            return dt.strftime("%d.%m.%Y")
    except (ValueError, OSError):
        return ""


def fmt_time_full(ts_ms):
    """Форматирует timestamp полностью."""
    if not ts_ms:
        return "—"
    try:
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "—"


def shorten_path(path, home=HOME):
    """Сокращает путь, заменяя home на ~."""
    if not path:
        return ""
    if path.startswith(home):
        return "~" + path[len(home):]
    return path


def truncate(text, max_len=80):
    """Обрезает текст до max_len с многоточием."""
    if not text:
        return ""
    text = str(text).replace("\n", " ").replace("\r", "")
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


def make_snippet(content, query, radius=40, max_len=100):
    """Вырезает фрагмент контента вокруг первого вхождения query."""
    if not content:
        return ""
    content = str(content)
    idx = content.lower().find(query.lower())
    if idx < 0:
        return ""
    start = max(0, idx - radius)
    end = min(len(content), idx + len(query) + radius)
    snippet = "..." + content[start:end].replace("\n", " ") + "..."
    return truncate(snippet, max_len)


def pluralize(n, singular, plural=None):
    """Склонение существительных."""
    if plural is None:
        plural = singular + "ов" if singular[-1] not in "ая" else singular + "и"
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {singular}"
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return f"{n} {plural if plural else singular + 'а'}"
    else:
        return f"{n} {plural if plural else singular + 'ов'}"


def format_tokens(tokens):
    """Форматирует количество токенов."""
    if tokens is None:
        return "—"
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    return str(tokens)


def format_cost(cost):
    """Форматирует стоимость в $."""
    if cost is None or cost == 0:
        return "—"
    return f"${cost:.4f}"


# ─── Работа с БД ─────────────────────────────────────────────────────────────


def connect(db_path=None, readonly=True):
    """Подключается к БД OpenCode."""
    path = db_path or get_db_path()
    if not os.path.exists(path):
        print(f"❌ База данных не найдена: {path}", file=sys.stderr)
        print(f"   Ищите здесь: ~/.local/share/opencode/opencode.db", file=sys.stderr)
        sys.exit(1)
    try:
        if readonly:
            # read-only режим (WAL совместим)
            uri = f"file:{path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
        else:
            conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Ошибка подключения к БД: {e}", file=sys.stderr)
        sys.exit(1)


def ensure_fts(conn):
    """Создаёт FTS5 виртуальную таблицу, если её нет. conn должен быть read-write."""
    try:
        # Проверяем существование FTS таблицы
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (FTS_TABLE,),
        )
        if cursor.fetchone():
            return

        # Определяем схему — есть ли таблица message или session_message
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='message'"
        )
        has_message = cursor.fetchone() is not None

        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='session_message'"
        )
        has_sm = cursor.fetchone() is not None

        if has_message:
            conn.executescript(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE} USING fts5(
                    session_id UNINDEXED,
                    title,
                    content,
                    tokenize='unicode61 remove_diacritics 2'
                );

                INSERT OR IGNORE INTO {FTS_TABLE}(session_id, title, content)
                SELECT 
                    s.id,
                    COALESCE(s.title, ''),
                    COALESCE(m.data, '')
                FROM session s
                LEFT JOIN message m ON m.session_id = s.id;
            """)
            print("✅ FTS5 индекс создан на базе таблицы message.", file=sys.stderr)
        elif has_sm:
            conn.executescript(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE} USING fts5(
                    session_id UNINDEXED,
                    title,
                    content,
                    tokenize='unicode61 remove_diacritics 2'
                );

                INSERT OR IGNORE INTO {FTS_TABLE}(session_id, title, content)
                SELECT 
                    s.id,
                    COALESCE(s.title, ''),
                    COALESCE(sm.data, '')
                FROM session s
                LEFT JOIN session_message sm ON sm.session_id = s.id;
            """)
            print("✅ FTS5 индекс создан на базе таблицы session_message.", file=sys.stderr)
        else:
            # Пробуем собрать из part таблицы
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='part'"
            )
            has_part = cursor.fetchone() is not None
            if has_part:
                conn.executescript(f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE} USING fts5(
                        session_id UNINDEXED,
                        title,
                        content,
                        tokenize='unicode61 remove_diacritics 2'
                    );

                    INSERT OR IGNORE INTO {FTS_TABLE}(session_id, title, content)
                    SELECT 
                        s.id,
                        COALESCE(s.title, ''),
                        COALESCE(p.data, '')
                    FROM session s
                    LEFT JOIN part p ON p.session_id = s.id;
                """)
                print("✅ FTS5 индекс создан на базе таблицы part.", file=sys.stderr)
            else:
                # Минимальный FTS только с заголовками
                conn.executescript(f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE} USING fts5(
                        session_id UNINDEXED,
                        title,
                        content,
                        tokenize='unicode61 remove_diacritics 2'
                    );

                    INSERT OR IGNORE INTO {FTS_TABLE}(session_id, title, content)
                    SELECT 
                        s.id,
                        COALESCE(s.title, ''),
                        COALESCE(s.title, '')
                    FROM session s;
                """)
                print("✅ FTS5 индекс создан на базе заголовков сессий.", file=sys.stderr)
        
        conn.commit()

    except sqlite3.OperationalError as e:
        if "no such module: fts5" in str(e):
            print("⚠️  FTS5 не поддерживается вашей сборкой SQLite.", file=sys.stderr)
            print("   Используйте `ses search` для базового поиска (LIKE).", file=sys.stderr)
        else:
            print(f"⚠️  Не удалось создать FTS5 индекс: {e}", file=sys.stderr)
            print("   Используйте `ses search` для базового поиска.", file=sys.stderr)
    except sqlite3.DatabaseError as e:
        print(f"⚠️  Ошибка БД при создании FTS5: {e}", file=sys.stderr)


def rebuild_fts(conn):
    """Перестраивает FTS5 индекс."""
    try:
        conn.execute(f"DELETE FROM {FTS_TABLE}")
        conn.execute(f"INSERT INTO {FTS_TABLE}(session_id, title, content) "
                     "SELECT s.id, COALESCE(s.title, ''), '' FROM session s")
        conn.commit()
        print("✅ FTS индекс перестроен.")
    except sqlite3.Error as e:
        print(f"❌ Ошибка перестроения FTS: {e}", file=sys.stderr)


def cmd_filter(args):
    """Фильтр сессий через GraphQL (ocdb)."""
    if not os.path.exists(OCDB_PATH):
        print(f"❌ ocdb не найден: {OCDB_PATH}", file=sys.stderr)
        print("   Установите: pip install ocdb", file=sys.stderr)
        sys.exit(1)

    # Строим GraphQL аргументы
    gql_args = []
    if args.title_substring:
        gql_args.append(f'titleSubstr: "{args.title_substring}"')
    if args.search:
        gql_args.append(f'search: "{args.search}"')
    if args.agent:
        gql_args.append(f'agent: "{args.agent}"')
    if args.model:
        gql_args.append(f'modelSubstr: "{args.model}"')
    if args.session_id:
        gql_args.append(f'sessionIdSubstr: "{args.session_id}"')
    if args.limit:
        gql_args.append(f'limit: {args.limit}')
    if args.min_msgs:
        gql_args.append(f'minMsgs: {args.min_msgs}')
    if args.min_input:
        gql_args.append(f'minInput: {args.min_input}')
    if args.min_output:
        gql_args.append(f'minOutput: {args.min_output}')
    if args.date_from:
        gql_args.append(f'dateFrom: "{args.date_from}"')
    if args.date_to:
        gql_args.append(f'dateTo: "{args.date_to}"')
    if args.order_by:
        gql_args.append(f'orderBy: "{args.order_by}"')
    if args.order_dir:
        gql_args.append(f'orderDir: "{args.order_dir}"')

    args_str = ", ".join(gql_args)
    gql = f'{{ sessions({args_str}) {{ id title directory agent timeCreated model {{ provider modelId }} tokensInput tokensOutput cost messageCount }} }}'

    if args.json:
        gql = f'{{ sessions({args_str}) {{ id title directory agent timeCreated tokensInput tokensOutput cost messageCount }} }}'

    # Запускаем ocdb
    cmd = [OCDB_PATH]
    if args.json:
        cmd.append("--json")
    cmd.append(gql)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка ocdb: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)

        output = result.stdout.strip()

        if args.json:
            print(output)
            return

        # Парсим JSON и красиво выводим
        try:
            data = json.loads(output)
            sessions = data.get("data", {}).get("sessions", [])
        except (json.JSONDecodeError, KeyError):
            print(output)
            return

        total = len(sessions)
        if total == 0:
            print("😴 Нет сессий по вашему фильтру.")
            return

        print(f"🔍 Фильтр GraphQL:")
        print(f"   {gql}")
        print()

        for s in sessions:
            sid = s.get("id", "")
            title = s.get("title", "—")
            agent = s.get("agent") or ""
            raw_time = s.get("timeCreated", "")
            try:
                ftime = fmt_time(int(raw_time)) if raw_time else ""
            except (ValueError, TypeError):
                ftime = str(raw_time) if raw_time else ""
            model = s.get("model", {})
            model_str = ""
            if model:
                prov = model.get("provider", "")
                mid = model.get("modelId", "")
                model_str = f"{prov}/{mid}" if prov else mid
            msgs = s.get("messageCount", 0)
            tokens = format_tokens((s.get("tokensInput", 0) or 0) + (s.get("tokensOutput", 0) or 0))
            cost = format_cost(s.get("cost", 0))

            sid_short = short_id(sid, force_full=True)
            print(f"  📄 {sid_short}  {title}")
            print(f"     {ftime}  [{agent}]  {model_str}  {msgs} msg  {tokens} tok  {cost}")
            print()

        print(f"{'='*60}")
        print(f"  Найдено: {total} сессий")

    except FileNotFoundError:
        print(f"❌ ocdb не найден: {OCDB_PATH}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ Таймаут ocdb (>30s)", file=sys.stderr)
        sys.exit(1)


# ─── Команды ──────────────────────────────────────────────────────────────────


def cmd_list(args):
    """Список сессий."""
    conn = connect()
    try:
        conditions = []
        params = []

        # Фильтр по проекту
        if args.project:
            # Определяем текущий проект через git
            try:
                git_root = subprocess.check_output(
                    ["git", "rev-parse", "--show-toplevel"],
                    stderr=subprocess.DEVNULL,
                ).decode().strip()
                conditions.append("s.directory LIKE ?")
                params.append(f"{git_root}%")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Не удалось определить текущий git-проект.", file=sys.stderr)

        # Фильтр по today
        if args.today:
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).timestamp() * 1000
            conditions.append("s.time_created >= ?")
            params.append(int(today_start))

        # Фильтр по days
        if args.days:
            cutoff = (datetime.now(timezone.utc).timestamp() - args.days * 86400) * 1000
            conditions.append("s.time_created >= ?")
            params.append(int(cutoff))

        where = ""
        if conditions:
            where = "WHERE " + " AND ".join(conditions)

        limit = ""
        if not args.all:
            limit = f"LIMIT {args.limit}"

        query = f"""
            SELECT 
                s.id,
                s.title,
                s.directory,
                s.time_created,
                s.agent,
                s.tokens_input,
                s.tokens_output,
                s.cost,
                COALESCE(s.model, '{{}}') as model
            FROM session s
            {where}
            ORDER BY s.time_created DESC
            {limit}
        """

        rows = conn.execute(query, params).fetchall()
        total = len(rows)
        
        if total == 0:
            print("😴 Нет сессий" + (" по вашему запросу." if conditions else "."))
            return

        # Подсчёт сообщений для каждой сессии
        session_ids = [r["id"] for r in rows]
        msg_counts = {}
        try:
            for sid in session_ids:
                msg_count = conn.execute(
                    "SELECT COUNT(*) as cnt FROM message WHERE session_id = ?",
                    (sid,),
                ).fetchone()
                msg_counts[sid] = msg_count["cnt"] if msg_count else 0
        except sqlite3.Error:
            pass

        if args.json:
            output = []
            for r in rows:
                model_data = {}
                try:
                    model_data = json.loads(r["model"]) if r["model"] else {}
                except (json.JSONDecodeError, TypeError):
                    pass
                output.append({
                    "id": r["id"],
                    "title": r["title"],
                    "directory": r["directory"],
                    "time_created": r["time_created"],
                    "time_created_fmt": fmt_time_full(r["time_created"]),
                    "agent": r["agent"],
                    "messages": msg_counts.get(r["id"], 0),
                    "tokens_input": r["tokens_input"],
                    "tokens_output": r["tokens_output"],
                    "cost": r["cost"],
                    "model": model_data.get("id", ""),
                })
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return

        if args.table:
            # Табличный вывод
            header = f"{'ID':<30} {'Название':<50} {'Проект':<30} {'Агент':<12} {'Сообщ':<6} {'Токены':<12} {'Дата':<18}"
            sep = "─" * len(header)
            print(sep)
            print(header)
            print(sep)
            for r in rows:
                sid_short = short_id(r["id"], 28, force_full=True)
                title = truncate(r["title"] or "—", 48)
                proj = shorten_path(r["directory"] or "—", HOME)
                agent = r["agent"] or "—"
                msgs = msg_counts.get(r["id"], 0)
                tokens = format_tokens((r["tokens_input"] or 0) + (r["tokens_output"] or 0))
                ftime = fmt_time_full(r["time_created"])
                print(f"{sid_short:<30} {title:<50} {proj:<30} {agent:<12} {msgs:<6} {tokens:<12} {ftime:<18}")
            print(sep)
        else:
            # Краткий вывод
            for r in rows:
                sid_short = short_id(r["id"], force_full=True)
                title = r["title"] or "—"
                ftime = fmt_time(r["time_created"])
                agent = f"[{r['agent']}]" if r["agent"] else ""
                msgs = msg_counts.get(r["id"], 0)
                tokens_str = format_tokens((r["tokens_input"] or 0) + (r["tokens_output"] or 0))
                cost_str = format_cost(r["cost"])
                print(f"  {sid_short}  {title:<60}  {ftime:<12}  {agent:<12}  {msgs} msg  {tokens_str} tok  {cost_str}")

        print(f"\n{'='*60}")
        print(f"  Всего: {pluralize(total, 'сессия', 'сессий')}")
        if not args.all:
            print(f"  (используйте --all для всех сессий)")
    finally:
        conn.close()


def cmd_search(args):
    """Поиск по сессиям (LIKE + FTS5 fallback)."""
    query = " ".join(args.query)
    if not query:
        print("❌ Укажите поисковый запрос.", file=sys.stderr)
        sys.exit(1)

    # Фильтр по сессии (если указан) — доступен и в FTS5, и в LIKE-fallback
    session_filter = ""
    session_params = []
    if args.session_id:
        session_filter = "AND fts.session_id = ?"
        session_params.append(args.session_id)

    conn = connect()
    try:
        # Пробуем FTS5 сначала
        found_fts = False
        try:
            # Сначала пробуем создать FTS если нет (read-write нужно)
            try:
                rw_conn = connect(readonly=False)
                ensure_fts(rw_conn)
                rw_conn.close()
            except sqlite3.Error:
                pass
            
            fts_query = query
            # Экранирование специальных символов FTS5
            # Пользовательские кавычки — точная фраза
            if '"' in query:
                fts_query = query  # оставляем как есть
            elif " AND " in query.upper() or " OR " in query.upper() or " NOT " in query.upper():
                fts_query = query  # булевы операторы
            elif " " in query and not any(op in query.upper() for op in [" AND ", " OR ", " NOT "]):
                # Фраза с пробелами — оборачиваем в кавычки для точного совпадения
                fts_query = f'"{query}"'
            else:
                fts_query = query

            sql = f"""
                SELECT 
                    fts.session_id,
                    fts.title,
                    fts.content,
                    s.directory,
                    s.time_created,
                    s.agent
                FROM {FTS_TABLE} fts
                JOIN session s ON s.id = fts.session_id
                WHERE {FTS_TABLE} MATCH ?
                {session_filter}
                ORDER BY rank
                LIMIT ?
            """
            limit_val = args.limit if args.limit else 20

            # Фильтр по проекту
            if args.project:
                try:
                    git_root = subprocess.check_output(
                        ["git", "rev-parse", "--show-toplevel"],
                        stderr=subprocess.DEVNULL,
                    ).decode().strip()
                    sql = f"""
                        SELECT 
                            fts.session_id,
                            fts.title,
                            fts.content,
                            s.directory,
                            s.time_created,
                            s.agent
                        FROM {FTS_TABLE} fts
                        JOIN session s ON s.id = fts.session_id
                        WHERE {FTS_TABLE} MATCH ?
                        {session_filter}
                        AND s.directory LIKE ?
                        ORDER BY rank
                        LIMIT ?
                    """
                    rows = conn.execute(sql, (fts_query, *session_params, f"{git_root}%", limit_val)).fetchall()
                except subprocess.CalledProcessError:
                    rows = conn.execute(sql, (fts_query, *session_params, limit_val)).fetchall()
            else:
                rows = conn.execute(sql, (fts_query, *session_params, limit_val)).fetchall()

            if rows:
                found_fts = True
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            rows = []

        # Fallback: LIKE поиск
        if not found_fts:
            conditions = []
            params = []
            
            like_pattern = f"%{query}%"
            # В LIKE-fallback таблица session алиасится как s, а не fts
            like_session_filter = "AND s.id = ?" if args.session_id else ""
            has_message_table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='message'"
            ).fetchone()

            if has_message_table:
                sql = f"""
                    SELECT DISTINCT
                        s.id,
                        s.title,
                        s.directory,
                        s.time_created,
                        s.agent
                    FROM session s
                    LEFT JOIN message m ON m.session_id = s.id
                    WHERE (s.title LIKE ? OR m.data LIKE ?)
                    {like_session_filter}
                    ORDER BY s.time_created DESC
                    LIMIT ?
                """
                rows = conn.execute(sql, (like_pattern, like_pattern, *session_params, args.limit or 20)).fetchall()
            else:
                sql = f"""
                    SELECT 
                        s.id,
                        s.title,
                        s.directory,
                        s.time_created,
                        s.agent
                    FROM session s
                    WHERE s.title LIKE ?
                    {like_session_filter}
                    ORDER BY s.time_created DESC
                    LIMIT ?
                """
                rows = conn.execute(sql, (like_pattern, *session_params, args.limit or 20)).fetchall()

        total = len(rows)
        if total == 0:
            print(f"🔍 Ничего не найдено по запросу «{query}»")
            return

        print(f"🔍 Результаты поиска «{query}»:")
        print()
        
        for r in rows:
            sid_short = short_id(r["session_id"] if found_fts else r["id"], force_full=True)
            title = r["title"] or "—"
            ftime = fmt_time(r["time_created"])
            proj = shorten_path(r["directory"] or "")
            agent = f"[{r['agent']}]" if r["agent"] else ""
            
            # Показываем snippet из контента
            snippet = ""
            if found_fts and r["content"]:
                content = str(r["content"])
                idx = content.lower().find(query.lower())
                if idx >= 0:
                    start = max(0, idx - 40)
                    end = min(len(content), idx + len(query) + 40)
                    snippet = "..." + content[start:end].replace("\n", " ") + "..."
                    snippet = truncate(snippet, 100)
            
            print(f"  📄 {sid_short}")
            print(f"     {title}")
            if proj:
                print(f"     📁 {proj}  {ftime}  {agent}")
            if snippet:
                print(f"     {snippet}")
            print()

        print(f"{'='*50}")
        print(f"  Найдено: {pluralize(total, 'сессия', 'сессий')}")

    finally:
        conn.close()


def cmd_fts(args):
    """Полнотекстовый поиск через FTS5."""
    query = " ".join(args.query)
    if not query:
        print("❌ Укажите поисковый запрос.", file=sys.stderr)
        sys.exit(1)

    # Сначала создаём/обновляем FTS индекс (нужно read-write соединение)
    try:
        rw_conn = connect(readonly=False)
        ensure_fts(rw_conn)
        rw_conn.close()
    except sqlite3.Error as e:
        print(f"⚠️  Не удалось инициализировать FTS: {e}", file=sys.stderr)
        # Продолжаем — возможно FTS уже есть и read-only хватит
    
    # Основной поиск (read-only)
    conn = connect()
    try:
        # Фильтр по days (если указан)
        date_filter = ""
        date_params = []
        if args.days:
            cutoff = (datetime.now(timezone.utc).timestamp() - args.days * 86400) * 1000
            date_filter = "AND s.time_created >= ?"
            date_params.append(int(cutoff))

        # Фильтр по проекту
        project_filter = ""
        project_params = []
        if args.project:
            try:
                git_root = subprocess.check_output(
                    ["git", "rev-parse", "--show-toplevel"],
                    stderr=subprocess.DEVNULL,
                ).decode().strip()
                project_filter = "AND s.directory LIKE ?"
                project_params.append(f"{git_root}%")
            except subprocess.CalledProcessError:
                pass

        # Фильтр по сессии (если указан)
        session_filter = ""
        session_params = []
        if args.session_id:
            session_filter = "AND fts.session_id = ?"
            session_params.append(args.session_id)

        sql = f"""
            SELECT 
                fts.session_id,
                fts.title,
                fts.content,
                s.directory,
                s.time_created,
                s.agent,
                s.tokens_input,
                s.tokens_output,
                s.cost
            FROM {FTS_TABLE} fts
            JOIN session s ON s.id = fts.session_id
            WHERE {FTS_TABLE} MATCH ?
            {session_filter}
            {project_filter}
            {date_filter}
            GROUP BY fts.session_id
            ORDER BY rank
            LIMIT ?
        """
        params = [query] + session_params + project_params + date_params + [args.limit or 20]

        rows = conn.execute(sql, params).fetchall()
        total = len(rows)

        if total == 0:
            print(f"🔍 Ничего не найдено по запросу «{query}»")
            print()
            print("  Подсказки:")
            print("  - Для точной фразы используйте кавычки: ses fts \"точная фраза\"")
            print("  - Для AND/OR/NOT: ses fts \"auth AND jwt\"")
            print("  - Для NEAR: ses fts \"error NEAR/5 timeout\"")
            print("  - Для префикса: ses fts \"auth*\"")
            return

        if args.json:
            output = []
            for r in rows:
                output.append({
                    "id": r["session_id"],
                    "title": r["title"],
                    "snippet": make_snippet(r["content"], query),
                    "directory": r["directory"],
                    "time_created": r["time_created"],
                    "time_created_fmt": fmt_time_full(r["time_created"]),
                    "agent": r["agent"],
                    "tokens_input": r["tokens_input"],
                    "tokens_output": r["tokens_output"],
                    "cost": r["cost"],
                })
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return

        print(f"🔍 FTS5: «{query}»")
        print(f"   Найдено: {pluralize(total, 'сессия', 'сессий')}")
        print()

        for r in rows:
            sid_short = short_id(r["session_id"], force_full=True)
            title = r["title"] or "—"
            ftime = fmt_time(r["time_created"])
            proj = shorten_path(r["directory"] or "")
            agent = f"[{r['agent']}]" if r["agent"] else ""
            snippet = make_snippet(r["content"], query)

            print(f"  📄 {sid_short}  {title}")
            if proj:
                print(f"     📁 {proj}  {ftime}  {agent}")
            if snippet:
                print(f"     📝 {snippet}")
            print()

        if args.limit and total >= args.limit:
            print(f"  (показано первых {args.limit}, используйте --limit для большего)")
        print(f"{'='*50}")

    except sqlite3.OperationalError as e:
        if "no such module: fts5" in str(e):
            print("❌ FTS5 не поддерживается. Используйте `ses search` вместо `ses fts`.", file=sys.stderr)
        else:
            print(f"❌ Ошибка FTS5: {e}", file=sys.stderr)
    finally:
        conn.close()


def _cmd_matches(cmdline, command):
    """Совпадает ли cmdline процесса с командой из part (двусторонняя подстрока).

    cmdline процесса: "python3 /path/to/ses.py current --method process"
    command из part:  "ses current --method process 2>&1" (через обёртку)
    Прямая подстрока не сработает, поэтому:
    1. Если в cmdline есть путь к ses.py — берём хвост после него (аргументы)
       и проверяем его вхождение в command.
    2. Иначе — двусторонняя проверка полных строк.
    """
    if not command:
        return False
    cmdline = cmdline.strip()
    command = command.strip()
    if not cmdline or not command:
        return False

    # 1. Хвост cmdline после пути к скрипту (аргументы ses)
    script_path = os.path.realpath(__file__)
    idx = cmdline.find(script_path)
    if idx >= 0:
        args_part = cmdline[idx + len(script_path):].strip()
        if args_part and (args_part in command or command in args_part):
            return True

    # 2. Двусторонняя подстрока полных строк
    return cmdline in command or command in cmdline


def _resolve_process(conn):
    """Реализация B: сессия процесса, из которого вызвана команда.

    1. /proc/self/cmdline → строка команды C
    2. starttime из /proc/self/stat (+ btime из /proc/stat для перевода в epoch ms)
    3. SQL: part WHERE type='tool' AND tool='bash' AND state.status='running'
       AND state.time.start > now-60s
    4. Фильтр: state.input.command содержит C (по подстроке)
    5. Если кандидатов несколько — ближайший state.time.start к starttime процесса
    Возвращает (session_id, method) или (None, "process").
    """
    # 1. cmdline процесса
    try:
        with open("/proc/self/cmdline", "rb") as f:
            cmdline = f.read().replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()
    except OSError:
        return None, "process"
    if not cmdline:
        return None, "process"

    # 2. starttime (тики с момента загрузки) + btime (epoch s)
    starttime_ticks = None
    try:
        with open("/proc/self/stat") as f:
            stat = f.read()
        # comm в скобках может содержать пробелы — режем по последней ")"
        fields = stat[stat.rfind(")") + 2:].split()
        # после ")" поля идут с 3-го: state(3)=idx0, ..., starttime(22)=idx19
        starttime_ticks = int(fields[19])
    except (OSError, IndexError, ValueError):
        pass

    btime_s = None
    try:
        with open("/proc/stat") as f:
            for line in f:
                if line.startswith("btime "):
                    btime_s = int(line.split()[1])
                    break
    except (OSError, IndexError, ValueError):
        pass

    # 3. Running bash-тулы за последние 60 секунд
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - 60_000
    rows = conn.execute(
        """
        SELECT session_id, id,
               json_extract(data, '$.state.time.start') as tstart,
               json_extract(data, '$.state.input.command') as command
        FROM part
        WHERE json_extract(data, '$.type') = 'tool'
          AND json_extract(data, '$.tool') = 'bash'
          AND json_extract(data, '$.state.status') = 'running'
          AND json_extract(data, '$.state.time.start') > ?
        ORDER BY tstart DESC
        """,
        (cutoff_ms,),
    ).fetchall()
    if not rows:
        return None, "process"

    # 4. Фильтр по подстроке cmdline
    candidates = [r for r in rows if _cmd_matches(cmdline, r["command"])]
    if not candidates:
        return None, "process"

    # 5. Один кандидат — сразу ответ
    if len(candidates) == 1:
        return candidates[0]["session_id"], "process"

    # Несколько кандидатов — ближайший по времени старта
    proc_start_ms = None
    if starttime_ticks is not None and btime_s is not None:
        clk_tck = os.sysconf("SC_CLK_TCK") or 100
        proc_start_ms = (btime_s + starttime_ticks / clk_tck) * 1000

    if proc_start_ms is not None:
        best = min(candidates, key=lambda r: abs((r["tstart"] or 0) - proc_start_ms))
        return best["session_id"], "process"

    # Фолбэк: самый свежий
    return candidates[0]["session_id"], "process"


def _resolve_activity(conn):
    """Реализация A: env OPENCODE_SESSION_ID → последняя активная по time_updated."""
    session_id = os.environ.get("OPENCODE_SESSION_ID")
    if session_id:
        return session_id, "activity (env OPENCODE_SESSION_ID)"

    row = conn.execute(
        "SELECT id FROM session ORDER BY time_updated DESC LIMIT 1"
    ).fetchone()
    if not row:
        return None, "activity"
    return row["id"], "activity"


def cmd_current(args):
    """Текущая сессия процесса и её родительская сессия.

    Методы:
      activity — env OPENCODE_SESSION_ID → последняя активная по time_updated
      process  — сессия процесса через /proc/self/cmdline + part (running bash)
      auto     — сначала process, при неудаче activity (по умолчанию)
    Родительская сессия определяется через колонку parent_id.
    """
    conn = connect()
    try:
        # Выбор метода
        session_id = None
        method = args.method

        if method == "activity":
            session_id, _ = _resolve_activity(conn)
            used_method = "activity"
        else:  # auto или process
            session_id, _ = _resolve_process(conn)
            if session_id:
                used_method = "process"
            else:
                session_id, _ = _resolve_activity(conn)
                used_method = "activity (фолбэк: process не нашёл сессию)"

        if not session_id:
            print("❌ Не удалось определить текущую сессию.", file=sys.stderr)
            sys.exit(1)

        # Данные текущей сессии
        cur = conn.execute(
            "SELECT id, parent_id, title, agent, directory, time_created, time_updated "
            "FROM session WHERE id = ?",
            (session_id,),
        ).fetchone()
        if not cur:
            print(f"❌ Сессия {session_id} не найдена в БД.", file=sys.stderr)
            sys.exit(1)

        parent_id = cur["parent_id"]

        # Данные родительской сессии
        parent = None
        if parent_id:
            parent = conn.execute(
                "SELECT id, title, agent, time_created FROM session WHERE id = ?",
                (parent_id,),
            ).fetchone()

        if args.json:
            print(json.dumps({
                "session_id": cur["id"],
                "parent_id": parent_id,
                "session_title": cur["title"],
                "session_agent": cur["agent"],
                "session_directory": cur["directory"],
                "parent_title": parent["title"] if parent else None,
                "parent_agent": parent["agent"] if parent else None,
                "parent_exists": parent is not None,
                "method": used_method,
            }, ensure_ascii=False, indent=2))
            return

        print(f"Текущая сессия: {cur['id']}")
        print(f"  Метод: {used_method}")
        print(f"  Заголовок: {cur['title'] or '—'}")
        print(f"  Агент: {cur['agent'] or '—'}")
        print(f"  Каталог: {shorten_path(cur['directory'] or '')}")
        print()
        if parent_id:
            print(f"Родительская сессия (parent_id): {parent_id}")
            if parent:
                print(f"  Заголовок: {parent['title'] or '—'}")
                print(f"  Агент: {parent['agent'] or '—'}")
            else:
                print(f"  ⚠️ Родительская сессия не найдена в БД (удалена?)")
        else:
            print(f"Родительская сессия: нет (это корневая сессия, не сабагент)")
    finally:
        conn.close()


def cmd_inspect(args):
    """Детальный просмотр сессии."""
    session_id = args.session_id
    if not session_id:
        print("❌ Укажите ID сессии.", file=sys.stderr)
        sys.exit(1)

    conn = connect()
    try:
        # Основная информация
        row = conn.execute(
            "SELECT * FROM session WHERE id = ?",
            (session_id,),
        ).fetchone()

        if not row:
            print(f"❌ Сессия {session_id} не найдена.")
            return

        # Парсим model JSON
        model_data = {}
        try:
            model_data = json.loads(row["model"]) if row["model"] else {}
        except (json.JSONDecodeError, TypeError):
            pass

        if args.json:
            output = {
                "id": row["id"],
                "title": row["title"],
                "slug": row["slug"],
                "directory": row["directory"],
                "agent": row["agent"],
                "version": row["version"],
                "time_created": row["time_created"],
                "time_created_fmt": fmt_time_full(row["time_created"]),
                "project_id": row["project_id"],
                "model": model_data,
                "tokens_input": row["tokens_input"],
                "tokens_output": row["tokens_output"],
                "tokens_reasoning": row["tokens_reasoning"],
                "tokens_cache_read": row["tokens_cache_read"],
                "tokens_cache_write": row["tokens_cache_write"],
                "cost": row["cost"],
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return

        # Вывод метаданных
        print(f"{'='*70}")
        print(f"  📄 Сессия: {row['id']}")
        print(f"{'='*70}")
        print(f"  Название:  {row['title'] or '—'}")
        print(f"  Агент:     {row['agent'] or '—'}")
        print(f"  Проект:    {shorten_path(row['directory'] or '—')}")
        print(f"  Создана:   {fmt_time_full(row['time_created'])}")
        print(f"  Slug:      {row['slug'] or '—'}")
        print(f"  Version:   {row['version'] or '—'}")
        
        # Модель
        model_id = model_data.get("id") or model_data.get("modelID", "")
        provider = model_data.get("providerID", "")
        if model_id:
            print(f"  Модель:    {provider}/{model_id}" if provider else f"  Модель:    {model_id}")

        # Токены и стоимость
        ti = row["tokens_input"] or 0
        to = row["tokens_output"] or 0
        tr = row["tokens_reasoning"] or 0
        tcr = row["tokens_cache_read"] or 0
        tcw = row["tokens_cache_write"] or 0
        cost = row["cost"] or 0

        print(f"  Токены:")
        print(f"    Input:    {format_tokens(ti)}")
        print(f"    Output:   {format_tokens(to)}")
        print(f"    Reasoning: {format_tokens(tr)}")
        print(f"    Cache R:  {format_tokens(tcr)}")
        print(f"    Cache W:  {format_tokens(tcw)}")
        print(f"    Всего:    {format_tokens(ti + to + tr)}")
        print(f"  Стоимость: {format_cost(cost)}")

        # Сообщения
        print()
        print(f"  {'─'*60}")
        
        msg_limit = args.messages if args.messages else 5
        
        # Пробуем message таблицу
        try:
            messages = conn.execute(
                """SELECT id, time_created, data 
                   FROM message 
                   WHERE session_id = ? 
                   ORDER BY time_created ASC""",
                (session_id,),
            ).fetchall()
        except sqlite3.OperationalError:
            messages = []

        if not messages:
            try:
                messages = conn.execute(
                    """SELECT id, time_created, data, type 
                       FROM session_message 
                       WHERE session_id = ? 
                       ORDER BY seq ASC""",
                    (session_id,),
                ).fetchall()
            except sqlite3.OperationalError:
                messages = []

        total_msgs = len(messages)
        if total_msgs > 0:
            print(f"  Сообщения ({total_msgs} всего, показано {min(msg_limit, total_msgs)}):")
            print()
            
            # Показываем только последние msg_limit
            show_messages = messages[-msg_limit:] if msg_limit < total_msgs else messages
            
            for m in show_messages:
                role = ""
                data = m["data"]
                if data:
                    try:
                        data_obj = json.loads(data) if isinstance(data, str) else data
                        role = data_obj.get("role", "?")
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                time_str = fmt_time_full(m["time_created"]) if m["time_created"] else "—"
                prefix = "  👤" if role == "user" else "  🤖"
                print(f"  {prefix} [{time_str}]")
                
                # Краткое содержимое
                content_preview = ""
                if data:
                    data_str = str(data)
                    # Парсим для красивого отображения
                    try:
                        data_obj = json.loads(data_str) if isinstance(data_str, str) else {}
                        if isinstance(data_obj, dict):
                            content_preview = data_obj.get("text") or data_obj.get("content") or ""
                            if not content_preview:
                                # Может быть в parts
                                parts = data_obj.get("parts", [])
                                if parts:
                                    first_part = parts[0] if isinstance(parts, list) else parts
                                    if isinstance(first_part, dict):
                                        content_preview = first_part.get("text", "")
                    except (json.JSONDecodeError, TypeError):
                        content_preview = data_str[:200] if len(str(data_str)) > 200 else str(data_str)
                
                if content_preview:
                    print(f"     {truncate(content_preview, 120)}")
                print()
        else:
            print("  Нет сообщений.")

        # Todos
        if args.todos:
            try:
                todos = conn.execute(
                    "SELECT content, status, priority FROM todo WHERE session_id = ? ORDER BY time_created",
                    (session_id,),
                ).fetchall()
                if todos:
                    print()
                    print(f"  Todos ({len(todos)}):")
                    for t in todos:
                        status_icon = "✅" if t["status"] == "done" else "🔄" if t["status"] == "in_progress" else "⏳"
                        print(f"    {status_icon} [{t['status']}] {t['content']} ({t['priority'] or '—'})")
            except sqlite3.OperationalError:
                pass

        print(f"{'='*70}")

    finally:
        conn.close()


def cmd_stats(args):
    """Статистика по сессиям."""
    conn = connect()
    try:
        # Фильтр по дням
        date_filter = ""
        params = []
        if args.days:
            cutoff = (datetime.now(timezone.utc).timestamp() - args.days * 86400) * 1000
            date_filter = "WHERE s.time_created >= ?"
            params.append(int(cutoff))

        # Общая статистика
        total_sessions = conn.execute(
            f"SELECT COUNT(*) as cnt FROM session s {date_filter}", params
        ).fetchone()["cnt"]

        total_tokens = conn.execute(
            f"""SELECT COALESCE(SUM(s.tokens_input), 0) as ti, 
                       COALESCE(SUM(s.tokens_output), 0) as to_
                FROM session s {date_filter}""", params
        ).fetchone()
        total_cost = conn.execute(
            f"SELECT COALESCE(SUM(s.cost), 0) as cost FROM session s {date_filter}", params
        ).fetchone()["cost"]

        # По проектам
        by_project = []
        if args.by_project:
            rows = conn.execute(
                f"""SELECT s.directory, COUNT(*) as cnt,
                           COALESCE(SUM(s.tokens_input), 0) as ti,
                           COALESCE(SUM(s.tokens_output), 0) as to_,
                           COALESCE(SUM(s.cost), 0) as cost
                    FROM session s {date_filter}
                    GROUP BY s.directory
                    ORDER BY cnt DESC
                    LIMIT 20""", params
            ).fetchall()
            by_project = rows

        # По агентам
        by_agent = []
        if args.by_agent:
            rows = conn.execute(
                f"""SELECT COALESCE(s.agent, '—') as agent, COUNT(*) as cnt,
                           COALESCE(SUM(s.tokens_input), 0) as ti,
                           COALESCE(SUM(s.tokens_output), 0) as to_,
                           COALESCE(SUM(s.cost), 0) as cost
                    FROM session s {date_filter}
                    GROUP BY s.agent
                    ORDER BY cnt DESC""", params
            ).fetchall()
            by_agent = rows

        # По моделям
        by_model = []
        if args.by_model:
            rows = conn.execute(
                f"""SELECT s.model, COUNT(*) as cnt
                    FROM session s {date_filter}
                    GROUP BY s.model
                    ORDER BY cnt DESC
                    LIMIT 20""", params
            ).fetchall()
            by_model = rows

        # Вывод
        print(f"{'='*60}")
        print("  📊 Статистика сессий")
        print(f"{'='*60}")

        period = f" за последние {args.days} дн." if args.days else " (всё время)"
        print(f"\n  📈 Общая{period}")
        print(f"     Сессий:   {total_sessions}")
        print(f"     Токены:   {format_tokens(total_tokens['ti'] + total_tokens['to_'])} "
              f"(in: {format_tokens(total_tokens['ti'])}, "
              f"out: {format_tokens(total_tokens['to_'])})")
        print(f"     Стоимость: ${total_cost:.4f}")

        if by_project:
            print(f"\n  📁 По проектам:")
            for r in by_project:
                proj = shorten_path(r["directory"] or "—")
                print(f"     {proj:<40} {r['cnt']} сес, "
                      f"{format_tokens(r['ti'] + r['to_'])} ток, "
                      f"${r['cost']:.4f}")

        if by_agent:
            print(f"\n  🤖 По агентам:")
            for r in by_agent:
                print(f"     {r['agent']:<20} {r['cnt']} сес, "
                      f"{format_tokens(r['ti'] + r['to_'])} ток, "
                      f"${r['cost']:.4f}")

        if by_model:
            print(f"\n  🧠 По моделям:")
            for r in by_model:
                model_str = r["model"] or "—"
                model_short = truncate(model_str, 40)
                print(f"     {model_short:<42} {r['cnt']} сес")

        print(f"{'='*60}")

    except sqlite3.Error as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
    finally:
        conn.close()


def cmd_db(args):
    """Информация о БД."""
    path = get_db_path()
    
    size = os.path.getsize(path) if os.path.exists(path) else 0
    
    print(f"  📁 База данных OpenCode")
    print(f"{'='*50}")
    print(f"  Путь:    {path}")
    print(f"  Размер:  {size / 1024 / 1024:.1f} MB")
    
    if args.tables or args.all:
        conn = connect()
        try:
            tables = conn.execute(
                "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
            ).fetchall()
            print(f"\n  Таблицы ({len(tables)}):")
            for t in tables:
                print(f"    📊 {t['name']:<30} ({t['type']})")
        finally:
            conn.close()

    if args.size:
        print(f"  Размер:  {size / 1024 / 1024:.1f} MB")


def cmd_ocdb(args):
    """Передача аргументов в ocdb."""
    if not os.path.exists(OCDB_PATH):
        print(f"❌ ocdb не найден по пути: {OCDB_PATH}", file=sys.stderr)
        print("   Установите ocdb или используйте прямые команды ses.")
        sys.exit(1)

    cmd = [OCDB_PATH] + args.args
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        print(f"❌ ocdb не найден.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass


def cmd_ocdb_check(args):
    """Проверка ocdb."""
    if os.path.exists(OCDB_PATH):
        print(f"✅ ocdb установлен: {OCDB_PATH}")
        try:
            result = subprocess.run([OCDB_PATH, "--version"], capture_output=True, text=True)
            print(f"   Версия: {result.stdout.strip() or result.stderr.strip() or '—'}")
        except FileNotFoundError:
            print("   Версия: не определена")
    else:
        print(f"❌ ocdb не найден по пути: {OCDB_PATH}")
        print()
        print("  Для установки ocdb:")
        print("    pip install ocdb  (если опубликован в PyPI)")
        print("    или установите вручную из исходников")
        print()
        print("  ocdb предоставляет GraphQL доступ к БД OpenCode.")


def cmd_help(args):
    """Справка."""
    print(textwrap.dedent("""\
    ses — Session Search для OpenCode
    ====================================
    
    ИСПОЛЬЗОВАНИЕ:
      ses list [--limit N] [--all] [--today] [--table] [--json] [--project]
      ses search <query> [--limit N] [--table] [--json] [--project] [--days N]
      ses fts <query> [--limit N] [--json] [--project] [--days N]
      ses inspect <id> [--messages N] [--todos] [--json]
      ses stats [--days N] [--by-project] [--by-agent] [--by-model]
      ses db [--tables] [--size]
      ses filter [--title-substring X] [--search X] [--agent X] [--model X] [--limit N]
      ses ocdb <args>
      ses ocdb-check
      ses help
    
    КОМАНДЫ:
      list      Список сессий
      search    Поиск по заголовкам и содержимому (LIKE + FTS5 fallback)
      fts       Полнотекстовый поиск FTS5 (слова, фразы, AND/OR/NOT, NEAR)
      inspect   Детальный просмотр сессии
      stats     Статистика по сессиям
      db        Информация о базе данных
      filter    Фильтр сессий через GraphQL (ocdb)
      ocdb      Вызов ocdb с аргументами
      ocdb-check Проверка наличия ocdb
      help      Эта справка
    
    ПРИМЕРЫ:
      ses list
      ses list --today --table
      ses search "docker compose"
      ses fts "auth AND jwt"
      ses fts '"rate limiting"'
      ses inspect ses_abc123 --messages 10
      ses stats --by-agent --days 7
      ses db --tables
    
    FTS5 СИНТАКСИС:
      "точная фраза"    — точное совпадение фразы
      auth AND jwt      — оба слова
      auth OR jwt       — любое из слов
      auth NOT oauth    — исключить слово
      auth NEAR/5 jwt   — в пределах 5 слов
      auth*             — префикс
    
    ПУТЬ К БД:
      По умолчанию: ~/.local/share/opencode/opencode.db
      Переменная: OPENCODE_DB
    """))


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="ses — Session Search для OpenCode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Примеры:
              ses list
              ses search auth
              ses fts "docker compose"
              ses inspect ses_abc123
              ses current
        """),
    )
    parser.add_argument("--db", help="Путь к БД OpenCode (по умолчанию автоопределение)")

    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # list
    p_list = subparsers.add_parser("list", help="Список сессий")
    p_list.add_argument("--limit", type=int, default=20, help="Максимум сессий (default: 20)")
    p_list.add_argument("--all", action="store_true", help="Все сессии")
    p_list.add_argument("--today", action="store_true", help="Только за сегодня")
    p_list.add_argument("--days", type=int, help="За последние N дней")
    p_list.add_argument("--table", action="store_true", help="Табличный вывод")
    p_list.add_argument("--json", action="store_true", help="JSON вывод")
    p_list.add_argument("--project", action="store_true", help="Только текущий проект")

    # search
    p_search = subparsers.add_parser("search", help="Поиск по содержимому сессий")
    p_search.add_argument("query", nargs="+", help="Поисковый запрос")
    p_search.add_argument("--limit", type=int, default=20, help="Максимум результатов")
    p_search.add_argument("--table", action="store_true", help="Табличный вывод")
    p_search.add_argument("--json", action="store_true", help="JSON вывод")
    p_search.add_argument("--project", action="store_true", help="Только текущий проект")
    p_search.add_argument("--days", type=int, help="За последние N дней")
    p_search.add_argument("--session-id", help="Искать только в сессии с этим ID")

    # fts
    p_fts = subparsers.add_parser("fts", help="Полнотекстовый поиск FTS5")
    p_fts.add_argument("query", nargs="+", help="FTS5 поисковый запрос")
    p_fts.add_argument("--limit", type=int, default=20, help="Максимум результатов")
    p_fts.add_argument("--json", action="store_true", help="JSON вывод")
    p_fts.add_argument("--project", action="store_true", help="Только текущий проект")
    p_fts.add_argument("--days", type=int, help="За последние N дней")
    p_fts.add_argument("--session-id", help="Искать только в сессии с этим ID")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Детали сессии")
    p_inspect.add_argument("session_id", help="ID сессии")
    p_inspect.add_argument("--messages", type=int, default=5, help="Сколько сообщений показать")
    p_inspect.add_argument("--todos", action="store_true", help="Показать todos")
    p_inspect.add_argument("--json", action="store_true", help="JSON вывод")

    # stats
    p_stats = subparsers.add_parser("stats", help="Статистика")
    p_stats.add_argument("--days", type=int, help="За последние N дней")
    p_stats.add_argument("--by-project", action="store_true", help="По проектам")
    p_stats.add_argument("--by-agent", action="store_true", help="По агентам")
    p_stats.add_argument("--by-model", action="store_true", help="По моделям")

    # current
    p_current = subparsers.add_parser(
        "current", help="Текущая сессия (последняя активная) и её родительская сессия"
    )
    p_current.add_argument(
        "--method", "-m",
        choices=["auto", "activity", "process"],
        default="auto",
        help="Метод определения сессии: process (по процессу), activity (по активности), auto (process → activity) (default: auto)",
    )
    p_current.add_argument("--json", action="store_true", help="JSON вывод")

    # db
    p_db = subparsers.add_parser("db", help="Информация о БД")
    p_db.add_argument("--tables", action="store_true", help="Список таблиц")
    p_db.add_argument("--size", action="store_true", help="Только размер")
    p_db.add_argument("--all", action="store_true", help="Вся информация")

    # filter
    p_filter = subparsers.add_parser("filter", help="Фильтр сессий через GraphQL (ocdb)")
    p_filter.add_argument("--title-substring", "-t", help="Подстрока в заголовке сессии")
    p_filter.add_argument("--search", "-s", help="Полнотекстовый поиск (заголовок + сообщения)")
    p_filter.add_argument("--agent", "-a", help="Фильтр по агенту")
    p_filter.add_argument("--model", "-m", help="Подстрока в имени модели")
    p_filter.add_argument("--session-id", "-i", help="Подстрока в ID сессии")
    p_filter.add_argument("--limit", "-l", type=int, default=20, help="Максимум сессий (default: 20)")
    p_filter.add_argument("--min-msgs", type=int, help="Мин. кол-во сообщений")
    p_filter.add_argument("--min-input", type=int, help="Мин. входных токенов")
    p_filter.add_argument("--min-output", type=int, help="Мин. выходных токенов")
    p_filter.add_argument("--date-from", help="Сессии от даты (YYYY-MM-DD)")
    p_filter.add_argument("--date-to", help="Сессии до даты (YYYY-MM-DD)")
    p_filter.add_argument("--order-by", help="Поле сортировки (time_created, title, tokens_input...)")
    p_filter.add_argument("--order-dir", help="Направление (asc/desc)")
    p_filter.add_argument("--json", action="store_true", help="JSON вывод")

    # ocdb
    p_ocdb = subparsers.add_parser("ocdb", help="Вызов ocdb")
    p_ocdb.add_argument("args", nargs=argparse.REMAINDER, help="Аргументы для ocdb")

    # ocdb-check
    subparsers.add_parser("ocdb-check", help="Проверка ocdb")

    # help
    subparsers.add_parser("help", help="Справка")

    args = parser.parse_args()

    # Глобальный --db
    if args.db:
        global DB_PATH
        DB_PATH = args.db

    # Диспетчеризация
    if args.command == "list":
        cmd_list(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "fts":
        cmd_fts(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "current":
        cmd_current(args)
    elif args.command == "db":
        cmd_db(args)
    elif args.command == "filter":
        cmd_filter(args)
    elif args.command == "ocdb":
        cmd_ocdb(args)
    elif args.command == "ocdb-check":
        cmd_ocdb_check(args)
    elif args.command == "help" or args.command is None:
        cmd_help(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
