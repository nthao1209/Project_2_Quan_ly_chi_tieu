from flask import Flask
from models import db, User  # Import after adjusting sys.path


def create_app():
    app = Flask(__name__)
    db.init_app(app)


    with app.app_context():
        db.create_all()  # Tạo database nếu chưa có

    return app
