# POLNAYA INSTRUKCIYA: Avtonomnyy AI-kanal v Telegram
## Vse besplatno. Vse kody vklyucheny. Po shagam.

---

## CHAST 1. CHTO BUDEM DELAT

My sozdadim Telegram-kanal, v kotoryy avtomaticheski budut publikovatsya stati ob II i tekhnologiyakh s kartinkami. Bot rabotayet 24/7 na besplatnom servere.

**Ispolzuemye servisy (vse besplatnye):**
- Telegram — kanal i bot
- Groq API — generatsiya tekstov (14 400 zaprosov/den besplatno)
- Pollinations.ai — generatsiya kartinok (bezlimitno, bez klyucha)
- Render.com — besplatnyy server
- GitHub — khranenie koda

---

## CHAST 2. SHAG 1 — SOZDAYOM TELEGRAM-KANAL I BOTA

### 2.1 Sozdanie kanala

1. Otkroy prilozhenie Telegram
2. Nazhmi na ikonku karandasha (sozdat novoe)
3. Vyberi "Novyy kanal"
4. Vvedi nazvanie kanala, naprimer: `AI Daily | Novosti II`
5. Vvedi opisanie, naprimer: `Avtonomnyy kanal ob iskusstvennom intellekte i tekhnologiyakh`
6. Nazhmi "Sozdat"
7. Vyberi **"Publichnyy kanal"**
8. Pridumay korotkiy adres (username), naprimer: `ai_daily_news`
   - Eto vazhno! Zapomni ego — on ponadobitsya pozzhe
   - Dolzhen byt unikalnym i okanchivatsya na bukvy/tsifry
9. Nazhmi "Gotovo"

**Zapishi username kanala.** On vyglyadit tak: `@ai_daily_news`

### 2.2 Sozdanie bota cherez @BotFather

1. V poiske Telegram naydi: `@BotFather`
2. Nazhmi "Start" ili otprav komandu `/start`
3. Otprav komandu: `/newbot`
4. BotFather sprosit imya bota — vvedi: `AI Publisher`
5. BotFather sprosit username — vvedi chto-to tipa: `ai_publisher_yourname_bot`
   - Obyazatelno dolzhen zakanchivatsya na `_bot`
   - Dolzhen byt unikalnym po vsemu Telegram
6. **BotFather vydast token.** Vyglyadit primerno tak:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   ```

**Skopiruy i sohrani etot token!** Eto parol ot tvoego bota. Nikomu ne pokazyvay.

### 2.3 Dobavlyaem bota administratorom kanala

1. Zaydi v svoy kanal
2. Nazhmi na nazvanie kanala sverkhu
3. Nazhmi na tri tochki (menyu) → "Upravlenie kanalom"
4. Vyberi "Administratoriy"
5. Nazhmi "Dobavit administratora"
6. Naydi svoyego bota po imeni (naprimer, `@ai_publisher_yourname_bot`)
7. Nazhmi na nego
8. **Vazhno:** vklyuchi galochku "Publikatsiya soobshcheniy"
9. Nazhmi "Gotovo"

**Proverka:** otprav v kanal lyuboe soobshchenie. Zatem pereshli ego botu. Yesli bot otvetit — vse rabotayet.

---

## CHAST 3. SHAG 2 — POLUCHAEM API-KLYUCH GROQ

Groq — eto servis, kotoryy dayet besplatnyy dostup k moshchnym II-modelyam (Llama, Mixtral).

1. Otkroy v brauzere: `https://console.groq.com`
2. Nazhmi "Sign Up" (Registratsiya)
3. Zaregistriruysya cherez Google-akkaunt (samyy prostoy sposob)
4. Posle vkhoda nazhmi na "API Keys" v levom menyu
5. Nazhmi knopku "Create API Key"
6. Vvedi nazvanie klyucha, naprimer: `telegram-bot`
7. Nazhmi "Submit"
8. **Skopiruy klyuch!** Vyglyadit tak:
   ```
   gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Sohrani etot klyuch!** On ponadobitsya dlya nastroiki bota.

> Limity besplatnogo tarifa Groq: 30 zaprosov/minutu, 14 400 zaprosov/den. Dlya 4 postov v den etogo bolee chem dostatochno.

---

## CHAST 4. SHAG 3 — SOZDAYOM AKKAUNT NA GITHUB

GitHub nuzhen dlya khraneniya koda bota. Render budet brat kod ottuda.

1. Otkroy: `https://github.com`
2. Nazhmi "Sign up" v pravom verkhнем uglu
3. Vvedi email, pridumay parol, vvedi username
4. Proydi proverku (kaptcha)
5. Podtverdi email (zaydi v pochtu, nazhmi na ssylku)
6. Vyberi "Just me" i "Student" ili "Hobby"
7. Nazhmi "Continue" neskolko raz

