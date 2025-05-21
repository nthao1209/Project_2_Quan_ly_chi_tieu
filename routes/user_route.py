from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
import os
from werkzeug.security import generate_password_hash
from flask_mail import Mail as mail
from flask_mail import Message
import redis
import random
from . import db
from models import User, Category
from twilio.rest import Client
from pathlib import Path
import uuid
import traceback

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
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    ngay_sinh = data.get("ngay_sinh")
    gioi_tinh = data.get("gioi_tinh")
    img = data.get("img")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    confirm_password = data.get("confirmPassword")

    # Trường hợp đăng ký (user=None)
    if not user:
        if email and User.query.filter_by(email=email).first():
            raise ValueError("Email đã được sử dụng.")
        if phone and User.query.filter_by(phone=phone).first():
            raise ValueError("Số điện thoại đã được sử dụng.")
        if not current_password:
            raise ValueError("Bạn phải nhập mật khẩu.")
        if new_password or confirm_password:
            raise ValueError("Không cần nhập mật khẩu mới khi đăng ký.")
        
        user = User(
            name=name,
            email=email,
            password=current_password,  
            phone=phone,
            ngay_sinh=ngay_sinh,
            gioi_tinh=gioi_tinh,
            is_active=True,
            img=img,
            categories_copied=False
        )
        db.session.add(user)
        db.session.commit()
        return user

    # Trường hợp cập nhật thông tin
    print(">>> Đang cập nhật các trường:")
    print(f"Email: {email}, Phone: {phone}, Name: {name}, Ngày sinh: {ngay_sinh}")

    if email and email != user.email:
        if User.query.filter_by(email=email).filter(User.user_id != user.user_id).first():
            raise ValueError("Email đã được sử dụng.")

    if phone and phone != user.phone:
        if User.query.filter_by(phone=phone).filter(User.user_id != user.user_id).first():
            raise ValueError("Số điện thoại đã được sử dụng.")

    if name is not None:
        user.name = name
    if ngay_sinh is not None:
        user.ngay_sinh = ngay_sinh
    if gioi_tinh is not None:
        user.gioi_tinh = gioi_tinh
    if email is not None:
        user.email = email
    if phone is not None:
        user.phone = phone
    if img is not None:
        user.img = img

    # Xử lý đổi mật khẩu
    if new_password:
        if not current_password:
            raise ValueError("Bạn phải nhập mật khẩu hiện tại để đổi mật khẩu.")
        if current_password != user.password:
            raise ValueError("Mật khẩu hiện tại không đúng.")
        if new_password != confirm_password:
            raise ValueError("Mật khẩu mới và xác nhận mật khẩu không khớp.")
        user.password = new_password

    db.session.commit()
    return user


def copy_default_categories_to_user(user_id):
    default_categories = Category.query.filter_by(user_id=None).all()
    for default_cat in default_categories:
        existing_category = Category.query.filter_by(name=default_cat.name, user_id=user_id).first()
        if not existing_category:
            new_category = Category(
                name=default_cat.name,
                icon=default_cat.icon,
                type=default_cat.type,
                user_id=user_id
            )
            db.session.add(new_category)
    db.session.commit()

# Đăng ký
@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"message": "Không nhận được dữ liệu"}), 400

        email = data.get("email")
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email đã tồn tại"}), 400

        if data.get("password") != data.get("confirm_password"):
            return jsonify({"message": "Mật khẩu xác nhận không khớp"}), 400

        user = handle_user_update(data)

        db.session.commit()

        return jsonify({"message": "Đăng ký thành công", "redirect": url_for("user.login")}), 201

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
        
        if not user.is_active:
            if request.is_json:
                return jsonify({"message": "Tài khoản của bạn đã bị khóa."}), 403
            else:
                return jsonify({"message": "Tài khoản của bạn đã bị khóa.", "error": True})

        session["user_id"] = user.user_id
        
        # Chỉ sao chép danh mục nếu chưa từng sao chép trước đó
        if not user.categories_copied:
            copy_default_categories_to_user(user.user_id)
            user.categories_copied = True  # Đánh dấu là đã sao chép
            db.session.commit()

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
        # Trường hợp gửi bằng fetch (application/json)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        try:
        # Trường hợp người dùng chỉ muốn xóa avatar
            if isinstance(data, dict) and data.get("delete_avatar"):
                user.avatar = None
                db.session.commit()
                return jsonify({"message": "Avatar đã được xoá"}), 200
            # Gọi hàm cập nhật
            user = handle_user_update(data, user)
        except ValueError as e:
            if request.is_json:
                return jsonify({"error": True, "message": str(e)}), 400

        # Trả về khác nhau tùy kiểu gửi
        if request.is_json:
                return jsonify({"message": "Cập nhật thành công"}), 200
        else:
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

@user_bp.route("/logout", methods=["GET"])
def logout():
    if "user_id" in session:
        session.pop("user_id") 
        return redirect(url_for("user.login")) 
    return redirect(url_for("user.login")) 

# Xóa tài khoản
@user_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if not session.get("user_id"):
        return jsonify({"message": "Vui lòng đăng nhập"}), 401

    user_id = session.get("user_id")
    user = db.session.get(User,user_id)

    if not user:
        return jsonify({"message": "Người dùng không tồn tại"}), 404

    # Xóa người dùng
    db.session.delete(user)
    db.session.commit()

    session.pop("user_id")
    return jsonify({"message": "Tài khoản và dữ liệu liên quan đã được xóa"}), 200


