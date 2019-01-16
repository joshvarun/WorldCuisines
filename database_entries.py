from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Thai Cuisine
cuisine1 = Category(name="Thai")

session.add(cuisine1)
session.commit()

item1 = Item(name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                     imageUrl="$7.50", course="Entree", restaurant=restaurant1)

session.add(menuItem2)
session.commit()
