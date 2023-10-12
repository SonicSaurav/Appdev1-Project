from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask import current_app as app
from application.database import db
from .models import *
from datetime import datetime
from functools import wraps
import numbers
from flask_security import current_user, roles_required, auth_required

# Helpful functions
def add_role(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user:
            roles=app.security.datastore.find_or_create_role(
                name="user", permissions=["user-read", "user-write"]
            )
            db.session.commit()
            if len(current_user.roles)<=0:
                app.security.datastore.add_role_to_user(current_user,roles)
                db.session.commit()
        return func(*args, **kwargs)

    return wrapper

# Views: User
@app.route("/user")
@auth_required()
@add_role
@roles_required('user')
def user_home():
    (request.cookies)
    search_query=None
    search_query = request.args.get('search_query')
    if search_query:
        # Query the database for products matching the search query
        products = Product.query.filter(
            (Product.name.like(f'%{search_query}%')) |
            (Product.category.has(Category.name.like(f'%{search_query}%'))) |
            (Product.manufacture_date.like(f'%{search_query}%')) |
            (Product.rate_per_unit == search_query)
        ).all()
        
        return render_template('user.html', products=products, search_query=search_query)
    
    categories=Category.query.all()
    products=Product.query.all()
    response=make_response(render_template('user.html', categories=categories,products=products, search_query=search_query))
    response.set_cookie('cart','',expires=0)
    (response)
    return response

@app.route("/user/products/under/<string:cat_name>")
@auth_required()
@add_role
@roles_required('user')
def cat_products_user(cat_name):
    categories=Category.query.filter_by(name=cat_name).first()
    return render_template('cat_for_user.html', categories=categories)

@app.route('/mycart')
@auth_required()
@add_role
@roles_required('user')
def mycart():
    product_ids=request.cookies.get('cart', None)
    if product_ids:
        product_ids = list(map(int, product_ids.split(',')))
        products = db.session.query(Product).filter(Product.id.in_(product_ids)).all()
        products_dic={}
        products_dic['product']=[]
        products_dic['quantity']=[]
        products_dic['total_price']=0
        for product in products:
            products_dic['product'].append(product)
            available_qty=(product_ids.count(product.id), 'available') if product.stock> product_ids.count(product.id) else (product.stock, 'max')
            products_dic['quantity'].append(available_qty)
            products_dic['total_price']+=available_qty[0]*product.rate_per_unit
        session['product_ids']=product_ids
        return render_template('mycart.html',products_dic=products_dic)
    else:
        flash('Please add altlest one item into your cart!')
        return redirect(url_for('user_home'))
    
@app.route('/pay', methods=['GET', 'POST'])
@auth_required()
@add_role
@roles_required('user')
def pay():
    product_ids=session['product_ids']
    if product_ids:
        products = db.session.query(Product).filter(Product.id.in_(product_ids)).all()
        products_dic={}
        products_dic['product']=[]
        products_dic['quantity']=[]
        products_dic['total_price']=0
        for product in products:
            products_dic['product'].append(product)
            products_dic['quantity'].append(product_ids.count(product.id))
            products_dic['total_price']+=product_ids.count(product.id)*product.rate_per_unit
        # try:
        for i in range(len(products_dic['product'])):
            amount_paid=products_dic['product'][i].rate_per_unit* products_dic['quantity'][i]
            product_name = products_dic['product'][i].name
            quantity = products_dic['quantity'][i]
            order_date = datetime.now()
            user_id = current_user.id
            order=Order(amount_paid=amount_paid,quantity=quantity,product_name=product_name,order_date=order_date,user_id=user_id)
            db.session.add(order)
            db.session.commit()
            products_dic['product'][i].stock-=products_dic['quantity'][i]
            db.session.commit()
            ('commiting orders in the database')
        session.pop('product_ids')
        flash('Thank you for your purchase!', 'success')
        return redirect(url_for('user_home'))
        # except:
        #     db.session.rollback()
    flash('Something went wrong!', 'failure')
    return redirect(url_for('user_home'))

@app.route('/order/cancel')
@auth_required()
@add_role
@roles_required('user')
def canecl_order():
    flash('Your order is being cancel, cart is empty')
    return redirect(url_for('user_home'))

@app.route('/user/order/history')
@auth_required()
@add_role
@roles_required('user')
def order_history():
    return render_template('user_orders.html', current_user=current_user)