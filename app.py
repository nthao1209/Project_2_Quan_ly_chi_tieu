from flask import Flask , jsonify,session,has_request_context, send_from_directory
from models.__init__ import *
from models import db
from routes import home, user_route, forgot_password, transaction_routes,category_routes,bank_account,savinggoal_routes,budget_routes
from routes.extensions import mail
from flask_mail import Mail
from routes.user_route import redis_client
import traceback
from utils.seed_default_category import seed_default_categories


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.register_blueprint(home.view)
app.register_blueprint(user_route.user_bp)
app.register_blueprint(forgot_password.forgot_password_bp)
app.register_blueprint(category_routes.category_bp)  
app.register_blueprint(transaction_routes.transaction_bp)
app.register_blueprint(bank_account.bank_account_bp)
app.register_blueprint(savinggoal_routes.saving_goal_bp)
app.register_blueprint(budget_routes.budget_bp )
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True  # Đảm bảo bạn sử dụng SSL với cổng 465
app.config['MAIL_USE_TLS'] = False  # Không sử dụng TLS với cổng 465
app.config['MAIL_USERNAME'] = 'nthao4744@gmail.com'  
app.config['MAIL_PASSWORD'] = 'ddnp fpfn ptnb sctn  ' 
app.config['MAIL_DEFAULT_SENDER'] = 'nthao4744@gmail.com'
mail.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12092004@localhost:5432/Quan_ly_chi_tieu_ca_nhan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

@app.teardown_appcontext
def clear_session(exception=None):
    """Xóa session khi có request context."""
    if has_request_context():  # Kiểm tra có request context không
        session.clear()


with app.app_context():
    db.create_all()
    seed_default_categories()

@app.route('/assets/images/<filename>')
def serve_image(filename):
    return send_from_directory('assets/images', filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    