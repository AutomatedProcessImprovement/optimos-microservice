from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
import os

def create_app():
    app = Flask(__name__)

    CORS(app)

    return app
