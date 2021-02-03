from aiohttp import web
from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
from datetime import datetime

engine = create_engine('sqlite:///database/foo.db', echo=True)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    fathers_name = Column(String)
    email = Column(String)


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    author = Column(String)
    isbn = Column(String)


class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    postcode = Column(Integer)


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    reg_date = Column(Date)
    user_id = Column(Integer, ForeignKey("user.id"))


class OrderItem(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    book_id = Column(Integer, ForeignKey("book.id"))
    shop_id = Column(Integer, ForeignKey("shop.id"))
    book_quantity = Column(Integer)


class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shop.id"))
    book_id = Column(Integer, ForeignKey("book.id"))
    available_qt = Column(Integer)


async def userinfo(request):
    try:
        value = request.rel_url.query.get("user_id", "")
        user = session.query(User).filter(User.id == value).one()
        return web.Response(text=json.dumps({"user_id": value, "name": user.name, "surname": user.surname,
                                             "fathers_name": user.fathers_name, "email": user.email},
                                            ensure_ascii=False))
    except Exception as e:
        return web.Response(text=f"{e}")


async def get_user_orders(request):
    try:
        value = request.rel_url.query.get("user_id", "")
        list_of_orders = []
        for order_id, reg_date, book_name, book_quantity, shop_name in \
                session.query(Order.id, Order.reg_date, Book.name, OrderItem.book_quantity, Shop.name). \
                        filter(Order.id == OrderItem.order_id). \
                        filter(Book.id == OrderItem.book_id). \
                        filter(Shop.id == OrderItem.shop_id). \
                        filter(Order.user_id == value):
            list_of_orders.append(json.dumps({"order_id": order_id, "reg_date": reg_date.strftime('%Y-%m-%d'),
                                              "book_name": book_name, "book_quantity": book_quantity,
                                              "shop_name": shop_name}, ensure_ascii=False))
        return web.Response(text=str(list_of_orders))
    except Exception as e:
        return web.Response(text=f"{e}")


async def new_order(request):
    try:
        data = await request.post()
        order = Order(reg_date=datetime.today(), user_id=data.get('user_id'))
        session.add(order)
        session.flush()
        for book_id, book_qt in json.loads(data.get('book_quantity')).items():
            session.add(
                OrderItem(order_id=order.id, book_id=book_id, shop_id=data.get('shop_id'), book_quantity=book_qt))
            session.flush()
        session.commit()
        return web.Response(text="Order added")
    except Exception as e:
        session.rollback()
        return web.Response(text="Order not added")


async def get_shop_assortment(request):
    try:
        shop_id = request.rel_url.query.get("shop_id", "")
        get_shop_assortment = []
        for shop_name, book_name, available_qt in \
                session.query(Shop.name, Book.name, Stock.available_qt). \
                        filter(Stock.shop_id == Shop.id). \
                        filter(Stock.book_id == Book.id). \
                        filter(Stock.shop_id == shop_id):
            get_shop_assortment.append(json.dumps({"shop_name": shop_name, "book_name": book_name,
                                                   "available_quantity": available_qt}, ensure_ascii=False))
        return web.Response(text=str(get_shop_assortment))
    except Exception as e:
        return web.Response(text=f"{e}")


app = web.Application()
app.router.add_get('/userinfo', userinfo)
app.router.add_get('/userorders', get_user_orders)
app.router.add_post('/neworder', new_order)
app.router.add_get('/shopassortment', get_shop_assortment)
web.run_app(app)
