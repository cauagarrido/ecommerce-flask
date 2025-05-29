from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = "1212"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db' 

login_manager = LoginManager()

db = SQLAlchemy(app) 
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Modelagem do banco de dados
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


with app.app_context():
    db.create_all() 
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
    
@app.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify ({"message": "Usuário logado com sucesso!"})
        
    return jsonify ({"message": "Credenciais inválidas!"}), 401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Credenciais Inválidas"}), 401
    
    

@app.route('/api/products/add', methods=["POST"])
@login_required 
def add_product():
    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return "Dados inválidos. 'name' e 'price' são obrigatórios.", 400

    try:
        price = float(data['price']) 
    except ValueError:
        return "O preço deve ser um número.", 400

    product = Product(name=data['name'], price=price, description=data.get('description', ''))
    db.session.add(product)
    db.session.commit()
    return "Produto cadastrado com sucesso!", 200

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return "Produto não encontrado.", 404
    db.session.delete(product)
    db.session.commit()
    return "Produto excluído com sucesso!", 200

@app.route('/api/products/<int:product_id>', methods=["GET"])
@login_required 
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        })
    return jsonify({"message:" "Produto não encontrado"}), 404


@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required 
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return "Produto não encontrado.", 404

    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return "Dados inválidos. 'name' e 'price' são obrigatórios.", 400

    try:
        price = float(data['price'])
    except ValueError:
        return "O preço deve ser um número.", 400

    product.name = data['name']
    product.price = price
    product.description = data.get('description', product.description)
    db.session.commit()
    return "Produto atualizado com sucesso!", 200

@app.route('/api/products', methods=["GET"])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data ={
            'id': product.id,
            'name': product.name,
            'price': product.price,
        }
        product_list.append(product_data)
    return jsonify(product_list)
        
    return jsonify({'message': 'Teste'})



   
# Checkout

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    user = User.query.get(int(current_user.id))
    product = Product.query.get(product_id)
    
    if user and product:
        cart_item = CartItem(user_id=user.id, product_id= product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item adicionado com sucesso ao carrinho!'})
    return jsonify({'message': 'Falha ao adicionar item.'}), 400

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removido do carrinho com sucesso!'})
    return jsonify({'Falha ao remover item do carrinho.'}), 400


@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append({
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id,
            "product_name": product.name,
            "product_price": product.price
        })
       
    return jsonify(cart_content)

@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'O carrinho foi limpo com sucesso!'}), 200
    
    

if __name__ == "__main__":
    app.run(debug=True)