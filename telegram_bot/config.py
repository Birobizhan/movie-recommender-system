from dataclasses import dataclass
from environs import Env


env = Env()
env.read_env()


@dataclass
class BotSettings:
    token: str
    admin_usernames: list[str]
    api_base_url: str


def get_settings() -> BotSettings:
    token = env.str("TELEGRAM_BOT_TOKEN")
    admins_raw = env.str("TELEGRAM_ADMIN_USERNAMES", "")
    admin_usernames = [u.strip().lstrip("@") for u in admins_raw.split(",") if u.strip()]
    api_base_url = env.str("ADMIN_API_BASE_URL", "http://localhost:8000/api")
    return BotSettings(token=token, admin_usernames=admin_usernames, api_base_url=api_base_url)





