import asyncio
from typing import Any, Dict

import aiohttp
from aiohttp import ClientResponseError, ClientError
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BotCommand

from .config import get_settings


settings = get_settings()
bot = Bot(token=settings.token)
dp = Dispatcher()

ADMIN_COMMANDS = [
    BotCommand(command="start", description="Показать список команд"),
    BotCommand(command="commands", description="Показать список команд"),
    BotCommand(command="status", description="Проверить статус API"),
    BotCommand(command="db_check", description="Проверить статус подключения к БД"),
    BotCommand(command="logs_errors", description="Последние ошибки в логах"),
    BotCommand(command="top_movies", description="Топ-10 просматриваемых фильмов"),
    BotCommand(command="new_reviews", description="Количество новых отзывов"),
    BotCommand(command="search_stats_none", description="Топ 'пустых' поисков"),
    BotCommand(command="top_search", description="Топ поисковых запросов"),
    BotCommand(command="top_pages", description="Топ-10 посещаемых страниц"),
    BotCommand(command="new_users", description="Статистика по новым пользователям"),
    BotCommand(command="active_users", description="Количество активных пользователей"),
    BotCommand(command="user_stats", description="Статистика по пользователю (ID)"),
    BotCommand(command="full_report", description="Полный отчет о системе"),
    BotCommand(command="ai_report", description="Аналитический отчет от LLM"),
]
def _is_admin(message: Message) -> bool:
    username = (message.from_user.username or "").lstrip("@")
    return username in settings.admin_usernames


async def _api_get(path: str, params: Dict[str, Any] | None = None) -> Any:
    url = settings.api_base_url.rstrip("/") + "/" + path.lstrip("/")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, timeout=10) as resp:
                resp.raise_for_status()
                return await resp.json()
        except ClientResponseError as e:
            return {"error": f"HTTP {e.status}: {e.message}", "status": e.status}
        except ClientError as e:
            # Ошибки соединения: backend не доступен / отказал в соединении
            return {"error": f"Ошибка соединения с API: {e}", "status": None}
        except Exception as e:
            return {"error": f"Неизвестная ошибка запроса к API: {e}", "status": None}


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if not _is_admin(message):
        await message.answer("Доступ запрещён. Вы не являетесь администратором.")
        return
    await message.answer(
        "Админ-бот MovieHub.\n"
        "Доступные команды:\n"
        "/status, /db_check, /logs_errors, /top_movies, /new_reviews,\n"
        "/search_stats_none, /top_search, /top_pages, /new_users,\n"
        "/active_users, /user_stats, /full_report, /ai_report"
    )


@dp.message(Command("commands"))
async def cmd_commands(message: Message):
    if not _is_admin(message):
        await message.answer("Доступ запрещён. Вы не являетесь администратором.")
        return
    await message.answer(
        "Админ-бот MovieHub.\n"
        "Доступные команды:\n"
        "/status, /db_check, /logs_errors, /top_movies, /new_reviews,\n"
        "/search_stats_none, /top_search, /top_pages, /new_users,\n"
        "/active_users, /user_stats, /full_report, /ai_report"
    )


@dp.message(Command("status"))
async def cmd_status(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/status")
    if "error" in data:
        await message.answer(f"Ошибка запроса к API: {data['error']}")
    else:

        await message.answer(f"Status: {data}")


@dp.message(Command("db_check"))
async def cmd_db_check(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/db_check")
    await message.answer(f"DB: {data}")


@dp.message(Command("logs_errors"))
async def cmd_logs_errors(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/logs_errors", params={"limit": 10})
    if "error" in data:
        await message.answer(f"Ошибка запроса к API: {data['error']}")
        return
    lines = []
    for item in data.get("items", []):
        lines.append(
            f"[{item['created_at']}] {item['level']}: {item['message']}")
    text = "\n".join(lines) or "Нет ошибок."
    await message.answer(text)


@dp.message(Command("top_movies"))
async def cmd_top_movies(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    period = "24h"
    if "7" in (message.text or ""):
        period = "7d"
    data = await _api_get("admin/top_movies", params={"period": period})
    if "error" in data:
        await message.answer(f"Ошибка запроса к API: {data['error']}")
        return
    lines = [f"Топ фильмов за {period}:"]
    for item in data.get("items", []):
        lines.append(f"{item['title']} — {item['views']} просмотров")
    if len(lines) == 1:
        lines.append("Пока нет данных о просмотрах фильмов.")
    await message.answer("\n".join(lines))


@dp.message(Command("new_reviews"))
async def cmd_new_reviews(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/new_reviews")
    await message.answer(f"Новых отзывов сегодня: {data.get('today_reviews', 0)}")


@dp.message(Command("search_stats_none"))
async def cmd_search_stats_none(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/search_stats_none")
    lines = ["Топ 'пустых' поисков:"]
    for item in data.get("items", []):
        lines.append(f"\"{item['query']}\" — {item['count']} запросов")
    await message.answer("\n".join(lines))


@dp.message(Command("top_search"))
async def cmd_top_search(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/top_search")
    lines = ["Топ поисковых запросов:"]
    for item in data.get("items", []):
        lines.append(f"\"{item['query']}\" — {item['count']} запросов")
    await message.answer("\n".join(lines))


@dp.message(Command("top_pages"))
async def cmd_top_pages(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/top_pages")
    lines = ["Топ страниц:"]
    for item in data.get("items", []):
        lines.append(f"{item['path']} — {item['count']} посещений")
    await message.answer("\n".join(lines))


@dp.message(Command("new_users"))
async def cmd_new_users(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/new_users")
    await message.answer(
        f"Новых пользователей сегодня: {data.get('today', 0)}\n"
        f"За последние 7 дней: {data.get('last_7_days', 0)}"
    )


@dp.message(Command("active_users"))
async def cmd_active_users(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/active_users")
    await message.answer(
        f"Активных пользователей за последние 7 дней: {data.get('active_users_last_7_days', 0)}"
    )


@dp.message(Command("user_stats"))
async def cmd_user_stats(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Использование: /user_stats <user_id>")
        return
    user_id = int(parts[1])
    data = await _api_get(f"admin/user_stats/{user_id}")
    if "error" in data:
        await message.answer(f"Ошибка запроса к API: {data['error']}")
        return
    await message.answer(
        f"Пользователь {data['username']} (id={data['id']})\n"
        f"Создан: {data['created_at']}\n"
        f"Отзывы: {data['reviews_count']}\n"
        f"Списки: {data['lists_count']}"
    )


@dp.message(Command("full_report"))
async def cmd_full_report(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/full_report")
    await message.answer(f"Полный отчёт:\n{data}")


@dp.message(Command("ai_report"))
async def cmd_ai_report(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав.")
        return
    data = await _api_get("admin/ai_report")
    analysis = data.get("analysis") or "LLM-аналитика недоступна."
    await message.answer(analysis)


async def main() -> None:
    await bot.set_my_commands(ADMIN_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
