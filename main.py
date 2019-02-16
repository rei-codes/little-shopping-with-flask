from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
import datetime
app = Flask(__name__)

app.secret_key = 'ehe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    pw = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    auth = db.Column(db.Integer, nullable=False)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    cats = db.Column(db.Text, nullable=False)
    features = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quantity = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    datetime = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

auth = False
logged_in = False
the_user = ""

@app.route('/', methods=['GET', 'POST'])
def index():
  products = Product.query.all()
  return render_template('index.html', products = products, auth = auth, logged_in = logged_in)
        
@app.route('/register', methods = ['POST', 'GET'])
def register():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    pw = request.form['pw']
    new = User.query.filter_by(email=email).first()
    if new is not None:
      return redirect(url_for('index'))
    user = User(name=name, pw=pw, email=email, auth=0)
    db.session.add(user)
    db.session.commit()
  return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return redirect(url_for('index'))
  else:
    cart = Cart.query.all()
    for c in cart:
      c.quantity = 0
    db.session.commit()
    email = request.form['email']
    pw = request.form['pw']
    global the_user
    the_user = email
    if User.query.filter_by(email=email, pw=pw, auth=1).first():
      global auth
      global logged_in
      auth = True
      logged_in = True
      return redirect(url_for('index'))
    else:
      data = User.query.filter_by(email=email, pw=pw).first()
      if data is not None:
        logged_in = True
        auth = False
        return redirect(url_for('index'))
      return redirect(url_for('index'))

@app.route("/logout")
def logout():
  global auth
  global logged_in
  global the_user
  the_user = ""
  auth = False
  logged_in = False
  cart = Cart.query.all()
  for c in cart:
    c.quantity = 0
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/addproduct', methods = ['POST', 'GET'])
def addproduct():
  if request.method == 'POST':
    name = request.form['pname']
    price = request.form['price']
    stock = request.form['pstock']
    cats = request.form['cats']
    features = request.form['features']
    image = request.form['pimage']
    pro = Product(name=name, price=price, stock=stock, cats=cats, features=features, image=image)
    db.session.add(pro)
    db.session.commit()
    cart = Cart(id = pro.id, product_id = pro.id, quantity = 0)
    db.session.add(cart)
    db.session.commit()
  return redirect(url_for('index'))

@app.route('/updateproduct', methods = ['POST', 'GET'])
def updateproduct():
  if request.method == 'POST':
    pro = Product.query.filter_by(name=request.form['upsname']).first()
    pro.name = request.form['upname']
    pro.price = request.form['uprice']
    pro.stock = request.form['upstock']
    pro.cats = request.form['ucats']
    pro.features = request.form['ufeatures']
    db.session.add(pro)
    db.session.commit()
  return redirect(url_for('index'))

@app.route('/deleteproduct', methods = ['POST', 'GET'])
def deleteproduct():
  if request.method == 'POST':
    dpname = request.form['dpname']
    product = Product.query.filter_by(name = dpname).first()
    cart = Cart.query.filter_by(product_id = product.id).first()
    db.session.delete(cart)
    db.session.delete(product)
    db.session.commit()
  return redirect(url_for('index'))

@app.route('/addtocart/<productid>/<fromcart>', methods = ['POST', 'GET'])
def addtocart(productid,fromcart):
  if request.method == 'POST':
    if fromcart == 'True':
      product = Product.query.filter_by(id = productid).first()
      cart = Cart.query.filter_by(product_id = productid).first()
      if product.stock > cart.quantity:
        cart.quantity += 1
        db.session.commit()
      return redirect(url_for('cart'))
    else:
      product = Product.query.filter_by(id = productid).first()
      cart = Cart.query.filter_by(product_id = productid).first()
      if product.stock > cart.quantity:
        cart.quantity += 1
        db.session.commit()
      return redirect(url_for('index'))

@app.route('/deletefromcart/<productid>', methods = ['POST', 'GET'])
def deletefromcart(productid):
  if request.method == 'POST':
    cart = Cart.query.filter_by(product_id = productid).first()
    cart.quantity -= 1
    db.session.commit()
  return redirect(url_for('cart'))

@app.route('/clearcart')
def clearcart():
  cart = Cart.query.all()
  for c in cart:
    c.quantity = 0
  db.session.commit()
  return redirect(url_for('cart'))

@app.route('/cart')
def cart():
  cart = Cart.query.filter((Cart.quantity > 0)).all()
  products = Product.query.all()
  total = 0
  for c in cart:
    for p in products:
      if p.id == c.id:
        total += p.price*c.quantity
  return render_template('cart.html', cart = cart,products = products, logged_in = logged_in, total = total)

@app.route('/purchase', methods = ['POST', 'GET'])
def purchase():
  global the_user
  user = User.query.filter_by(email = the_user).first()
  cart = Cart.query.filter((Cart.quantity > 0)).all()
  products = Product.query.all()
  now = datetime.datetime.now()
  for c in cart:
      for p in products:
        if c.id == p.id:
          order = Order(user_id=user.id, product_id=p.id, datetime = now.strftime("%Y-%m-%d %H:%M"), amount=c.quantity)
          p.stock -= c.quantity
          db.session.add(order)
          db.session.add(p)
          db.session.commit()
  cart = Cart.query.all()
  for c in cart:
    c.quantity = 0
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/orderhistory')
def orderhistory():
  global the_user
  if the_user is "":
    return redirect(url_for('index'))
  user = User.query.filter_by(email = the_user).first()
  orders = Order.query.filter_by(user_id = user.id).all()
  products = Product.query.all()
  return render_template('orderhistory.html', products = products, orders = orders, logged_in = logged_in)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', e=e,a = 404), 404
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', e=e,a = 403), 403
@app.errorhandler(410)
def gone(e):
    return render_template('error.html', e=e,a = 410), 410
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', e=e,a = 500), 500

def create_app(config_filename):
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(410, gone)
    app.register_error_handler(500, internal_server_error)
    return app

if __name__ == '__main__':
  app.run(debug=True)
