import json
import asyncio
import os
import redis.asyncio as redis
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, Base, get_db, AsyncSessionLocal
from models import Feed, NewsItem
from services import update_feeds

app = FastAPI(title="Hardware Sniper Bot")

# --- SEGURANÇA ---
# Define que a senha deve vir no Header com o nome "x-api-key"
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verificar_chave_seguranca(api_key_header: str = Security(api_key_header)):
    # Pega a senha real das variáveis de ambiente (ou usa uma padrão fraca pra teste local)
    SENHA_MESTRA = os.getenv("API_SECRET", "minhasenhalocal123")
    
    if api_key_header == SENHA_MESTRA:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🔒 Acesso Negado: Você precisa da API Key correta no header 'x-api-key'"
        )

# Configuração Redis e Loop Automático (Iguais ao anterior)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(redis_url, decode_responses=True)
except:
    redis_client = None 

async def monitorar_automaticamente():
    # ... (código igual ao anterior) ...
    print("⏰ Monitoramento Automático INICIADO!")
    while True:
        try:
            async with AsyncSessionLocal() as session:
                await update_feeds(session)
        except Exception as e:
            print(f"❌ Erro no loop: {e}")
        await asyncio.sleep(300)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(monitorar_automaticamente())


# --- ROTAS PROTEGIDAS (PRECISAM DE SENHA) ---

@app.post("/feeds/", dependencies=[Depends(verificar_chave_seguranca)])
async def adicionar_feed(url: str, name: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    try:
        new_feed = Feed(url=url, name=name)
        db.add(new_feed)
        await db.commit()
        background_tasks.add_task(update_feeds, db)
        return {"message": "Feed adicionado!", "feed": name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/force-update/", dependencies=[Depends(verificar_chave_seguranca)])
async def forcar_atualizacao(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    if redis_client:
        try:
            await redis_client.delete("latest_news")
        except:
            pass
    background_tasks.add_task(update_feeds, db)
    return {"message": "Atualização forçada!"}


# --- ROTA PÚBLICA (QUALQUER UM PODE LER) ---
# Deixamos público para recrutadores verem que funciona sem precisar de senha
@app.get("/news/")
async def ler_noticias(busca: str = None, db: AsyncSession = Depends(get_db)):
    # ... (código igual ao anterior) ...
    cache_key = f"news_{busca}" if busca else "news_geral"
    
    if redis_client:
        try:
            cached_news = await redis_client.get(cache_key)
            if cached_news:
                return {"source": "redis", "filter": busca, "data": json.loads(cached_news)}
        except:
            pass 

    query = select(NewsItem).order_by(NewsItem.published_at.desc()).limit(20)
    if busca:
        query = query.where(NewsItem.title.contains(busca))

    result = await db.execute(query)
    news = result.scalars().all()
    news_data = [{"id": n.id, "title": n.title, "link": n.link} for n in news]

    if redis_client and news_data:
        try:
            await redis_client.set(cache_key, json.dumps(news_data), ex=60)
        except:
            pass

    return {"source": "database", "filter": busca, "data": news_data}