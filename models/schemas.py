from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

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

# дополнительная таблица, связывающая Book и Shop, отражает доступное кол-во книг в магазине
class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shop.id"))
    book_id = Column(Integer, ForeignKey("book.id"))
    available_qt = Column(Integer)