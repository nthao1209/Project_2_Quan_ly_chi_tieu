from flask import Blueprint, request, render_template

view = Blueprint("home", __name__)

@view.route("/")
def home():
    return render_template("register.html")