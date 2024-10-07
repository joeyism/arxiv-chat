from flask import render_template

from app import app

from api.v1 import api as api_v1

app.register_blueprint(api_v1, url_prefix="/api/v1")

@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")

@app.route("/api", methods=["GET"])
def api():
    return "api"
