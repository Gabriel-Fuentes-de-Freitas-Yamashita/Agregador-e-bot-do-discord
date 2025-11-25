import os
import feedparser
import asyncio
import httpx
from bs4 import BeautifulSoup 
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Feed, NewsItem

# ---------------------------------------------------------
raw_webhooks = os.getenv("DISCORD_WEBHOOK_URL", "")
WEBHOOK_LIST = [url.strip() for url in raw_webhooks.split(",") if url.strip()]
# ---------------------------------------------------------

# 🎯 SNIPER MODE: Lista Definitiva de Hardware
KEYWORDS = [
    # --- PLACAS DE VÍDEO (NVIDIA) ---
    "RTX 3060", "RTX 4060", "RTX 4060 Ti", 
    "RTX 4070", "RTX 4070 Ti", "RTX 4070 Super",
    "RTX 4080", "RTX 4090", "RTX 50", # Já preparando para o futuro
    
    # --- PLACAS DE VÍDEO (AMD) ---
    "RX 6600", "RX 6650", "RX 6750", 
    "RX 7600", "RX 7700", "RX 7800", "RX 7900",

    # --- PROCESSADORES ---
    "Ryzen 5 5600", "Ryzen 7 5700X", "Ryzen 7 5800X3D", 
    "Ryzen 5 7600", "Ryzen 7 7800X3D", "Ryzen 9",
    "Core i5-12", "Core i5-13", "Core i5-14", # Gerações 12, 13 e 14
    "Core i7-12", "Core i7-13", "Core i7-14",

    # --- CONSOLES & ACESSÓRIOS ---
    "Playstation 5", "PS5", "Xbox Series X", "Nintendo Switch",
    "Dualsense", "Controle Xbox",

    # --- ARMAZENAMENTO & MEMÓRIA ---
    "SSD 1TB", "SSD 2TB", "SSD 4TB",
    "NVMe 1TB", "NVMe 2TB",
    "DDR4 16GB", "DDR5 16GB", "DDR5 32GB",

    # --- MONITORES & PERIFÉRICOS ---
    "Monitor 144hz", "Monitor 165hz", "Monitor 240hz", 
    "Monitor OLED", "Monitor QLED", "Monitor IPS",
    "Logitech G", "Razer", "HyperX", # Marcas boas costumam ter promos reais

]

def parse_feed_sync(url: str):
    return feedparser.parse(url)

def extrair_imagem(entry):
    if hasattr(entry, 'media_content'):
        return entry.media_content[0]['url']
    if hasattr(entry, 'links'):
        for link in entry.links:
            if link.type.startswith('image/'):
                return link.href
    if hasattr(entry, 'summary'):
        soup = BeautifulSoup(entry.summary, 'lxml')
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
    return None

async def send_discord_alert(title: str, link: str, image_url: str = None):
    # Se a lista estiver vazia, não faz nada
    if not WEBHOOK_LIST:
        return

    embed = {
        "title": "🔥 Alerta Sniper!",
        "description": f"**{title}**",
        "url": link,
        "color": 10181046,
        "footer": {"text": "Monitorando Preços 24/7"},
    }
    if image_url:
        embed["image"] = {"url": image_url}

    payload = {"username": "Hardware Sniper", "embeds": [embed]}

    async with httpx.AsyncClient() as client:
        # --- AQUI ESTÁ A MÁGICA: LOOP PARA TODOS OS SERVIDORES ---
        for webhook_url in WEBHOOK_LIST:
            try:
                # Envia para cada servidor da lista
                await client.post(webhook_url, json=payload)
                print(f"🔔 Enviado para um servidor: {title[:20]}...")
            except Exception as e:
                print(f"❌ Erro ao enviar para um dos Webhooks: {e}")

async def update_feeds(db: AsyncSession):
    print("🔄 Verificando Feeds...")
    result = await db.execute(select(Feed))
    feeds = result.scalars().all()

    for feed in feeds:
        loop = asyncio.get_event_loop()
        try:
            feed_data = await loop.run_in_executor(None, parse_feed_sync, feed.url)
            for entry in feed_data.entries:
                exists = await db.execute(select(NewsItem).where(NewsItem.link == entry.link))
                if not exists.scalars().first():
                    new_news = NewsItem(title=entry.title[:250], link=entry.link, feed_id=feed.id)
                    db.add(new_news)
                    
                    # Sniper Check
                    if any(k.lower() in entry.title.lower() for k in KEYWORDS):
                        img = extrair_imagem(entry)
                        await send_discord_alert(entry.title, entry.link, img)
        except Exception as e:
            print(f"Erro no feed {feed.url}: {e}")

    await db.commit()