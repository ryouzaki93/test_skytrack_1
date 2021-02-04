from datetime import datetime
from sqlalchemy.future import select
import json
import logging
import traceback

from models.schemas import User, Order, Book, Shop, OrderItem, Stock

logger = logging.getLogger('sqlrequests.py')


def exception_decorator(function):
    async def wrapper(*args):
        try:
            result = await function(*args)
            return result
        except Exception as e:
            logger.error(traceback.format_exc())
            return "Raised exception" + str(e)
    return wrapper


# запрос данных пользователя в БД по user_id
# результат из БД предполагает только одну строчку
# результаты запроса возвращаются в формате json
@exception_decorator
async def get_user_by_id(user_id, session):
    stmt = select(User).filter(User.id == user_id)
    result = await session.stream(stmt)
    user = await result.scalars().one()
    logger.info("selecting user_info by user_id %s finished", user.id)
    return {'user_id': user_id, 'name': user.name, 'surname': user.surname, 'fathers_name': user.fathers_name,
            'email': user.email}


# запрос истории заказов пользователя по user_id
# функции filter выполняют join по внешнему ключу
# итоговый результат в формате list, содержащий json (id заказа, дата заказа, имя книги, кол-во книг, название магазина)
@exception_decorator
async def get_user_history_orders(user_id, session):
    response_from_db = []
    stmt = select(Order.id, Order.reg_date, Book.name, OrderItem.book_quantity, Shop.name). \
        filter(Order.id == OrderItem.order_id). \
        filter(Book.id == OrderItem.book_id). \
        filter(Shop.id == OrderItem.shop_id). \
        filter(Order.user_id == user_id)
    result = await session.stream(stmt)
    logger.info("selecting user_orders_history by user_id %s finished", user_id)
    async for order in result:
        response_from_db.append({"order_id": order[0], "reg_date": order[1].strftime('%Y-%m-%d'), "book_name": order[2],
                                 "book_quantity": order[3], "shop_name": order[4]})
    return response_from_db


# добавление нового заказа
# 1. добавляется заказ в таблицу Order
# 2. flush добавления заказа для чтения order_id (который инкрементируется автоматически)
# 3. обход в цикле всех заказанных книг и их кол-во с последующим добавлением в таблицу OrderItem
# 4. коммит сессии происходит в вызывающем методе
@exception_decorator
async def add_new_order(post, session):
    order = Order(reg_date=datetime.today(), user_id=post.get('user_id'))
    async with session.begin():
        session.add(order)
        await session.flush()
        logger.info("insert flushed order, order_id is %s", order.id)
        for book_id, book_qt in json.loads(post.get('book_quantity')).items():
            order_item = OrderItem(order_id=order.id, book_id=book_id, shop_id=post.get('shop_id'),
                                   book_quantity=book_qt)
            session.add(order_item)
            await session.flush()
            logger.info("insert flushed orderItem, orderItem_id is %s", order_item.id)


# получение ассортимента магазина по его id
# итоговый результат в формате list, содержащий json (id заказа, дата заказа, имя книги, кол-во книг, название магазина)
# если по id магазина ничего не было найдено, возвращается пустая строка
@exception_decorator
async def get_assortment_by_shop_id(shop_id, session):
    response_from_db = []
    stmt = select(Shop.name, Book.name, Stock.available_qt). \
        filter(Stock.shop_id == Shop.id). \
        filter(Stock.book_id == Book.id). \
        filter(Stock.shop_id == shop_id)
    result = await session.stream(stmt)
    logger.info("selecting shop_assortment by shop_id %s finished", shop_id)
    async for position in result:
        response_from_db.append({"shop_name": position[0], "book_name": position[1],
                                 "available_qt": position[2]})
    return response_from_db
