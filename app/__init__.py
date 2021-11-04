import os
from flask import Flask
from flask_cors import CORS

print(os.getenv('ENV'))
if os.getenv('ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
cors = CORS(app)

@app.route('/')
def index():
    return 'asd'
