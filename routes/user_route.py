from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
import os
from werkzeug.security import generate_password_hash
from flask_mail import Mail as mail
from flask_mail import Message
import redis
import random
from . import db, User
from twilio.rest import Client
from pathlib import Path
import uuid


# Khởi tạo Blueprint
user_bp = Blueprint('user', __name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

otp_storage = {}

img_path = Path("assets/images")
img_ext = {"jpg", "jpeg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in img_ext


def check_password(real_password, password):
    return real_password == password

# Hàm chung để xử lý cập nhật thông tin người dùng (đăng ký hoặc chỉnh sửa)
def handle_user_update(data, user=None):
    """
    Hàm này xử lý việc đăng ký và cập nhật thông tin người dùng và ảnh đại diện.
    Nếu có `user` (trong trường hợp chỉnh sửa), sẽ cập nhật thông tin người dùng đó.
    Nếu không có `user`, sẽ tạo người dùng mới (trong trường hợp đăng ký).
    """
    # Lấy thông tin từ dữ liệu form hoặc JSON
    name = data.get("name")
    ngay_sinh = data.get("ngay_sinh")
    gioi_tinh = data.get("gioi_tinh")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    
    # Nếu là chỉnh sửa thông tin, lấy thông tin từ user hiện tại
    if user:
        user.name = name
        user.ngay_sinh = ngay_sinh
        user.gioi_tinh = gioi_tinh
        user.email = email
        user.phone = phone
        if password:
            user.password = password
    else:
        # Nếu là đăng ký mới, tạo user mới
        user = User(name=name, ngay_sinh=ngay_sinh, gioi_tinh=gioi_tinh, email=email, phone=phone, password=password)
        db.session.add(user)

    # Cập nhật ảnh đại diện nếu có
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = f"{user.user_id}_{uuid.uuid4().hex}.jpg"
            file_path = img_path / filename
            file.save(str(file_path))
            user.img = f"assets/images/{filename}"

    db.session.commit()
    return user


# Đăng ký
@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form

        if not data:
            return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

        # Kiểm tra xem email đã tồn tại chưa
        if User.query.filter_by(email=data.get("email")).first():
            return jsonify({"message": "Email đã tồn tại"}), 400

        # Gọi hàm chung để tạo người dùng mới
        user = handle_user_update(data)

        return jsonify({"message": "Đăng ký thành công"}), 201

    return render_template("register.html")


# Đăng nhập
@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json

        if not data:
            return render_template("login.html")

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password(user.password, password):
            return jsonify({"message": "Sai email hoặc mật khẩu"}), 401

        session["user_id"] = user.user_id
        return jsonify({"message": "Đăng nhập thành công"}), 200
    return render_template("login.html")


# Cập nhật dữ liệu người dùng
@user_bp.route("/editProfile", methods=["GET", "POST"])
def editProfile():
    if not session.get("user_id"):
        return redirect(url_for("user.login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("user.login"))

    if request.method == "POST":
        data = request.form
        
        # Gọi hàm chung để cập nhật thông tin người dùng
        user = handle_user_update(data, user)

        return redirect(url_for("user.viewProfile"))

    return render_template("editProfile.html", user=user)


# Xem tài khoản người dùng
@user_bp.route("/viewProfile", methods=["GET"])
def viewProfile():
    if not session.get("user_id"):
        return redirect(url_for("user.login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("user.login"))

    return render_template("viewProfile.html", user=user)


