from flask import Blueprint, request, render_template,redirect,url_for,session,current_app
from . import user_route
from models import db, User , Transaction, Category, Account, Budget

import os

view = Blueprint("home", __name__)


@view.route("/")
def render():
    return redirect(url_for("home.home"))

@view.route("/home")
def home():
    user = User.query.get(session.get("user_id"))
    if not user:
        return redirect(url_for("user.login"))        
    return render_template("home.html",
                           user=user)

