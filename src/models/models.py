# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DECIMAL  # BLOB, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Parameter(Base):
    __tablename__ = 'parameters'

    name = Column(String(20), primary_key=True)
    value = Column(Integer)


class User(Base):
    __tablename__ = 'users'

    chat_id = Column(BigInteger, primary_key=True)
    id = Column(BigInteger, primary_key=True)
    correct_answers = Column(Integer)
    points = Column(Integer)
    user_name = Column(String(250))


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(BigInteger, primary_key=True)
    u_id = Column(Integer)
    q_id = Column(Integer)
    is_on = Column(Boolean)
    game = Column(String(20))
    lang = Column(String(2))
