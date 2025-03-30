from flask import Blueprint, jsonify, request, render_template
from werkzeug.security import generate_password_hash
from flask_mail import Mail as mail
from flask_mail import Message
import redis
import random
from . import db, User
from twilio.rest import Client 

# Khởi tạo Blueprint
user_bp = Blueprint('user', __name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

otp_storage = {}


def check_password_hash(password_hash, password):
    return password_hash == password

#Đăng ký
@user_bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'POST':
        data = request.json

        if not data:
            return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

        
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        phone = data.get("phone")

        if not name or not email or not phone or not password:
            return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email đã tồn tại"}), 400

        new_user = User(name=name, email=email,phone=phone, password=password)
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
            return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            print(email, password)
            return jsonify({"message": "Sai email hoặc mật khẩu"}), 401

        return jsonify({"message": "Đăng ký thành công"}), 200
    return render_template("login.html")

#Cập nhật thông tin người dùng
@user_bp.route("/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.json

    if not data:
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    user = User.query.get(id)

    if not user:
        return jsonify({"message": "Người dùng không tồn tại"}), 404

    if name:
        user.name = name
    if email:
        user.email = email
    if phone:
        user.phone = phone
    if password:
        user.password = generate_password_hash(password)

    db.session.commit()

    return jsonify({"message": "Cập nhật thành công"}), 200

#Quên mật khẩu
@user_bp.route("/forgot-password", methods=["GET","POST"])
def forgot_password():
    data = request.json

    if not data:
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    email = data.get("email")
    phone = data.get("phone")

    if not email or not phone:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

    user = User.query.filter((User.email == email, User.phone == phone)).first()

    if not user:
        return jsonify({"message": "Email hoặc số điện thoại không tồn tại"}), 404

    otp = random.randint(100000, 999999)
    redis_client.setex(user.email, 300, otp)  # Lưu OTP vào Redis với thời gian sống 5 phút

    if email:
        msg = Message("Đặt lại mật khẩu",sender="admin@gmail.com",recipients=[email])
        msg.body = f"Mã OTP của bạn là: {otp}"
        mail.send(msg)
        return jsonify({"message": "Mã OTP đã được gửi đến email"}), 200

#    elif phone:  
#      twilio_client.messages.create(
#           body=f"Mã OTP của bạn là: {otp}",
#           from_=TWILIO_PHONE_NUMBER,
#           to=phone
#       )
#      return jsonify({"message": "Mã OTP đã được gửi đến số điện thoại"}), 2
 
    

