import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from database import Base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship, backref


class Areas(Base):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description

    def __repr__(self):
        return f'<Area {self.title!r}>'

class Dating(Base):
    __tablename__ = 'dating'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('dating.id'))
    title = Column(String, nullable=False, unique=True)
    children = relationship('Dating', backref=backref('parent', remote_side=[id]))

    def __init__(self, parent_id=None, title=None):
        self.parent_id = parent_id
        self.title = title

    def __repr__(self):
        return self.title