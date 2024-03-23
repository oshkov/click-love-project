from sqlalchemy import Column, Integer, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class FormModel(Base):
    __tablename__ = 'forms'

    creation_date = Column(Text)
    id = Column(Text, primary_key=True)
    username = Column(Text)
    status = Column(Text)
    name = Column(Text)
    gender = Column(Text)
    preferences = Column(Text)
    city = Column(Text)
    age = Column(Integer)
    vk_url = Column(Text)
    target = Column(ARRAY(Text))
    about = Column(Text)
    photos = Column(ARRAY(Text))
    warns = Column(Integer)


class UserModel(Base):
    __tablename__ = 'users'

    enter = Column(Text)
    id = Column(Text, primary_key=True)
    username = Column(Text)
    name = Column(Text)
    lastname = Column(Text)
    last_action = Column(Text)
    ban_status = Column(Text)
    sub_status = Column(Text)
    sub_end_date = Column(Text)
    referrals = Column(Integer)
    invited_by = Column(Text)
    agreement = Column(Integer)
    language = Column(Text)
    admin = Column(Integer)


class ActionModel(Base):
    __tablename__ = 'actions'

    creation_date = Column(Text)
    id_creator = Column(Text, primary_key=True)
    id_receiver = Column(Text)
    status = Column(Text)
    message = Column(Text)