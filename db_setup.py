import sys
import os
from sqlalchemy import ForeignKey, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()


# create Users table
class Users(Base):
    __tablename__ = 'Users'
    name = Column(String, nullable=False)
    id = Column(String, primary_key=True)
    # add serialize property for using in jsonify

    @property
    def serialize(self):
        return {
            'user_name': self.name,
            'user_id': self.id
        }


# create Posts table
class Posts(Base):
    __tablename__ = 'Posts'
    date = Column(String, nullable=False)
    id = Column(String, primary_key=True)
    text = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship(Users)
    # add serialize property for using in jsonify

    @property
    def serialize(self):
        return {
            'post_date': self.date,
            'post_text': self.text
        }


engine = create_engine('sqlite:///Ofaly.db')
Base.metadata.create_all(engine)
