# Setup Database for Udacity Full Stack Web Development Nanodegree
# Item Catalog
# Written: January 12, 2019 by Varun Joshi

import os
import sys
from sqlalchemy import Column, ForeignKey, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    profileImage = Column(String(250))


class Cuisine(Base):
    __tablename__ = 'cuisine'

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


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    imageUrl = Column(String(250), nullable=False)
    cuisine_id = Column(Integer, ForeignKey('cuisine.id'))
    cuisine = relationship(Cuisine)
    created_by = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cuisine_id': self.cuisine_id,
            'created_by': self.created_by,
            'imageUrl': self.imageUrl,
        }


engine = create_engine('sqlite:///worldcuisines.db')
Base.metadata.create_all(engine)
