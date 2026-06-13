import asyncio
import logging
import sys
from telegram import Bot
from telegram.constants import ParseMode
import aiohttp
from io import BytesIO
from typing import Optional
import signal
import os
from aiohttp import web

from config import BOT_TOKEN, CHANNEL_ID, CHECK_INTERVAL, MAX_NEWS_PER_CYCLE, PUBLISH_DELAY, DEBUG
from sources import NewsCollector, NewsItem

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG if DEBUG else logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class TechNewsBot:
    def __init__(self):
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not CHANNEL_ID:
            raise ValueError("CHANNEL_ID environment variable is required")
        
        self.bot = Bot(token=BOT_TOKEN)
        self.collector = NewsCollector()
        self.is_running = False
        self._shutdown = False
        
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        logger.info("Received shutdown signal, stopping gracefully...")
        self._shutdown = True
        self.is_running = False
    
    async def download_image(self, url: str) -> Optional[BytesIO]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type:
                            data = await response.read()
                            if len(data) < 10 * 1024 * 1024:
                                return BytesIO(data)
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
        return None
    
    async def publish_news(self, news_item: NewsItem) -> bool:
        try:
            text = f"<b>{self._escape_html(news_item.title)}</b>\n\n"
            
            if news_item.text:
                text += f"{self._escape_html(news_item.text)}\n\n"
            
            text += f"🔗 <a href=\"{news_item.url}\">Читать далее</a>"
            text += "\n\n#технологии #новости #IT"
            
            if news_item.image_url:
                image = await self.download_image(news_item.image_url)
                if image:
                    try:
                        await self.bot.send_photo(
                            chat_id=CHANNEL_ID,
                            photo=image,
                            caption=text[:1024],
                            parse_mode=ParseMode.HTML
                        )
                        return True
                    except Exception as e:
                        logger.error(f"Error sending photo: {e}")
                        pass
            
            await self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text[:4096],
                parse_mode=ParseMode.HTML
            )
            return True
            
        except Exception as e:
            logger.error(f"Error publishing news: {e}")
            return False
    
    def _escape_html(self, text: str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    async def news_cycle(self):
        while not self._shutdown:
            try:
                logger.info("Starting news collection cycle...")
                news = self.collector.collect_news()
                
                if not news:
                    logger.info("No new relevant news found")
                else:
                    logger.info(f"Found {len(news)} news items")
                    
                    published = 0
                    for item in news[:MAX_NEWS_PER_CYCLE]:
                        if self._shutdown:
                            break
                        
                        if await self.publish_news(item):
                            published += 1
                            self.collector.mark_as_published(item)
                            logger.info(f"Published: {item.title[:50]}...")
                        
                        await asyncio.sleep(PUBLISH_DELAY)
                    
                    logger.info(f"Cycle completed. Published {published} news items")
                
            except Exception as e:
                logger.error(f"Error in news cycle: {e}")
            
            for _ in range(CHECK_INTERVAL):
                if self._shutdown:
                    break
                await asyncio.sleep(1)
    
    async def run(self):
        self.is_running = True
        logger.info(f"Bot started. Channel: {CHANNEL_ID}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
        
        try:
            await self.news_cycle()
        finally:
            logger.info("Bot stopped")
            await self.bot.close()


async def health_check(request):
    return web.Response(text="OK", status=200)


async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080")))
    await site.start()
    logger.info(f"Web server started on port {os.getenv('PORT', '8080')}")


async def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable is required")
        sys.exit(1)
    
    if not CHANNEL_ID:
        print("ERROR: CHANNEL_ID environment variable is required")
        sys.exit(1)
    
    await start_web_server()
    
    bot = TechNewsBot()
    await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
