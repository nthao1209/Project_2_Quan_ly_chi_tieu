from flask import Blueprint, jsonify, request, render_template,session,redirect,url_for
import os
from werkzeug.security import generate_password_hash
from flask_mail import Mail as mail
from flask_mail import Message
import redis
import random
from . import db, User
from twilio.rest import Client 
from pathlib import Path


# Khởi tạo Blueprint
user_bp = Blueprint('user', __name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

otp_storage = {}

img_path = Path("/assets/imgages")
img_ext = {"jpg", "jpeg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in img_ext


def check_password(real_password, password):
    return real_password == password

#Đăng ký
@user_bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'POST':
        data = request.json

        if not data:
            return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

        
        name = data.get("name")
        ngay_sinh = data.get("ngay_sinh")
        gioi_tinh = data.get("gioi_tinh")
        email = data.get("email")
        password = data.get("password")
        phone = data.get("phone")

        if not name or not email or not phone or not password:
            return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email đã tồn tại"}), 400

        new_user = User(name=name,ngay_sinh=ngay_sinh,gioi_tinh=gioi_tinh, email=email,phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Đăng ký thành công"}), 201
    
    return render_template("register.html")

#Đăng nhập
@user_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method == 'POST':
        data = request.json

        if not data:
            return render_template("login.html")

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password(user.password, password):
            print(email, password)
            return jsonify({"message": "Sai email hoặc mật khẩu"}), 401
        
        session["user_id"] = user.user_id
        return jsonify({"message": "Đăng nhập thành công"}), 200
    return render_template("login.html")

#Cập nhật dữ liệu người dùng
@user_bp.route("/editProfile", methods=["GET", "POST"])

def editProfile():
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if not session.get("user_id"):
        return redirect(url_for("user.login"))
    # Lấy thông tin người dùng từ cơ sở dữ liệu
    user_id = session["user_id"]
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("user.login"))
    # Cập nhật ảnh đại diệndiện
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = f"{user_id}.jpg"
                file_path = img_path/filename
                file.save(str(file_path))

                user.img = f"assets/images/{filename}"

    # Xử lý khi người dùng gửi yêu cầu xóa ảnh
    if request.method == "POST":
        if "delete_avatar" in request.form:
            if user.img:
                img_filename = Path(user.img).name
                img_file_path= img_path/img_filename
                
                if img_file_path.exists():  # Kiểm tra xem tệp có tồn tại không
                    img_file_path.unlink()
                user.img = None
                db.session.commit()

        return jsonify({"message": "Xóa ảnh đại diện thành công"}), 200


    # Xử lý khi người dùng gửi thông tin cập nhật
    if request.method == "POST":
        data = request.json  # Đọc dữ liệu từ JSON

        name = data.get("name", user.name)
        email = data.get("email", user.email)
        phone = data.get("phone", user.phone)
        oldPassword = data.get("currentPassword")
        password = data.get("newPassword")

        if not email:  # Kiểm tra nếu email không tồn tại
            return jsonify({"message": "Email không được để trống"}), 400

        if user.password != oldPassword:  # Kiểm tra mật khẩu cũ
            return jsonify({"message": "Mật khẩu cũ không chính xác"}), 400
        # Cập nhật thông tin người dùng
        user.name = name
        user.email = email
        user.phone = phone
        user.password = password

        db.session.commit()

        return redirect(url_for("home.home"))
    
    for file in img_path.rglob("*"):
        if file.suffix.lower() in img_ext:
            if user.img == str(file):
               user.img = str(img_path / file.name)
               break

    return render_template("editProfile.html",user=user)
