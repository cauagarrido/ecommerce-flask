from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

#modelagem banco



#rotas
@app.route('/teste')

def hello_world():
    return 'hello world'

if __name__ == "__main__":
    app.run(debug=True)