#!/usr/bin/env python3
"""
🤖 Auto-Telegram AI Bot
Автономный бот для Telegram-канала о ИИ и технологиях.
Генерирует статьи через Groq API и картинки через Pollinations.ai
Публикует автоматически по расписанию.

Автор: AI Assistant
Дата: 2026-06-07
"""

import os
import json
import random
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ (заполни свои данные!)
# ═══════════════════════════════════════════════════════════════

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН_БОТА")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "ВСТАВЬ_СЮДА_ID_КАНАЛА")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "ВСТАВЬ_СЮДА_GROQ_API_KEY")

# Расписание публикаций (в часах, UTC)
# По умолчанию: 08:00, 12:00, 16:00, 20:00 (МСК = UTC+3)
PUBLISH_SCHEDULE = [5, 9, 13, 17]  # UTC время

# ═══════════════════════════════════════════════════════════════
# БАЗА ТЕМ ДЛЯ СТАТЕЙ (постоянно пополняется)
# ═══════════════════════════════════════════════════════════════

ARTICLE_TOPICS = [
    # Общий ИИ
    "Новейшие достижения в области генеративного ИИ",
    "Как нейросети меняют медицину: диагностика и лечение",
    "ИИ в образовании: персонализированное обучение",
    "Этика искусственного интеллекта: вызовы и решения",
    "Будущее работы: как ИИ изменит рынок труда",
    "Нейросети и творчество: искусство, музыка, литература",
    "ИИ в бизнесе: автоматизация и аналитика",
    "Квантовые вычисления и ИИ: новый виток развития",
    "Распознавание речи: прорывы и технологии",
    "Компьютерное зрение: от распознавания лиц до автопилотов",

    # Модели и технологии
    "Сравнение языковых моделей: GPT, Claude, Gemini, Llama",
    "Мультимодальные ИИ: текст, изображения, видео в одной модели",
    "Малые языковые модели: эффективность на мобильных устройствах",
    "Агентный ИИ: автономные системы принятия решений",
    "RAG-системы: как ИИ работает с внешними данными",
    "Fine-tuning vs Prompt Engineering: что выбрать",
    "Инфраструктура ИИ: GPU, TPU, LPU — сравнение",
    "Оптимизация нейросетей: квантизация и дистилляция",

    # Практическое применение
    "Топ-10 бесплатных инструментов ИИ для продуктивности",
    "Как создать собственного ИИ-ассистента без программирования",
    "ИИ в маркетинге: персонализация и таргетинг",
    "Чат-боты нового поколения: от простых ответов до агентов",
    "ИИ для программистов: автодополнение, ревью кода, генерация",
    "Генерация видео с помощью ИИ: Sora, Runway и аналоги",
    "ИИ в научных исследованиях: ускорение открытий",
    "Персональные ИИ-ассистенты: будущее или реальность",

    # Новости и тренды
    "ИИ-регулирование в 2026 году: законы и нормы",
    "Инвестиции в ИИ: куда вкладывают миллиарды",
    "Open Source ИИ: почему открытые модели важны",
    "ИИ и кибербезопасность: защита и угрозы",
    "Зелёный ИИ: экологичность вычислений",
    "Нейроинтерфейсы: мозг-компьютер связь",
    "ИИ в космосе: исследование Вселенной",
    "Эмоциональный ИИ: распознавание и генерация эмоций",

    # Глубокие технологии
    "Трансформеры: как работают современные языковые модели",
    "Диффузионные модели: генерация изображений из шума",
    "Графовые нейросети: анализ связей и структур",
    "Обучение с подкреплением: от игр до робототехники",
    "Федеративное обучение: приватность и коллаборация",
    "Нейросети на краю: Edge AI и IoT",
    "ИИ и блокчейн: синергия технологий",
    "Генеративный дизайн: ИИ создаёт архитектуру и продукты",
]

# Промпты для генерации статей
SYSTEM_PROMPT = """Ты — профессиональный автор технологического блога о искусственном интеллекте. 
Пиши увлекательные, информативные статьи на русском языке.

Правила:
- Используй профессиональную, но доступную лексику
- Добавляй конкретные примеры, цифры и факты
- Структурируй текст: заголовок, вступление, основная часть (3-5 пунктов), заключение
- Длина: 800-1500 слов для развёрнутых тем, 300-500 для коротких
- Добавляй эмодзи для визуального разделения
- В конце каждой статьи добавь теги через # (5-7 релевантных хештегов)
- Будь объективным, избегай сенсационности
"""

# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ КОНТЕНТА
# ═══════════════════════════════════════════════════════════════

