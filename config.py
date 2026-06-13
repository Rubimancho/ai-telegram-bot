import os

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")

# ID канала для публикации
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Интервал проверки новостей (в секундах)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # 1 минута

# Максимальное количество новостей за один цикл
MAX_NEWS_PER_CYCLE = int(os.getenv("MAX_NEWS_PER_CYCLE", "5"))

# Задержка между публикациями (в секундах)
PUBLISH_DELAY = int(os.getenv("PUBLISH_DELAY", "5"))

# Минимальная длина текста новости
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "50"))

# Режим отладки
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
