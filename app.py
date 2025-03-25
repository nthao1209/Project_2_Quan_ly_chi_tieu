from flask import Flask , jsonify
from models.__init__ import *
from models import db
from routes import home,user_route
from routes.user_route import redis_client
import traceback



app = Flask(__name__)
app.register_blueprint(home.view)
app.register_blueprint(user_route.user_bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12092004@localhost:5432/Quan_ly_chi_tieu_ca_nhan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run()