class ContentGenerator:
    """Генератор контента через Groq API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.used_topics = set()  # Отслеживание использованных тем

    def get_random_topic(self) -> str:
        """Получить случайную неиспользованную тему"""
        available = [t for t in ARTICLE_TOPICS if t not in self.used_topics]
        if not available:
            self.used_topics.clear()
            available = ARTICLE_TOPICS
        topic = random.choice(available)
        self.used_topics.add(topic)
        return topic

    async def generate_article(self, topic: Optional[str] = None) -> Dict[str, str]:
        """Генерация статьи через Groq API"""
        if not topic:
            topic = self.get_random_topic()

        user_prompt = f"""Напиши подробную статью на тему: "{topic}"

Требования:
1. Придумай цепляющий заголовок (не более 100 символов)
2. Напиши вступление (2-3 предложения)
3. Основная часть: 3-5 разделов с подзаголовками, конкретными примерами
4. Заключение с выводами
5. Добавь 5-7 хештегов в конце
6. Общий объём: 800-1200 слов

Формат ответа (строго JSON):
{{
    "title": "Заголовок статьи",
    "content": "Полный текст статьи с разметкой",
    "hashtags": "#тег1 #тег2 #тег3 #тег4 #тег5"
}}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "response_format": {"type": "json_object"}
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 429:
                        logger.warning("⏳ Groq rate limit! Ждём 60 секунд...")
                        await asyncio.sleep(60)
                        return await self.generate_article(topic)

                    response.raise_for_status()
                    data = await response.json()

                    content = data["choices"][0]["message"]["content"]
                    article_data = json.loads(content)

                    logger.info(f"✅ Статья сгенерирована: {article_data.get('title', 'Без заголовка')[:50]}...")
                    return article_data

            except Exception as e:
                logger.error(f"❌ Ошибка генерации статьи: {e}")
                return self._fallback_article(topic)

    def _fallback_article(self, topic: str) -> Dict[str, str]:
        """Резервная статья при ошибке API"""
        return {
            "title": f"🤖 {topic}",
            "content": f"""🔍 {topic}

Сегодня мы рассмотрим одну из самых актуальных тем в сфере искусственного интеллекта.

📌 Ключевые моменты:
• ИИ продолжает стремительно развиваться
• Новые технологии открывают безграничные возможности
• Важно следить за этическими аспектами развития

💡 Вывод: будущее за интеграцией ИИ в повседневную жизнь.

Статья подготовлена автоматически.""",
            "hashtags": "#ИИ #Технологии #ИскусственныйИнтеллект #AI #Новости"
        }

    async def generate_image_prompt(self, article_title: str) -> str:
        """Генерация промпта для картинки на основе заголовка"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt_request = f"""Создай короткий промпт (на английском, 10-15 слов) для генерации изображения к статье с заголовком: "{article_title}"

Требования:
- Опиши визуальную сцену
- Добавь стиль: digital art, futuristic, high quality
- Только промпт, без пояснений

