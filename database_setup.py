import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    

class Catalog(Base):
    __tablename__ = 'catalog'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
                     

    @property
    def serialize(self):
        return{
            'name' : self.name,
            'id' : self.id,
            }

class Items(Base):
    __tablename__ = 'items'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    

    @property
    def serialize(self):
        return{
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            }




engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)

                       
