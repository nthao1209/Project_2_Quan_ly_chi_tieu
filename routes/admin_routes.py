from flask import Blueprint, request, session, current_app, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash
from models import Admin
from . import db
import traceback

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return {"success": False, "message": "Thiếu thông tin đăng nhập."}, 400

        admin = Admin.query.filter_by(email=email).first()

        if not admin or admin.password != password:
            return {"success": False, "message": "Thông tin đăng nhập không chính xác."}, 401

        if admin.role == "superadmin":
            session["pending_admin_id"] = admin.admin_id
            return {"success": True, "redirect": url_for("admin_bp.admin_secret")}

        session["admin_id"] = admin.admin_id
        session["role"] = admin.role
        return {"success": True, "redirect": url_for("admin_bp.manage_users")}

    return render_template("admin_login.html")



@admin_bp.route("/admin/secret", methods=["GET", "POST"])
def admin_secret():
    if request.method == "POST":
        entered_secret = request.form.get("secret_key")
        correct_secret = current_app.config.get("SUPERADMIN_SECRET")

        if entered_secret == correct_secret:
            admin_id = session.pop("pending_admin_id", None)
            if not admin_id:
                flash("Không tìm thấy admin đang chờ xác thực.", "error")
                return redirect(url_for("admin_bp.admin_login"))

            session["admin_id"] = admin_id
            session["role"] = "superadmin"
            flash("Xác thực thành công!", "success")
            return redirect(url_for("admin_bp.manage_users"))
        else:
            flash("Sai mã secret!", "danger")

    return render_template("admin_secret.html")


@admin_bp.route("/admin/users")
def manage_users():
    if session.get("role") not in ["admin", "superadmin"]:
        flash("Bạn không có quyền truy cập.", "error")
        return redirect(url_for("admin_bp.admin_login"))

    from models import User
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@admin_bp.route("/admin/users/<int:user_id>/toggle", methods=["POST"])
def toggle_user_status(user_id):
    if session.get("role") not in ["admin", "superadmin"]:
        flash("Bạn không có quyền truy cập.", "error")
        return redirect(url_for("admin_bp.admin_login"))

    from models import User
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"Đã {'mở khóa' if user.is_active else 'khóa'} người dùng {user.email}", "success")
    return redirect(url_for("admin_bp.manage_users"))