Ответь одной строкой."""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Ты создаёшь промпты для генерации изображений. Отвечай кратко."},
                {"role": "user", "content": prompt_request}
            ],
            "temperature": 0.8,
            "max_tokens": 100
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    prompt = data["choices"][0]["message"]["content"].strip().strip('"')
                    # Добавляем стилистику
                    prompt += ", digital art, futuristic, high quality, 4k, detailed"
                    logger.info(f"🎨 Промпт для картинки: {prompt[:80]}...")
                    return prompt
            except Exception as e:
                logger.error(f"❌ Ошибка генерации промпта: {e}")
                return "futuristic artificial intelligence, digital art, high quality, 4k, detailed"


# ═══════════════════════════════════════════════════════════════
# TELEGRAM ПУБЛИКАЦИЯ
# ═══════════════════════════════════════════════════════════════

class TelegramPublisher:
    """Публикация контента в Telegram"""

    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_photo_with_caption(self, photo_url: str, caption: str) -> bool:
        """Отправить фото с подписью в канал"""
        # Telegram ограничивает caption 1024 символами
        if len(caption) > 1024:
            # Разбиваем: фото с короткой подписью + отдельное текстовое сообщение
            short_caption = caption[:1000] + "..."

            async with aiohttp.ClientSession() as session:
                # Отправляем фото
                photo_payload = {
                    "chat_id": self.channel_id,
                    "photo": photo_url,
                    "caption": short_caption,
                    "parse_mode": "HTML"
                }

                try:
                    async with session.post(
                        f"{self.base_url}/sendPhoto",
                        json=photo_payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            logger.info("📸 Фото отправлено")
                            # Отправляем оставшийся текст
                            remaining_text = caption[1000:]
                            if remaining_text:
                                await self.send_text(remaining_text)
                            return True
                        else:
                            error = await response.text()
                            logger.error(f"❌ Ошибка отправки фото: {error}")
                            return False
                except Exception as e:
                    logger.error(f"❌ Ошибка: {e}")
                    return False
        else:
            # Короткая подпись — отправляем всё одним сообщением
            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": self.channel_id,
                    "photo": photo_url,
                    "caption": caption,
                    "parse_mode": "HTML"
                }

                try:
                    async with session.post(
                        f"{self.base_url}/sendPhoto",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            logger.info("📸 Пост с фото отправлен")
                            return True
                        else:
                            error = await response.text()
                            logger.error(f"❌ Ошибка: {error}")
                            return False
                except Exception as e:
                    logger.error(f"❌ Ошибка: {e}")
                    return False

    async def send_text(self, text: str) -> bool:
        """Отправить текстовое сообщение"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "chat_id": self.channel_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }

            try:
                async with session.post(
                    f"{self.base_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        logger.info("📝 Текст отправлен")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"❌ Ошибка отправки текста: {error}")
                        return False
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")
                return False


# ═══════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС БОТА
# ═══════════════════════════════════════════════════════════════

class AITelegramBot:
    """Главный класс автономного бота"""

    def __init__(self):
        self.content_gen = ContentGenerator(GROQ_API_KEY)
        self.publisher = TelegramPublisher(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
        self.running = True

    def get_pollinations_url(self, prompt: str, width: int = 1024, height: int = 768) -> str:
        """Формирование URL для генерации картинки через Pollinations"""
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        # Pollinations.ai — бесплатный API без ключа
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={random.randint(1, 999999)}"

    async def publish_article(self):
        """Полный цикл: генерация + публикация"""
        logger.info("🚀 Начинаем цикл публикации...")

        try:
            # 1. Генерируем статью
            article = await self.content_gen.generate_article()
            title = article.get("title", "Без заголовка")
            content = article.get("content", "")
            hashtags = article.get("hashtags", "")

            # 2. Формируем полный текст поста
            full_text = f"<b>{title}</b>\n\n{content}\n\n{hashtags}"

            # 3. Генерируем промпт для картинки
            image_prompt = await self.content_gen.generate_image_prompt(title)

            # 4. Формируем URL картинки
            image_url = self.get_pollinations_url(image_prompt)

            # 5. Публикуем
            success = await self.publisher.send_photo_with_caption(image_url, full_text)

            if success:
                logger.info(f"✅ Пост опубликован: {title[:60]}...")
            else:
                # Fallback: отправляем только текст
                logger.warning("⚠️ Отправляем только текст...")
                text_only = f"📰 {title}\n\n{content}\n\n{hashtags}"
                await self.publisher.send_text(text_only)

        except Exception as e:
            logger.error(f"❌ Критическая ошибка в цикле: {e}")

    async def run_scheduler(self):
        """Главный цикл планировщика"""
        logger.info("🤖 Бот запущен! Ожидаем расписание...")
        logger.info(f"📅 Расписание публикаций (UTC): {PUBLISH_SCHEDULE}")

        while self.running:
            now = datetime.utcnow()
            current_hour = now.hour

            # Проверяем, нужно ли публиковать сейчас
            if current_hour in PUBLISH_SCHEDULE and now.minute == 0:
                logger.info(f"⏰ Время публикации! {now.strftime('%H:%M')} UTC")
                await self.publish_article()

                # Ждём 61 минуту, чтобы не опубликовать дважды
                await asyncio.sleep(3660)
            else:
                # Ждём до следующей проверки (каждую минуту)
                await asyncio.sleep(60)

    async def run_once(self):
        """Одноразовый запуск (для теста)"""
        logger.info("🧪 Тестовый запуск...")
        await self.publish_article()


# ═══════════════════════════════════════════════════════════════
# ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════

async def main():
    bot = AITelegramBot()

    # Проверяем конфигурацию
    if TELEGRAM_BOT_TOKEN == "ВСТАВЬ_СЮДА_ТОКЕН_БОТА":
        logger.error("❌ Не настроен TELEGRAM_BOT_TOKEN!")
        logger.info("💡 Запусти: export TELEGRAM_BOT_TOKEN='твой_токен'")
        return

    if TELEGRAM_CHANNEL_ID == "ВСТАВЬ_СЮДА_ID_КАНАЛА":
        logger.error("❌ Не настроен TELEGRAM_CHANNEL_ID!")
        logger.info("💡 Запусти: export TELEGRAM_CHANNEL_ID='@твой_канал'")
        return

    if GROQ_API_KEY == "ВСТАВЬ_СЮДА_GROQ_API_KEY":
        logger.error("❌ Не настроен GROQ_API_KEY!")
        logger.info("💡 Запусти: export GROQ_API_KEY='твой_ключ'")
        return

    # Режим работы
    mode = os.getenv("BOT_MODE", "scheduler")  # scheduler или once

    if mode == "once":
        await bot.run_once()
    else:
        await bot.run_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
