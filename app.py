from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db' 
db = SQLAlchemy(app) 
CORS(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Modelagem do banco de dados
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


with app.app_context():
    db.create_all() 

@app.route('/api/products/add', methods=["POST"])
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
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return "Produto não encontrado.", 404
    db.session.delete(product)
    db.session.commit()
    return "Produto excluído com sucesso!", 200

@app.route('/api/products/<int:product_id>', methods=["GET"])
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



   
# Rotas
@app.route('/')
def hello_world():
    return 'hello world'

if __name__ == "__main__":
    app.run(debug=True)