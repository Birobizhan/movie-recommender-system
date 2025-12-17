# Текстовые константы для форматирования
REPORT_HEADER = "📊 ПОЛНЫЙ ОТЧЕТ О СИСТЕМЕ MovieHub"
REPORT_DIVIDER = "─" * 40

STATUS_SECTION = "🔧 СТАТУС СЕРВИСОВ"
DB_SECTION = "💾 БАЗА ДАННЫХ"
ERRORS_SECTION = "⚠️ КРИТИЧЕСКИЕ ОШИБКИ"
MOVIES_SECTION = "🎬 ТОП ФИЛЬМОВ (24ч)"
REVIEWS_SECTION = "⭐ НОВЫЕ ОТЗЫВЫ"
SEARCH_SECTION = "🔍 ПОИСКОВАЯ АКТИВНОСТЬ"
USERS_SECTION = "👥 ПОЛЬЗОВАТЕЛИ"
PAGES_SECTION = "📄 ПОПУЛЯРНЫЕ СТРАНИЦЫ"

STATUS_OK = "✅"
STATUS_ERROR = "❌"
STATUS_WARNING = "⚠️"


def parse_status(data):
    back_status = data['services']['backend_api']['status']
    back_message = data['services']['backend_api']['message']
    db_status = data['services']['database']['status']
    db_message = data['services']['database']['message']
    front_status = data['services']['frontend_ui']['status']
    front_message = data['services']['frontend_ui']['message']
    if back_status == 'ok' and db_status == 'ok' and front_status == 'ok':
        answer = (f'Все 3 сервиса работают без проблем:\n'
                  f'{back_message}\n'
                  f'{db_message}\n'
                  f'{front_message}')
    else:
        answer = (f'Есть проблемы с сервисами, сейчас они работают так:\n'
                  f'{back_message}\n'
                  f'{db_message}\n'
                  f'{front_message}')
    return answer


def parse_db(data):
    answer = (f'Состояние базы данных:\n'
              f'Работает исправно\n'
              f'Характеристики БД: Количество фильмов: {data["movies_count"]}\n'
              f'Количество пользователей: {data["users_count"]}\n'
              f'Количество отзывов и оценок: {data["reviews_count"]}\n'
              f'Количество списков: {data["lists_count"]}\n'
              f'Количество списков, созданных пользователями: {data["users_created_list"]}')
    return answer


