from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/resultado", methods=["POST"])
def resultado():
    data = request.form
    return render_template("resultado.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
