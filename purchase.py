from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func

DB_FILE = "farm_produce_delivery.db"

Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    commercial = Column(String)
    goods = relationship('Goods', back_populates='client')


class Goods(Base):
    __tablename__ = 'goods'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    category = Column(String)
    type = Column(String)
    weight = Column(Float)
    client = relationship('Client', back_populates='goods')


def calculate_delivery_fee(total_weight, distance):
    delivery_fee = total_weight * 150
    if distance >= 0 and distance <= 10:
        return delivery_fee + 50
    else:
        return delivery_fee + 150


def calculate_item_price(category, item_type, weight):
    price_per_kg = 0
    if category == "MEAT":
        if item_type == "chicken":
            price_per_kg = 200
        elif item_type == "beef":
            price_per_kg = 300
        elif item_type == "mutton":
            price_per_kg = 250
        elif item_type == "pork":
            price_per_kg = 280
        elif item_type == "sardines":
            price_per_kg = 150
    elif category == "SEA FOOD":
        if item_type == "tilapia":
            price_per_kg = 180
        elif item_type == "omena":
            price_per_kg = 120
        elif item_type == "snapper":
            price_per_kg = 220
    elif category == "DAIRY":
        if item_type == "milk":
            price_per_kg = 80
        elif item_type == "cream":
            price_per_kg = 150
        elif item_type == "cheese":
            price_per_kg = 200
        elif item_type == "ghee":
            price_per_kg = 250
    elif category == "OTHER":
        if item_type == "rice":
            price_per_kg = 90
        elif item_type == "maize flour":
            price_per_kg = 50
        elif item_type == "wheat flour":
            price_per_kg = 70
        elif item_type == "pasta":
            price_per_kg = 120
    elif category == "VEGES":
        if item_type == "kales":
            price_per_kg = 40
        elif item_type == "cabbages":
            price_per_kg = 60
        elif item_type == "lettuce":
            price_per_kg = 70
        elif item_type == "spinach":
            price_per_kg = 50
    else:
        print("Invalid category")

    return price_per_kg * weight


def filter_database_by_most_sold_goods(session):
    most_purchased_goods = session.query(Goods).\
        group_by(Goods.category, Goods.type).\
        order_by(func.count(Goods.id).desc()).\
        first()

    if most_purchased_goods:
        print("Most Sold Goods:")
        print("Category:", most_purchased_goods.category)
        print("Type:", most_purchased_goods.type)
        print("Number of Sales:", session.query(Goods).filter(Goods.category == most_purchased_goods.category,
                                                              Goods.type == most_purchased_goods.type).count())
    else:
        print("No goods found.")


def update_price_per_kg(session):
    category = input("Enter the category of goods to update the price per kg: ")
    item_type = input("Enter the type of goods to update the price per kg: ")
    new_price_per_kg = float(input("Enter the new price per kg: "))

    goods = session.query(Goods).filter(Goods.category == category.upper(), Goods.type == item_type.lower()).first()

    if goods:
        goods_price = calculate_item_price(category.upper(), item_type.lower(), goods.weight)
        goods_price_updated = new_price_per_kg * goods.weight

        print("Old Price:", goods_price)
        print("New Price:", goods_price_updated)

        goods_price_difference = goods_price_updated - goods_price
        print("Price Difference:", goods_price_difference)

        goods.price_per_kg = new_price_per_kg
        session.commit()
    else:
        print("Goods not found.")


def main():
    engine = create_engine(f'sqlite:///{DB_FILE}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user_name = input("Enter your name: ")

    client = session.query(Client).filter(Client.name == user_name).first()
    if client is None:
        user_type = input("Are you a commercial user? (yes/no): ")
        if user_type.lower() == "yes":
            commercial = "yes"
            additional_charge = 50
            delivery_fee = 200
        elif user_type.lower() == "no":
            commercial = "no"
            additional_charge = 0
            delivery_fee = 150
        elif user_type.lower() == "0":
            commercial = "no"
            additional_charge = 0
            delivery_fee = 0
        else:
            print("Invalid user type")
            return

        client = Client(name=user_name, commercial=commercial)
        session.add(client)
        session.commit()

    total_amount = 0

    while True:
        category = input("Enter the category of goods (MEAT/SEA FOOD/DAIRY/OTHER/VEGES): ")
        if category.lower() not in ["meat", "sea food", "dairy", "other", "veges"]:
            print("Invalid category")
            continue

        item_type = input("Enter the type of goods: ")
        weight = float(input("Enter the weight of goods in kg: "))

        item_price = calculate_item_price(category.upper(), item_type.lower(), weight)
        total_amount += item_price

        goods = Goods(client_id=client.id, category=category.upper(), type=item_type.lower(), weight=weight)
        session.add(goods)
        session.commit()

        continue_shopping = input("Do you want to continue shopping? (yes/no): ")
        if continue_shopping.lower() == "no":
            break

    total_delivery_fee = calculate_delivery_fee(total_amount, delivery_fee)

    total_amount = total_delivery_fee + additional_charge

    print("------- Invoice -------")
    print("Client Name:", user_name)
    print("Total Goods Amount:", total_amount)
    # print("Total Delivery Fee:", total_delivery_fee)
   

    user_option = input("Enter 'filter' to filter the database or 'update' to update the price per kg: ")

    if user_option.lower() == "filter":
        filter_database_by_most_sold_goods(session)
    elif user_option.lower() == "update":
        update_price_per_kg(session)
    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
    