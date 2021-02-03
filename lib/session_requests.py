from datetime import datetime
from sqlalchemy.future import select
import json

from models.schemas import User, Order, Book, Shop, OrderItem, Stock


# запрос данных пользователя в БД по user_id
# результат из БД предполагает только одну строчку
# результаты запроса возвращаются в формате json
async def get_user_by_id(user_id, session):
    try:
        stmt = select(User).filter(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().one()
        return json.dumps({"user_id": user_id, "name": user.name, "surname": user.surname,
                           "fathers_name": user.fathers_name, "email": user.email},
                          ensure_ascii=False)
    except Exception as e:
        return "Произошла ошибка" + str(e)


# запрос истории заказов пользователя по user_id
# функции filter выполняют join по внешнему ключу
# итоговый результат в формате list, содержащий json (id заказа, дата заказа, имя книги, кол-во книг, название магазина)
async def get_user_history_orders(user_id, session):
    try:
        response_from_db = []
        stmt = select(Order.id, Order.reg_date, Book.name, OrderItem.book_quantity, Shop.name).\
            filter(Order.id == OrderItem.order_id).\
            filter(Book.id == OrderItem.book_id). \
            filter(Shop.id == OrderItem.shop_id). \
            filter(Order.user_id == user_id)
        result = await session.execute(stmt)
        orders = result.fetchall()
        for order in orders:
            response_from_db.append(dict(order._mapping))
        return str(response_from_db)
    except Exception as e:
        return "Произошла ошибка" + str(e)


# добавление нового заказа
# 1. добавляется заказ в таблицу Order
# 2. flush добавления заказа для чтения order_id (который инкрементируется автоматически)
# 3. обход в цикле всех заказанных книг и их кол-во с последующим добавлением в таблицу OrderItem
# 4. коммит сессии происходит в вызывающем методе
def add_new_order(post, session):
    try:
        order = Order(reg_date=datetime.today(), user_id=post.get('user_id'))
        session.add(order)
        session.flush()
        for book_id, book_qt in json.loads(post.get('book_quantity')).items():
            session.add(
                OrderItem(order_id=order.id, book_id=book_id, shop_id=post.get('shop_id'), book_quantity=book_qt))
            session.flush()
    except Exception as e:
        return "Произошла ошибка" + str(e)


# получение ассортимента магазина по его id
# итоговый результат в формате list, содержащий json (id заказа, дата заказа, имя книги, кол-во книг, название магазина)
# если по id магазина ничего не было найдено, возвращается пустая строка
def get_assortment_by_shop_id(shop_id, session):
    response_from_db = []
    for shop_name, book_name, available_qt in session.query(Shop.name, Book.name, Stock.available_qt). \
            filter(Stock.shop_id == Shop.id). \
            filter(Stock.book_id == Book.id). \
            filter(Stock.shop_id == shop_id):
        response_from_db.append(json.dumps({"shop_name": shop_name, "book_name": book_name,
                                            "available_quantity": available_qt}, ensure_ascii=False))
        return str(response_from_db)
