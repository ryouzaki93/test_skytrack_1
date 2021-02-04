from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from lib import session_requests
import logging
import inspect

engine = create_async_engine('sqlite:///database/foo.db', echo=True)
logger = logging.getLogger('main.py')


# запрос информации о пользователе
# чтение значения из GET запроса по ключу user_id -> отправка на запрос в бд
async def get_user_info(request):
    try:
        async with AsyncSession(engine) as session:
            user_id = request.rel_url.query.get("user_id", "")
            logger.info(inspect.stack()[0][3] + " started, user_id: %s", user_id)
            user_info = await session_requests.get_user_by_id(user_id, session)
            logger.info("user info from DB received: %s", user_info)
            return web.Response(text=user_info)
    except Exception as e:
        logger.warning(inspect.stack()[0][3] + "raised exception ", e)
        return web.Response(text=f"{e}")
    finally:
        await session.close()


# запрос истории заказов по ключу
# чтение значения из GET запроса по ключу user_id -> отправка на запрос в бд
async def get_user_orders(request):
    try:
        async with AsyncSession(engine) as session:
            user_id = request.rel_url.query.get("user_id", "")
            logger.info(inspect.stack()[0][3] + " started, user_id: %s", user_id)
            user_history_orders = await session_requests.get_user_history_orders(user_id, session)
            logger.info("user orders from DB received: %s", user_history_orders)
        return web.Response(text=user_history_orders)
    except Exception as e:
        logger.warning(inspect.stack()[0][3] + "raised exception ", e)
        return web.Response(text=f"{e}")
    finally:
        await session.close()


# добавление нового заказа
async def add_new_order(request):
    try:
        post = await request.post()
        logger.info(inspect.stack()[0][3] + " started, POST message: %s", post)
        async with AsyncSession(engine) as session:
            await session_requests.add_new_order(post, session)
            await session.commit()
        return web.Response(text="Order added")
    except Exception as e:
        await session.rollback()
        logger.warning(inspect.stack()[0][3] + "raised exception ", e)
        return web.Response(text="Order not added. Exception"+f"{e}")
    finally:
        await session.close()


# получение ассортимента определенного магазина
# чтение значения из GET запроса по ключу user_id -> отправка на запрос в бд
async def get_shop_assortment(request):
    try:
        async with AsyncSession(engine) as session:
            shop_id = request.rel_url.query.get("shop_id", "")
            logger.info(inspect.stack()[0][3] + " started, shop_id: %s", shop_id)
            shop_assortment = await session_requests.get_assortment_by_shop_id(shop_id, session)
            logger.info("shop assortment from DB received: %s", shop_assortment)
        return web.Response(text=shop_assortment)
    except Exception as e:
        logger.warning(inspect.stack()[0][3] + "raised exception ", e)
        return web.Response(text=f"{e}")
    finally:
        await session.close()


if __name__ == '__main__':
    logging.basicConfig(filename="logs/logging.log", level=logging.INFO, filemode="w", format='%(name)s - %(levelname)s '
                                                                                           '- %(message)s')
    # добавление обработчиков GET и POST запросов
    app = web.Application()
    app.router.add_get('/userinfo', get_user_info)
    app.router.add_get('/userorders', get_user_orders)
    app.router.add_post('/neworder', add_new_order)
    app.router.add_get('/shopassortment', get_shop_assortment)
    web.run_app(app)