### 4.1 Sozdayom repozitoriy

1. Na glavnoy stranitse GitHub nazhmi zelenuyu knopku "New" ili "+" → "New repository"
2. V pole "Repository name" vvedi: `ai-telegram-bot`
3. Vyberi "Public" (publichnyy)
4. Postav galochku "Add a README file"
5. Nazhmi "Create repository"

### 4.2 Zagruzhayem fayly bota

1. Vnutri repozitoriya nazhmi "Add file" → "Upload files"
2. Peretashchi tuda fayly iz skachannogo arkhiva (ili sozday ikh po kodu nizhe)
3. Nazhmi "Commit changes"

**Vazhno:** tebe nuzhno sozdat 4 fayla v repozitorii. Vot ikh soderzhanie:

---

### FAYL 1: main.py

Sozday fayl s imenem `main.py` i vstavy etot kod:

```python
import os
import json
import random
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

PUBLISH_SCHEDULE = [5, 9, 13, 17]

ARTICLE_TOPICS = [
    "Latest achievements in generative AI",
    "How neural networks are changing medicine",
    "AI in education: personalized learning",
    "Ethics of artificial intelligence",
    "Future of work: how AI will change the labor market",
    "Neural networks and creativity",
    "AI in business: automation and analytics",
    "Quantum computing and AI",
    "Speech recognition: breakthroughs and technologies",
    "Computer vision: from face recognition to autopilots",
    "Comparison of language models: GPT, Claude, Gemini, Llama",
    "Multimodal AI: text, images, video in one model",
    "Small language models: efficiency on mobile devices",
    "Agent AI: autonomous decision-making systems",
    "RAG systems: how AI works with external data",
    "Fine-tuning vs Prompt Engineering",
    "AI infrastructure: GPU, TPU, LPU comparison",
    "Neural network optimization: quantization and distillation",
    "Top 10 free AI tools for productivity",
    "How to create your own AI assistant without programming",
    "AI in marketing: personalization and targeting",
    "Next-gen chatbots: from simple answers to agents",
    "AI for programmers: autocomplete, code review, generation",
    "Video generation with AI: Sora, Runway and analogues",
    "AI in scientific research",
    "Personal AI assistants: future or reality",
    "AI regulation in 2026: laws and norms",
    "Investments in AI: where billions are invested",
    "Open Source AI: why open models matter",
    "AI and cybersecurity",
    "Green AI: ecology of computing",
    "Neurointerfaces: brain-computer connection",
    "AI in space: exploring the universe",
    "Emotional AI: recognition and generation of emotions",
    "Transformers: how modern language models work",
    "Diffusion models: generating images from noise",
    "Graph neural networks: analyzing connections",
    "Reinforcement learning: from games to robotics",
    "Federated learning: privacy and collaboration",
    "Neural networks on the edge: Edge AI and IoT",
    "AI and blockchain: synergy of technologies",
    "Generative design: AI creates architecture",
]

SYSTEM_PROMPT = """You are a professional technology blog author about artificial intelligence. Write engaging, informative articles in Russian.

Rules:
- Use professional but accessible vocabulary
- Add specific examples, numbers and facts
- Structure text: heading, introduction, main part (3-5 points), conclusion
- Length: 800-1500 words for detailed topics, 300-500 for short ones
- Add emojis for visual separation
- At the end add tags via # (5-7 relevant hashtags)
- Be objective, avoid sensationalism
"""

class ContentGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.used_topics = set()

    def get_random_topic(self) -> str:
        available = [t for t in ARTICLE_TOPICS if t not in self.used_topics]
        if not available:
            self.used_topics.clear()
            available = ARTICLE_TOPICS
        topic = random.choice(available)
        self.used_topics.add(topic)
        return topic

    async def generate_article(self, topic: Optional[str] = None) -> Dict[str, str]:
        if not topic:
            topic = self.get_random_topic()

        user_prompt = f"""Write a detailed article on the topic: "{topic}"

Requirements:
1. Come up with a catchy headline (max 100 characters)
2. Write an introduction (2-3 sentences)
3. Main part: 3-5 sections with subheadings, specific examples
4. Conclusion with findings
5. Add 5-7 hashtags at the end
6. Total volume: 800-1200 words

Format response (strict JSON):
{{
    "title": "Article headline",
    "content": "Full article text with markup",
    "hashtags": "#tag1 #tag2 #tag3 #tag4 #tag5"
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
                        logger.warning("Rate limit! Waiting 60 seconds...")
                        await asyncio.sleep(60)
                        return await self.generate_article(topic)

                    response.raise_for_status()
                    data = await response.json()

                    content = data["choices"][0]["message"]["content"]
                    article_data = json.loads(content)

                    logger.info(f"Article generated: {article_data.get('title', 'No title')[:50]}...")
                    return article_data

            except Exception as e:
                logger.error(f"Error generating article: {e}")
                return self._fallback_article(topic)

    def _fallback_article(self, topic: str) -> Dict[str, str]:
        return {
            "title": f"{topic}",
            "content": f"""{topic}

Today we look at one of the most relevant topics in artificial intelligence.

Key points:
- AI continues to develop rapidly
- New technologies open up limitless possibilities
- It is important to monitor the ethical aspects of development

Conclusion: the future lies in integrating AI into everyday life.

Article prepared automatically.""",
            "hashtags": "#AI #Technology #ArtificialIntelligence #Innovation #News"
        }

    async def generate_image_prompt(self, article_title: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt_request = f"""Create a short prompt (in English, 10-15 words) for generating an image for an article with the headline: "{article_title}"

Requirements:
- Describe a visual scene
- Add style: digital art, futuristic, high quality
- Only the prompt, no explanations

Answer in one line."""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You create image generation prompts. Answer briefly."},
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
                    prompt += ", digital art, futuristic, high quality, 4k, detailed"
                    logger.info(f"Image prompt: {prompt[:80]}...")
                    return prompt
            except Exception as e:
                logger.error(f"Error generating prompt: {e}")
                return "futuristic artificial intelligence, digital art, high quality, 4k, detailed"


class TelegramPublisher:
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_photo_with_caption(self, photo_url: str, caption: str) -> bool:
        if len(caption) > 1024:
            short_caption = caption[:1000] + "..."

            async with aiohttp.ClientSession() as session:
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
                            logger.info("Photo sent")
                            remaining_text = caption[1000:]
                            if remaining_text:
                                await self.send_text(remaining_text)
                            return True
                        else:
                            error = await response.text()
                            logger.error(f"Error sending photo: {error}")
                            return False
                except Exception as e:
                    logger.error(f"Error: {e}")
                    return False
        else:
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
                            logger.info("Post with photo sent")
                            return True
                        else:
                            error = await response.text()
                            logger.error(f"Error: {error}")
                            return False
                except Exception as e:
                    logger.error(f"Error: {e}")
                    return False

    async def send_text(self, text: str) -> bool:
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
                        logger.info("Text sent")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Error sending text: {error}")
                        return False
            except Exception as e:
                logger.error(f"Error: {e}")
                return False


class AITelegramBot:
    def __init__(self):
        self.content_gen = ContentGenerator(GROQ_API_KEY)
        self.publisher = TelegramPublisher(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
        self.running = True

    def get_pollinations_url(self, prompt: str, width: int = 1024, height: int = 768) -> str:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={random.randint(1, 999999)}"

    async def publish_article(self):
        logger.info("Starting publication cycle...")

        try:
            article = await self.content_gen.generate_article()
            title = article.get("title", "No title")
            content = article.get("content", "")
            hashtags = article.get("hashtags", "")

            full_text = f"<b>{title}</b>\n\n{content}\n\n{hashtags}"

            image_prompt = await self.content_gen.generate_image_prompt(title)
            image_url = self.get_pollinations_url(image_prompt)

            success = await self.publisher.send_photo_with_caption(image_url, full_text)

            if success:
                logger.info(f"Post published: {title[:60]}...")
            else:
                logger.warning("Sending text only...")
                text_only = f"{title}\n\n{content}\n\n{hashtags}"
                await self.publisher.send_text(text_only)

        except Exception as e:
            logger.error(f"Critical error in cycle: {e}")

    async def run_scheduler(self):
        logger.info("Bot started! Waiting for schedule...")
        logger.info(f"Publication schedule (UTC): {PUBLISH_SCHEDULE}")

        while self.running:
            now = datetime.utcnow()
            current_hour = now.hour

            if current_hour in PUBLISH_SCHEDULE and now.minute == 0:
                logger.info(f"Publication time! {now.strftime('%H:%M')} UTC")
                await self.publish_article()
                await asyncio.sleep(3660)
            else:
                await asyncio.sleep(60)

    async def run_once(self):
        logger.info("Test run...")
        await self.publish_article()


async def main():
    bot = AITelegramBot()

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    if not TELEGRAM_CHANNEL_ID:
        logger.error("TELEGRAM_CHANNEL_ID not set!")
        return

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set!")
        return

    mode = os.getenv("BOT_MODE", "scheduler")

    if mode == "once":
        await bot.run_once()
    else:
        await bot.run_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### FAYL 2: requirements.txt

Sozday fayl s imenem `requirements.txt` i vstavy:

```
aiohttp>=3.9.0
```

---

### FAYL 3: Dockerfile

Sozday fayl s imenem `Dockerfile` (bez rasshireniya) i vstavy:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
```

