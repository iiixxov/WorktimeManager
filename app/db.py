import datetime

from sqlalchemy import create_engine, MetaData, Column, INTEGER, VARCHAR,  func, ForeignKey, DATE, FLOAT, DATETIME
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


Base = declarative_base(metadata=MetaData())
engine = create_engine(f"sqlite:///base.db")
Session = sessionmaker(bind=engine)


class UserModel(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(250), nullable=False)
    utoken = Column(VARCHAR(250), nullable=False, unique=True)


class TGUserModel(Base):
    __tablename__ = 'tg_user'

    id = Column(INTEGER, primary_key=True)
    tg_id = Column(INTEGER, nullable=False)
    user_id = Column(INTEGER, ForeignKey('user.id', ondelete='CASCADE'))

    user = relationship(UserModel)


class TGAdminModel(Base):
    __tablename__ = 'tg_admin'

    id = Column(INTEGER, primary_key=True)
    chat_id = Column(INTEGER, nullable=False)


class UserTimeInModel(Base):
    __tablename__ = 'user_time_in'

    id: Column[INTEGER] = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    time = Column(DATETIME, default=func.current_timestamp())

    user = relationship(UserModel, lazy="joined")

    @property
    def localtime(self):
        return (self.time + datetime.timedelta(hours=7)).time()


class UserTimeOutModel(Base):
    __tablename__ = 'user_time_out'

    id: Column[INTEGER] = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    time = Column(DATETIME, default=func.current_timestamp())

    user = relationship(UserModel, lazy="joined")

    @property
    def localtime(self):
        return (self.time + datetime.timedelta(hours=7)).time()


class WorkDayModel(Base):
    __tablename__ = 'work_day'

    id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    day = Column(DATE, default=func.current_date())
    time = Column(FLOAT, nullable=False)

    user = relationship(UserModel)
