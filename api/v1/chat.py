from flask import Blueprint, jsonify, request

from app import app
from arxiv_chat.models.rag import RAG

api = Blueprint("chat", __name__)

rag = RAG(num_docs=10, model_name="gpt-4o-mini")


@api.route("/", methods=["POST", "GET"])
def main():
    if request.method == "POST":
        body = request.get_json()
        if not body or not body.get("prompt"):
            return jsonify({"status": "ERROR", "message": "Request body is invalid"}), 400
        return app.response_class(
            rag.query(query=body["prompt"], streaming=True), mimetype="text/stream"
        )
    elif request.method == "GET":
        return "chat"