---

### FAYL 4: render.yaml

Sozday fayl s imenem `render.yaml` i vstavy:

```yaml
services:
  - type: worker
    name: ai-telegram-bot
    runtime: docker
    plan: free
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_CHANNEL_ID
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: BOT_MODE
        value: scheduler
```

---

**Posle sozdaniya vsekh 4 faylov nazhmi "Commit changes" (zelenaya knopka vnizu).**

---

## CHAST 5. SHAG 4 — NASTRAIVAEM RENDER.COM

Render.com — eto besplatnyy oblachnyy server, na kotorom budet rabotat nash bot.

### 5.1 Registratsiya

1. Otkroy: `https://render.com`
2. Nazhmi "Get Started for Free"
3. Vyberi "Continue with GitHub"
4. Avtorizuy Render dostup k svoemu GitHub-akkauntu
5. Vyberi "Just me" → "Continue"

### 5.2 Sozdanie Background Worker

1. V paneli Render nazhmi sinuyu knopku **"New +"** vverkhu
2. Vyberi **"Background Worker"**
3. Vyberi **"Build and deploy from a Git repository"**
4. Nazhmi "Connect account" (esli sprosit) i podklyuchi GitHub
5. Naydi i vyberi svoy repozitoriy `ai-telegram-bot`
6. Nazhmi "Connect"

