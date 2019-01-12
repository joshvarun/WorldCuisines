from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
