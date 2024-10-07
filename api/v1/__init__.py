from flask import Blueprint

from .chat import api as api_chat

api = Blueprint("v1", __name__)

api.register_blueprint(api_chat, url_prefix="/chat")


@api.route("/")
def main():
    return "v1"
