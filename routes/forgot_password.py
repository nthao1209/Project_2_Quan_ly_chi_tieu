from flask import Blueprint, request, render_template, jsonify
from flask_mail import Message
from routes.extensions import mail
from models import db, User
import random
import time
from werkzeug.security import generate_password_hash

# Blueprint cho quên mật khẩu
forgot_password_bp = Blueprint("forgot_password", __name__)

# Từ điển để lưu trữ OTP tạm thời
otp_store = {}

@forgot_password_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        if request.content_type != "application/json":
            return jsonify({"message": "Sai kiểu dữ liệu, cần JSON!"}), 415

        data = request.get_json(silent=True)
        if not data or "email" not in data:
            return jsonify({"message": "Vui lòng nhập email!"}), 400

        email = data["email"]
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "Email không tồn tại!"}), 400

        # Tạo và lưu trữ OTP
        otp = str(random.randint(100000, 999999))
        otp_store[email] = {"otp": otp, "expires_at": time.time() + 300}

        # Gửi OTP qua email
        msg = Message("Mã OTP đặt lại mật khẩu", recipients=[email])
        msg.body = f"Mã OTP của bạn là: {otp}"
        mail.send(msg)

        return jsonify({"message": "OTP đã được gửi!"}), 200

    return render_template("forgot_password.html")

@forgot_password_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if email in otp_store:
        stored_otp_info = otp_store[email]
        if time.time() < stored_otp_info["expires_at"] and stored_otp_info["otp"] == otp:
            return jsonify({"message": "OTP hợp lệ!"}), 200
        else:
            return jsonify({"message": "OTP không hợp lệ hoặc đã hết hạn!"}), 400
    else:
        return jsonify({"message": "OTP không tồn tại!"}), 400

@forgot_password_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("newPassword")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email không tồn tại!"}), 400

    user.password = new_password
    db.session.commit()

    # Xóa OTP sau khi sử dụng
    if email in otp_store:
        del otp_store[email]

    return jsonify({"message": "Mật khẩu đã được cập nhật!"}), 200

@forgot_password_bp.route("/forgot-password-page", methods=["GET"])
def forgot_password_page():
    return render_template("forgot_password.html")
