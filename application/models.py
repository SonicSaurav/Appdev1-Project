from application.database import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey, JSON, Float

class Category(db.Model):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    products = relationship('Product', backref='category')

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    stock = Column(Integer)
    name = Column(String(255))
    manufacture_date = Column(DateTime)
    expiry_date = Column(DateTime)
    rate_per_unit = Column(Float)
    unit = Column(String(20))  # e.g., 'Rs/Kg', 'Rs/Litre'
    category_id = Column(Integer, ForeignKey('categories.id'))
    
class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    amount_paid = Column(Float)
    product_name = Column(String(20))
    quantity = Column(Integer, nullable=False)
    order_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(MutableList.as_mutable(JSON), nullable=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(64), unique=True, nullable=False)
    orders = relationship('Order', backref='user')
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))