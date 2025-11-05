import asyncio
import asyncpg
from aiohttp import web
from .models import Base
from .database import get_engine, get_session_maker
from .views import create_ad, get_ad, update_ad, delete_ad

async def wait_for_db():
    while True:
        try:
            conn = await asyncpg.connect(
                user="user",
                password="password",
                host="db",
                port=5432,
                database="ads"
            )
            await conn.close()
            print("✅ PostgreSQL is ready!")
            break
        except Exception as e:
            print(f"⏳ Waiting for PostgreSQL... ({e})")
            await asyncio.sleep(1)

async def init_db(app):
    await wait_for_db()
    
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    app["engine"] = engine
    app["session_maker"] = get_session_maker(engine)

async def cleanup_db(app):
    engine = app.get("engine")
    if engine:
        await engine.dispose()

def create_app():
    app = web.Application()
    
    app.on_startup.append(init_db)
    app.on_cleanup.append(cleanup_db)
    
    app.router.add_post('/ads', create_ad)
    app.router.add_get('/ads/{ad_id}', get_ad)
    app.router.add_patch('/ads/{ad_id}', update_ad)
    app.router.add_delete('/ads/{ad_id}', delete_ad)
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080)