### 5.3 Nastroyka peremennykh okruzheniya (OChen VAZHNO!)

Prokruti vniz do razdela **"Environment"** (Peremennye okruzheniya).

Nazhmi **"Add Environment Variable"** i dobav 3 peremennye:

| Imya peremennoy | Znachenie | Primer |
|-----------------|-----------|--------|
| `TELEGRAM_BOT_TOKEN` | Token ot @BotFather | `123456789:ABCdef...` |
| `TELEGRAM_CHANNEL_ID` | Username kanala | `@ai_daily_news` |
| `GROQ_API_KEY` | Klyuch ot Groq | `gsk_xxxxxxxx...` |

**Vazhno:**
- Vvodi znacheniya BEZ kavychek
- Dlya kanala ispolzuy format `@username` (s sobachkoy)
- Ubedis, chto net lishnikh probelov

### 5.4 Zapusk

1. Prokruti vverkh i nazhmi **"Create Background Worker"** (vnizu stranitsy)
2. Render nachnet sborku — uvidish logi v realnom vremeni
3. Zhdi 2-3 minuty
4. Yesli v logakh vidish: `Bot started! Waiting for schedule...` — vse rabotayet!

---

## CHAST 6. PROVERKA RABOTY

### 6.1 Testovyy zapusk

1. V paneli Render naydi vkladku **"Shell"** (vverkhu)
2. Vvedi komandu:
   ```
   export BOT_MODE=once && python main.py
   ```
3. Nazhmi Enter
4. Zhdi 30-60 sekund
5. Zaydi v svoy Telegram-kanal — dolzhen poyavitsya post!

### 6.2 Yesli post poyavilsya

1. Verni rezhim planirovshchika:
   - Naydi peremennuyu `BOT_MODE` v razdele Environment
   - Ubedis, chto znachenie = `scheduler`
   - Yesli net — izmeni i nazhmi "Save Changes"

2. Bot teper rabotayet avtomaticheski po raspisaniyu!

### 6.3 Yesli post NE poyavilsya

Prover logi (vkladka "Logs" v Render):

