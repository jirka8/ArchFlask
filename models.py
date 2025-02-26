import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Table
from database import Base
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import *

items_categories = Table(
    'items_categories',
    Base.metadata,
    Column('item_id', ForeignKey('items.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True)
)

items_dating = Table(
    'items_dating',
    Base.metadata,
    Column('item_id', ForeignKey('items.id'), primary_key=True),
    Column('dating_id', ForeignKey('dating.id'), primary_key=True),
)

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
    parent_id = Column(Integer, ForeignKey('dating.id'), nullable=True)
    title = Column(String, nullable=False, unique=False)
    children = relationship('Dating', backref=backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    items = relationship('Items', secondary=items_dating, back_populates='dating')

    def __init__(self, parent_id=None, title=None):
        self.parent_id = parent_id
        self.title = title

    def __repr__(self):
        return self.title

    # format choices for parent_id select box
    def select_choices(self, non_list = 0):
        choices = [(self.id, self.title)]
        for child in self.children:
            if child.id != int(non_list):
                choices.extend([(child.id, f' -- {child.title}')])
        return choices

class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    title = Column(String, nullable=False, unique=False)
    children = relationship('Categories', backref=backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    items = relationship('Items', secondary=items_categories, back_populates='categories')

    def __init__(self, parent_id=None, title=None):
        self.parent_id = parent_id
        self.title = title

    def __repr__(self):
        return self.title

    # format choices for parent_id select box
    def select_choices(self, non_list=0):
        choices = [(self.id, self.title)]
        for child in self.children:
            if child.id != int(non_list):
                choices.extend([(child.id, f' -- {child.title}')])
        return choices

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    item_id = Column(ForeignKey('items.id'), nullable=False)
    description = Column(String, nullable=True)
    item = relationship('Items', back_populates='images')

    def __init__(self, file_name=None):
        self.file_name = file_name

    def __repr__(self):
        return self.file_name

class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=False)
    description = Column(String, nullable=False)
    found_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    location = Column(Geometry('POINT', srid=4326))
    area_id = Column(ForeignKey('areas.id'), nullable=True)
    categories = relationship('Categories', secondary=items_categories, back_populates='items')
    dating = relationship('Dating', secondary=items_dating, back_populates='items')
    images = relationship('Images', back_populates='item')

    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description

    def __repr__(self):
        return f'<Item {self.title!r}>'

    def get_area(self):
        area = Areas.query.get(self.area_id)
        return area