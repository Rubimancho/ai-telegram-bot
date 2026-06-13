import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import json
import os
from typing import List, Optional
from dataclasses import dataclass
import re
import time

@dataclass
class NewsItem:
    title: str
    text: str
    url: str
    image_url: str = None
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
        self._recent_texts = []
        
        self.channels = [
            # Пользовательские каналы
            "technomedia",
            "pda_4",
            "pekagame",
            "media1337",
            "igmggoficial",
            
            # Технологии и гаджеты
            "iguides",
            "sdelano_u_nas",
            "4pda_news",
            "kaktutz",
            "hi_tech_mail",
            "gagadget",
            "rozetked",
            "tbtech",
            "androidinsider",
            "3dnews",
            
            # Игры
            "igromania",
            "stopgame",
            "dtf",
            "gamedev_dtf",
            
            # IT и наука
            "habr_com",
            "nplus1",
            "vc",
            "caboronda",
            
            # Видео и обзоры
            "Wylsacom",
            "TheDigger",
            "TechMax",
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
        if len(self.published_hashes) > 2000:
            self.published_hashes = set(list(self.published_hashes)[-2000:])
        with open(self.published_hashes_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.published_hashes), f)
    
    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_image(self, soup_element) -> Optional[str]:
        photo_wrap = soup_element.find('a', class_='tgme_widget_message_photo_wrap')
        if photo_wrap:
            style = photo_wrap.get('style', '')
            match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
            if match:
                return match.group(1)
        
        link_preview = soup_element.find('a', class_='tgme_widget_message_link_preview')
        if link_preview:
            style = link_preview.get('style', '')
            match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
            if match:
                return match.group(1)
        
        img = soup_element.find('img', class_='tgme_widget_message_photo')
        if img and img.get('src'):
            return img['src']
        
        return None
    
    def collect_channel_news(self) -> List[NewsItem]:
        news_items = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for channel in self.channels:
            try:
                url = f"https://t.me/s/{channel}"
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    print(f"Cannot access channel {channel}: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                messages = soup.find_all('div', class_='tgme_widget_message_wrap')
                
                for msg in messages[:10]:
                    text_el = msg.find('div', class_='tgme_widget_message_text')
                    if not text_el:
                        continue
                    
                    raw_text = str(text_el)
                    clean_text = self._clean_html(raw_text)
                    
                    if not clean_text or len(clean_text) < 20:
                        continue
                    
                    title = clean_text[:120].split('.')[0] if '.' in clean_text else clean_text[:120]
                    
                    link_el = msg.find('a', class_='tgme_widget_message_date')
                    post_url = link_el['href'] if link_el and link_el.get('href') else f"https://t.me/s/{channel}"
                    
                    image_url = self._extract_image(msg)
                    
                    news_item = NewsItem(
                        title=title,
                        text=clean_text,
                        url=post_url,
                        image_url=image_url,
                        source=channel,
                    )
                    
                    if news_item.hash not in self.published_hashes:
                        news_items.append(news_item)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error collecting from {channel}: {e}")
                continue
        
        return news_items
    
    def _is_similar(self, text1: str, text2: str) -> bool:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return False
        common = words1 & words2
        similarity = len(common) / min(len(words1), len(words2))
        return similarity > 0.5
    
    def _is_duplicate(self, news_item: NewsItem) -> bool:
        for h in self.published_hashes:
            for recent in self._recent_texts:
                if self._is_similar(news_item.text, recent):
                    return True
        return False
    
    def collect_news(self) -> List[NewsItem]:
        news = self.collect_channel_news()
        
        unique = []
        seen_texts = []
        for item in news:
            is_dup = False
            for existing in seen_texts:
                if self._is_similar(item.text, existing):
                    is_dup = True
                    break
            
            if not is_dup:
                unique.append(item)
                seen_texts.append(item.text)
        
        return unique[:10]
    
    def mark_as_published(self, news_item: NewsItem):
        self.published_hashes.add(news_item.hash)
        self._recent_texts.append(news_item.text)
        if len(self._recent_texts) > 50:
            self._recent_texts = self._recent_texts[-50:]
        self._save_published_hashes()