def parse_full_report(data: dict) -> str:
    """
    Форматирует полный отчёт в красивый текст для Telegram.
    """
    lines = []
    
    # Заголовок
    lines.append(f"<b>{REPORT_HEADER}</b>")
    lines.append(REPORT_DIVIDER)
    lines.append("")
    
    # 1. СТАТУС СЕРВИСОВ
    lines.append(f"<b>{STATUS_SECTION}</b>")
    status = data.get("status", {}).get("services", {})
    
    backend = status.get("backend_api", {})
    backend_icon = STATUS_OK if backend.get("status") == "ok" else STATUS_ERROR
    lines.append(f"{backend_icon} <b>Backend API:</b> {backend.get('message', 'N/A')}")
    
    database = status.get("database", {})
    db_icon = STATUS_OK if database.get("status") == "ok" else STATUS_ERROR
    lines.append(f"{db_icon} <b>База данных:</b> {database.get('message', 'N/A')}")
    
    frontend = status.get("frontend_ui", {})
    frontend_icon = STATUS_OK if frontend.get("status") == "ok" else STATUS_ERROR
    lines.append(f"{frontend_icon} <b>Frontend UI:</b> {frontend.get('message', 'N/A')}")
    lines.append("")
    
    # 2. БАЗА ДАННЫХ
    lines.append(f"<b>{DB_SECTION}</b>")
    db_check = data.get("db_check", {})
    lines.append(f"📚 Фильмов: <b>{db_check.get('movies_count', 0):,}</b>")
    lines.append(f"👤 Пользователей: <b>{db_check.get('users_count', 0):,}</b>")
    lines.append(f"⭐ Отзывов: <b>{db_check.get('reviews_count', 0):,}</b>")
    lines.append(f"📋 Списков: <b>{db_check.get('lists_count', 0):,}</b>")
    lines.append(f"📝 Списков от пользователей: <b>{db_check.get('users_created_list', 0):,}</b>")
    lines.append("")
    
    # 3. КРИТИЧЕСКИЕ ОШИБКИ
    lines.append(f"<b>{ERRORS_SECTION}</b>")
    errors = data.get("logs_errors", {}).get("items", [])
    if errors:
        for i, error in enumerate(errors[:5], 1):
            error_time = error.get("created_at", "N/A")[:16] if error.get("created_at") else "N/A"
            error_msg = error.get("message", "N/A")[:100]
            lines.append(f"{i}. [{error_time}] {error_msg}")
    else:
        lines.append("✅ Критических ошибок не обнаружено")
    lines.append("")
    
    # 4. ТОП ФИЛЬМОВ
    lines.append(f"<b>{MOVIES_SECTION}</b>")
    top_movies = data.get("top_movies_24h", {}).get("items", [])
    if top_movies:
        for i, movie in enumerate(top_movies[:10], 1):
            title = movie.get("title", "N/A")[:40]
            views = movie.get("views", 0)
            lines.append(f"{i}. <b>{title}</b> — {views} просмотров")
    else:
        lines.append("📊 Данных о просмотрах пока нет")
    lines.append("")
    
    # 5. НОВЫЕ ОТЗЫВЫ
    lines.append(f"<b>{REVIEWS_SECTION}</b>")
    new_reviews = data.get("new_reviews", {}).get("today_reviews", 0)
    lines.append(f"Сегодня добавлено: <b>{new_reviews}</b> отзывов")
    lines.append("")
    
    # 6. ПОИСКОВАЯ АКТИВНОСТЬ
    lines.append(f"<b>{SEARCH_SECTION}</b>")
    
    # Топ поисковых запросов
    top_search = data.get("top_search", {}).get("items", [])
    if top_search:
        lines.append("🔝 <b>Популярные запросы:</b>")
        for i, item in enumerate(top_search[:5], 1):
            query = item.get("query", "N/A")[:30]
            count = item.get("count", 0)
            lines.append(f"  {i}. \"{query}\" — {count} раз")
    
    # Пустые поиски
    search_none = data.get("search_stats_none", {}).get("items", [])
    if search_none:
        lines.append("")
        lines.append("❌ <b>Запросы без результатов:</b>")
        for i, item in enumerate(search_none[:5], 1):
            query = item.get("query", "N/A")[:30]
            count = item.get("count", 0)
            lines.append(f"  {i}. \"{query}\" — {count} раз")
    lines.append("")
    
    # 7. ПОЛЬЗОВАТЕЛИ
    lines.append(f"<b>{USERS_SECTION}</b>")
    new_users = data.get("new_users", {})
    lines.append(f"📅 Сегодня: <b>{new_users.get('today', 0)}</b> новых")
    lines.append(f"📆 За неделю: <b>{new_users.get('last_7_days', 0)}</b> новых")
    
    active_users = data.get("active_users", {}).get("active_users_last_7_days", 0)
    lines.append(f"🔥 Активных (7 дней): <b>{active_users}</b>")
    lines.append("")
    
    # 8. ПОПУЛЯРНЫЕ СТРАНИЦЫ
    lines.append(f"<b>{PAGES_SECTION}</b>")
    top_pages = data.get("top_pages", {}).get("items", [])
    if top_pages:
        for i, page in enumerate(top_pages[:10], 1):
            path = page.get("path", "N/A")[:35]
            count = page.get("count", 0)
            lines.append(f"{i}. {path} — {count} посещений")
    else:
        lines.append("📊 Данных о посещениях пока нет")
    
    lines.append("")
    lines.append(REPORT_DIVIDER)
    lines.append("📅 Отчёт сформирован автоматически")
    
    return "\n".join(lines)