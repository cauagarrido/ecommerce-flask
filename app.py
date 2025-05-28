from flask import Flask

app = Flask(__name__)

#rotas
@app.route('/')

def hello_world():
    return 'hello world'

app.run(debug=True)