| Oshibka | Reshenie |
|---------|----------|
| `TELEGRAM_BOT_TOKEN not set` | Pereprover peremennuyu TELEGRAM_BOT_TOKEN |
| `Bad Request: chat not found` | Prover TELEGRAM_CHANNEL_ID (dolzhen byt s @) |
| `Unauthorized` | Token bota nevernyy — poluchi novyy u @BotFather |
| `Rate limit` | Normalno, bot avtomaticheski podozhdet i povtorit |
| `GROQ_API_KEY not set` | Pereprover peremennuyu GROQ_API_KEY |

---

## CHAST 7. NASTROYKA RASPISANIYA

Po umolchaniyu bot publikuyet 4 raza v den:
- 08:00 MSK (05:00 UTC)
- 12:00 MSK (09:00 UTC)
- 16:00 MSK (13:00 UTC)
- 20:00 MSK (17:00 UTC)

### Kak izmenit raspisanie

1. V GitHub otkroy fayl `main.py`
2. Naydi stroku:
   ```python
   PUBLISH_SCHEDULE = [5, 9, 13, 17]
   ```
3. Izmeni chisla (vremya v UTC):

| Chto khochesh | Kod |
|---------------|-----|
| Kazhdyy chas | `PUBLISH_SCHEDULE = list(range(24))` |
| 2 raza v den (utro/vecher) | `PUBLISH_SCHEDULE = [6, 18]` |
| 3 raza v den | `PUBLISH_SCHEDULE = [7, 12, 17]` |
| Tolko nochyu | `PUBLISH_SCHEDULE = [1, 2, 3, 4, 5]` |

> Pomni: MSK = UTC + 3 (letom) ili UTC + 2 (zimoy)

4. Nazhmi "Commit changes"
5. Render avtomaticheski perезapustit bota s novym raspisaniem

---

## CHAST 8. LIMITY BESPLATNYKH TARIFOV

| Servis | Limit | Khvatit dlya |
|--------|-------|--------------|
| Groq API | 14 400 zaprosov/den | Do 24 postov/den |
| Pollinations.ai | Bezlimitno | Lyuboe kolichestvo kartinok |
| Render.com | 750 chasov/mes | Rabotayet 24/7 |
| Telegram API | 30 soobshcheniy/sek | Ne ogranichevayet |

---

## CHAST 9. BEZOPASNOST

**Nikogda ne publikuy eti dannye:**
- TELEGRAM_BOT_TOKEN
- GROQ_API_KEY

Yesli sluchayno kto-to uvidel token:
1. Zaydi k @BotFather
2. Otprav `/revoke`
3. Vyberi svoyego bota
4. Poluchi novyy token
5. Obnovi peremennuyu v Render

---

## CHAST 10. CHTO DELAT, ESLI CHTO-TO NE RABOTAYET

### Problema: "Bot ne publikuyet posty"

**Prover po poryadku:**
1. Zaydi v Render → Logs. Yest li oshibki?
2. Peremennye okruzheniya zapolneny pravilno?
3. Bot dobavlen administratorom kanala?
4. Kanal publichnyy? (username nachinayetsya s @)

### Problema: "Oshibka 429 ot Groq"

**Eto normalno!** Bot avtomaticheski zhdet 60 sekund i povtoryayet. Yesli chasto — umenshi chastotu publikatsiy.

### Problema: "Kartinki ne zagruzhayutsya"

Pollinations.ai inogda peregruzhen. Bot avtomaticheski otpravit post bez kartinki. Cherez vremya kartinki snova budut rabotat.

### Problema: "Render ostanavlivayet bota"

Na besplatnom tarife Render mozhet "zasyipat" neaktivnye servisy. No bot avtomaticheski prosypayetsya po raspisaniyu. Yesli ne prosypayetsya:
1. Zaregistriruysya na `uptimerobot.com` (besplatno)
2. Dobav monitoring s intervalom 5 minut
3. Render budet poluchat pingi i ne zasyipat

---

## CHAST 11. GOTOVO!

Yesli ty doshel do etogo mesta — pozdravlyayu! Tvoy bot rabotayet.

**Chto proiskhodit avtomaticheski:**
- Bot prosypayetsya po raspisaniyu
- Vybirayet sluchaynuyu temu iz 40+ variantov
- Generiruyet unikalnuyu statyu cherez Groq AI
- Sozdayet unikalnuyu kartinku cherez Pollinations
- Publikuyet vse v tvoy kanal
- Zasyipayet do sleduyushchego vremeni

**Tebe ostayetsya tolko:**
- Nablyudat za kanalom
- Inogda dobavlyat novye temy v spisok ARTICLE_TOPICS
- Naslazhdatsya avtonomnym kontentom!

---

Udachi s tvoim AI-kanalom!
