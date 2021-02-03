from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lib import session_requests
import logging

engine = create_engine('sqlite:///database/foo.db', echo=True)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)


# запрос информации о пользователе
# чтение значения из GET запроса по ключу user_id -> отправка на запрос в бд
async def get_user_info(request):
    try:
        session = Session()
        user_id = request.rel_url.query.get("user_id", "")
        user_info = session_requests.get_user_by_id(user_id, session)
        return web.Response(text=user_info)
    except Exception as e:
        return web.Response(text=f"{e}")
    finally:
        session.close()


# запрос истории заказов по ключу
# чтение значения из GET запроса по ключу user_id -> отправка на запрос в бд
async def get_user_orders(request):
    try:
        session = Session()
        user_id = request.rel_url.query.get("user_id", "")
        user_history_orders = session_requests.get_user_history_orders(user_id, session)
        return web.Response(text=user_history_orders)
    except Exception as e:
        return web.Response(text=f"{e}")
    finally:
        session.close()


# добавление нового заказа
# чтение значения из POST запроса по ключу user_id -> отправка на запрос в бд
async def add_new_order(request):
    try:
        session = Session()
        post = await request.post()
        session_requests.add_new_order(post, session)
        session.commit()
        return web.Response(text="Order added")
    except Exception:
        session.rollback()
        return web.Response(text="Order not added")
    finally:
        session.close()


# получение ассортимента определенного магазина
# чтение значения из GET запроса по ключу user_id -> отправка на запрос в бд
async def get_shop_assortment(request):
    try:
        session = Session()
        shop_id = request.rel_url.query.get("shop_id", "")
        logger.info("GET reguest shopassortment with shop_id %s" % shop_id)
        shop_assortment = session_requests.get_assortment_by_shop_id(shop_id, session)
        logger.info("Shop assortment returned")
        return web.Response(text=shop_assortment)
    except Exception as e:
        logger.info("exception raised getting shop assortment. details: %s" % e)
        return web.Response(text=f"{e}")
    finally:
        session.close()


if __name__ == '__main__':
    # инициализация логгера
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logs/log.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("Program started")
    # добавление обработчиков GET и POST запросов
    app = web.Application()
    app.router.add_get('/userinfo', get_user_info)
    app.router.add_get('/userorders', get_user_orders)
    app.router.add_post('/neworder', add_new_order)
    app.router.add_get('/shopassortment', get_shop_assortment)
    web.run_app(app)
