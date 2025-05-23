from flask import Flask , jsonify,session,has_request_context, send_from_directory
from routes import transfer_transaction_routes
from models.__init__ import *
from models import db
from routes import home, user_route, forgot_password, transaction_routes,category_routes,bank_account,savinggoal_routes,budget_routes,deposit_transaction_routes,analytics,admin_routes
from routes.extensions import mail
from flask_mail import Mail
from routes.user_route import redis_client
import traceback
from utils.seed_default_category import seed_default_categories
from dotenv import load_dotenv
import os



load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.register_blueprint(home.view)
app.register_blueprint(user_route.user_bp)
app.register_blueprint(forgot_password.forgot_password_bp)
app.register_blueprint(category_routes.category_bp)  
app.register_blueprint(transaction_routes.transaction_bp)
app.register_blueprint(bank_account.bank_account_bp)
app.register_blueprint(savinggoal_routes.saving_goal_bp)
app.register_blueprint(budget_routes.budget_bp )
app.register_blueprint(deposit_transaction_routes.deposit_bp)
app.register_blueprint(analytics.analytics_bp)
app.register_blueprint(admin_routes.admin_bp)
app.register_blueprint(transfer_transaction_routes.transfer_bp)
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 465))
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "True") == "True"
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "False") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

app.config["SUPERADMIN_SECRET"] = os.getenv("SUPERADMIN_SECRET")
mail.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
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
    