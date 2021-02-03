from sqlalchemy import create_engine, Table, Column, String, MetaData, Integer, Date, ForeignKey, insert, delete, \
    UniqueConstraint
import csv
import os
import random
import radar
import datetime

engine = create_engine('sqlite:///database/foo.db', echo=True)


# создание таблиц в БД
def create_database():
    metadata = MetaData()
    user = Table('user', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String),
                 Column('surname', String),
                 Column('fathers_name', String),
                 Column('email', String),
                 )
    book = Table('book', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String),
                 Column('author', String),
                 Column('isbn', String)
                 )
    order = Table('order', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('reg_date', Date),
                  Column('user_id', Integer, ForeignKey('user.id'))
                  )
    order_item = Table('order_item', metadata,
                       Column('id', Integer, primary_key=True, autoincrement=True),
                       Column('order_id', Integer, ForeignKey('order.id')),
                       Column('book_id', Integer, ForeignKey('book.id')),
                       Column('shop_id', Integer, ForeignKey('book.id')),
                       Column('book_quantity', Integer)
                       )
    shop = Table('shop', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String),
                 Column('address', String),
                 Column('postcode', Integer)
                 )
    # UniqueConstraint необходим, чтобы избежать дублей (книга,магазин) с разным кол-вом книг
    stock = Table('stock', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('shop_id', Integer, ForeignKey('shop.id')),
                  Column('book_id', Integer, ForeignKey('book.id')),
                  Column('available_qt', Integer),
                  UniqueConstraint('shop_id', 'book_id', name='uix_1')
                  )
    metadata.create_all(engine)


# скрипт для заполнения БД
def fillin_database():
    with engine.connect() as connection:
        metadata = MetaData(bind=engine, reflect=True)
        raw_data_dict = {}
        # обход файлов в папке raw data для создания словаря с "сырыми" данными
        # ключ - имя файла, значения хранятся в списке обработанного csv файла
        for filename in os.listdir('../static'):
            with open(os.path.join('../static', filename), newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                raw_data_dict.update({filename.replace('.csv', ''): list(reader)})
        # очистка таблиц перед заполнением
        for table in metadata.tables:
            stmt = (
                delete(metadata.tables[table]))
            connection.execute(stmt)
        # переменная not_repeated_orders необходима для корректного заполнения таблицы orderItem,
        # в случае ее отсутствия в таблице Order будут "повисшие" заказы, у которых нет связи с таблицей orderItem
        not_repeated_orders = random.sample(range(1, 100), 99)
        for i in range(99):
            # заполнение случайными значениями таблицы user
            # данные берутся из словаря с "сырыми" данными
            stmt = (
                insert(metadata.tables['user']).values(name=random.choice(raw_data_dict.get("names"))[0],
                                                       surname=random.choice(raw_data_dict.get("surnames"))[0],
                                                       fathers_name=random.choice(raw_data_dict.get("fathers_names"))[
                                                           0],
                                                       email=random.choice(raw_data_dict.get("emails"))[0])
            )
            connection.execute(stmt)
            # получение случайной даты
            random_date = radar.random_datetime(
                start=datetime.datetime(year=2000, month=5, day=24),
                stop=datetime.datetime(year=2013, month=5, day=24)
            )
            # заполнение случайными значения таблицы order
            stmt = (
                insert(metadata.tables['order']).values(reg_date=random_date,
                                                        user_id=random.randint(1, 99))
            )
            connection.execute(stmt)
            # заполнение случайными значениями таблицы book
            # данные берутся из словаря с "сырыми" данными
            stmt = (
                insert(metadata.tables['book']).values(name=random.choice(raw_data_dict.get("book_names"))[0],
                                                       author=random.choice(raw_data_dict.get("authors"))[0],
                                                       isbn=random.choice(raw_data_dict.get("isbns"))[0])
            )
            connection.execute(stmt)
            # заполнение случайными значениями таблицы shop
            # данные берутся из словаря с "сырыми" данными
            stmt = (
                insert(metadata.tables['shop']).values(name=random.choice(raw_data_dict.get("shop_names"))[0],
                                                       address=random.choice(raw_data_dict.get("addresses"))[0],
                                                       postcode=random.randint(100000, 999999))
            )
            connection.execute(stmt)
            # заполнение случайными значениями таблицы order_item
            # таблица заполняется двумя insert для реализации логики "несколько книг в одном заказе"
            stmt = (
                insert(metadata.tables['order_item']).values(
                    order_id=not_repeated_orders[i],
                    book_id=random.randint(1, 99),
                    shop_id=random.randint(1, 99),
                    book_quantity=random.randint(1, 5))
            )
            connection.execute(stmt)
            stmt = (
                insert(metadata.tables['order_item']).values(
                    order_id=not_repeated_orders[i],
                    book_id=random.randint(1, 99),
                    shop_id=random.randint(1, 99),
                    book_quantity=random.randint(1, 5))
            )
            connection.execute(stmt)
            # заполнение случайными значениями таблицы stock
            stmt = (
                insert(metadata.tables['stock']).values(
                    book_id=random.randint(1, 99),
                    shop_id=random.randint(1, 99),
                    available_qt=random.randint(1, 40))
            )
            try:
                connection.execute(stmt)
            except Exception:
                pass


if __name__ == '__main__':
    create_database()
    fillin_database()
