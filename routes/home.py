from flask import Blueprint, request, render_template,redirect,url_for,session,jsonify
from . import user_route
from models import db, User
import os

view = Blueprint("home", __name__)

@view.route("/")
def home():
    return render_template("home.html")

