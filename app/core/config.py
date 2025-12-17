from environs import Env


env = Env()
env.read_env()

# Database
DATABASE_URL: str = env.str("DATABASE_URL")

# Security
SECRET_KEY: str = env.str("SECRET_KEY")
ALGORITHM: str = env.str("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

# Optional refresh token lifetime (days)
REFRESH_TOKEN_EXPIRE_DAYS: int = env.int("REFRESH_TOKEN_EXPIRE_DAYS", 30)

# OAuth
YANDEX_CLIENT_ID: str = env.str("YANDEX_CLIENT_ID", "")
YANDEX_CLIENT_SECRET: str = env.str("YANDEX_CLIENT_SECRET", "")
YANDEX_REDIRECT_URI: str = env.str("YANDEX_REDIRECT_URI", "http://localhost:8000/api/auth/yandex/callback")
FRONTEND_URL: str = env.str("FRONTEND_URL", "http://localhost:5173")
