from flask import Flask, request
from flask_cors import CORS
from time import time
from arxiv_chat.utils.postgres import connection
import logging
from flask_sqlalchemy import SQLAlchemy

def init_app():
    app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="template/app")
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = connection
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.secret_key = "YjJhNGI0ZmM0YmUzNmUwMTA1NjhlZmM0"
    app.config["SESSION_TYPE"] = "filesystem"
    db = SQLAlchemy(app)
    return app, db

app, db = init_app()

@app.before_request
def before_request():
    return

@app.after_request
def after_request(response):
    app.logger.info(f"{request.headers.get('X-Forwarded-For')} {request.method} {request.scheme} {request.full_path} {response.status}")
    return response
