# Setup Database for Udacity Full Stack Web Development Nanodegree
# Item Catalog
# Written: January 12, 2019 by Varun Joshi

import os
import sys
from sqlalchemy import Column, ForeignKey, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    profileImage = Column(String(250))


class Category(base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    imageUrl = Column(String(250), nullable=False)
    created_by = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'imageUrl': self.imageUrl,
        }


class Item(base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    imageUrl = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    created_by = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'created_by': self.created_by,
            'imageUrl': self.imageUrl,
        }


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
