import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import json
import os
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class NewsItem:
    title: str
    text: str
    url: str
    image_url: str = None
    video_url: str = None
    source: str = ""
    published: datetime = None
    
    def __post_init__(self):
        if self.published is None:
            self.published = datetime.now()
        self.hash = hashlib.md5(f"{self.title}{self.url}".encode()).hexdigest()

class NewsCollector:
    def __init__(self):
        self.published_hashes_file = "published_news.json"
        self.published_hashes = self._load_published_hashes()
        
        # Бесплатные RSS-фиды новостей на русском
        self.rss_feeds = [
            # Общие новости
            "https://www.kommersant.ru/RSS/news.xml",
            "https://lenta.ru/rss",
            "https://www.gazeta.ru/export/rss/tech.xml",
            "https://ria.ru/rss/",
            "https://tass.ru/rss/v1.xml",
            "https://www.rbc.ru/rss/",
            "https://www.rbc.ru/v20/feeds/all",
            "https://www.fontanka.ru/rss/news.xml",
            
            # Технологии и IT
            "https://3dnews.ru/rss",
            "https://habr.com/ru/rss/hubs/all/",
            "https://www.ixbt.com/rss/",
            "https://techcrunch.com/feed/",
            "https://www.techpowerup.com/rss/",
            "https://www.overclockers.ru/rss.xml",
            "https://hardwaresfera.com/rss.xml",
            "https://trashbox.ru/link/rss.xml",
            "https://4pda.to/feed/",
            
            # Игры
            "https://stopgame.ru/rss.xml",
            "https://dtf.ru/rss",
            "https://www.igromania.ru/rss/",
            "https://gameguru.ru/rss.xml",
            "https://www.cubik.com/rss.xml",
            "https://www.my-games.com/rss/",
            "https://www.gametracker.com/rss/",
            "https://www.metacritic.com/rss/games",
            
            # Наука и техника
            "https://nplus1.ru/feed",
            "https://scientificrussia.ru/rss",
            "https://www.naked-science.ru/feed",
            "https://www.popmech.ru/rss/",
            "https://www.vokrugsveta.ru/rss/",
            
            # Мобильные технологии
            "https://mobile-review.com/feed/",
            "https://hi-tech.mail.ru/review/rss/",
            "https://www.androidauthority.com/feed/",
            "https://www.phonearena.com/rss",
        ]
        
        # Ключевые слова для фильтрации (technology, games, computer topics)
        self.keywords = [
            # Технологии
            "технологии", "техника", "компьютер", "смартфон", "телефон",
            "процессор", "видеокарта", "ноутбук", "планшет", "гаджет",
            "софт", "программа", "приложение", "интернет", "сеть",
            "人工智能", "нейросеть", "робот", "автоматизация",
            "кибербезопасность", "хакер", "вирус", "безопасность",
            "облачные технологии", "сервер", "дата-центр",
            "5G", "6G", "Wi-Fi", "Bluetooth", "NFC",
            "виртуальная реальность", "дополненная реальность",
            "blockchain", "криптовалюта", "биткоин", "эфириум",
            
            # Компьютеры и комплектующие
            "Intel", "AMD", "NVIDIA", "GeForce", "Radeon",
            "Windows", "Linux", "macOS", "Android", "iOS",
            "SSD", "HDD", "RAM", "процессор", "материнская плата",
            "блок питания", "корпус", "охлаждение", "водяное охлаждение",
            
            # Игры
            "игры", "игровая", "геймер", "консоль", "playstation", "xbox",
            "nintendo", "steam", "epic games", "Origin",
            "PlayStation 5", "PS5", "Xbox Series", "Nintendo Switch",
            "игровой", "геймплей", "геймер", "стрим", "киберспорт",
            "Dota", "CS", "Counter-Strike", "Valorant", "League of Legends",
            "Fortnite", "Minecraft", "GTA", "Cyberpunk", "Assassin's Creed",
            
            # Софт и приложения
            "Windows 11", "Windows 10", "Office", "Microsoft",
            "Google", "Apple", "Samsung", "Xiaomi", "Huawei",
            "Telegram", "WhatsApp", "Instagram", "TikTok",
            "браузер", "Chrome", "Firefox", "Edge", "Safari",
            "антивирус", "фаервол", "VPN",
            
            # Разработка
            "программирование", "разработка", "код", "программист",
            "Python", "JavaScript", "Java", "C++", "Swift",
            "frontend", "backend", "девелопмент", "девелопер",
            "API", "REST", "GraphQL", "SQL", "NoSQL",
            
            # Гаджеты и устройства
            "наушники", "колонка", "умный дом", "IoT",
            "фитнес-браслет", "умные часы", "Apple Watch",
            "无人机", "дрон", "робот-пылесос", "умная колонка",
            
            # Источники энергии и экология
            "аккумулятор", "батарея", "зарядка", "беспроводная зарядка",
            "солнечная энергия", "экология", "переработка",
        ]
    
    def _load_published_hashes(self) -> set:
        if os.path.exists(self.published_hashes_file):
            try:
                with open(self.published_hashes_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def _save_published_hashes(self):
        # Оставляем только последние 1000 хешей
        if len(self.published_hashes) > 1000:
            self.published_hashes = set(list(self.published_hashes)[-1000:])
        
        with open(self.published_hashes_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.published_hashes), f)
    
    def _is_relevant(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_image(self, entry: dict) -> Optional[str]:
        # Проверяем разные форматы RSS для изображений
        if 'media_content' in entry:
            for media in entry['media_content']:
                if media.get('medium') == 'image' or 'image' in media.get('type', ''):
                    return media.get('url')
        
        if 'media_thumbnail' in entry:
            return entry['media_thumbnail'][0].get('url')
        
        if 'enclosures' in entry:
            for enc in entry['enclosures']:
                if 'image' in enc.get('type', ''):
                    return enc.get('href') or enc.get('url')
        
        # Пытаемся найти изображение в контенте
        content = entry.get('content', [{}])
        if content and isinstance(content, list):
            content = content[0].get('value', '')
        else:
            content = str(content)
        
        img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
        if img_match:
            return img_match.group(1)
        
        return None
    
    def collect_rss_news(self) -> List[NewsItem]:
        news_items = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for feed_url in self.rss_feeds:
            try:
                response = requests.get(feed_url, headers=headers, timeout=15)
                if response.status_code != 200:
                    continue
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:15]:
                    title = entry.get('title', '').strip()
                    text = entry.get('summary', '') or entry.get('description', '')
                    url = entry.get('link', '')
                    
                    if not title or not url:
                        continue
                    
                    # Проверяем релевантность
                    full_text = f"{title} {text}"
                    if not self._is_relevant(full_text):
                        continue
                    
                    # Берём полный текст из content, если есть
                    content = entry.get('content', [{}])
                    if content and isinstance(content, list):
                        full_content = content[0].get('value', '')
                    else:
                        full_content = text
                    
                    if len(full_content) > len(text):
                        clean_text = self._clean_html(full_content)[:2000]
                    else:
                        clean_text = self._clean_html(text)[:2000]
                    
                    # Извлекаем изображение
                    image_url = self._extract_image(entry)
                    
                    news_item = NewsItem(
                        title=title,
                        text=clean_text,
                        url=url,
                        image_url=image_url,
                        source=feed_url.split('/')[2],
                    )
                    
                    if news_item.hash not in self.published_hashes:
                        news_items.append(news_item)
                        
            except Exception as e:
                print(f"Error parsing RSS {feed_url}: {e}")
                continue
        
        return news_items
    
    def collect_news(self) -> List[NewsItem]:
        all_news = self.collect_rss_news()
        
        # Убираем дубликаты
        unique_news = {}
        for item in all_news:
            if item.hash not in unique_news:
                unique_news[item.hash] = item
        
        return list(unique_news.values())
    
    def mark_as_published(self, news_item: NewsItem):
        self.published_hashes.add(news_item.hash)
        self._save_published_hashes()
