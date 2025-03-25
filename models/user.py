from . import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

        

    accounts = db.relationship('Account', back_populates='user', cascade='all, delete')
    transactions = db.relationship('Transaction', back_populates='user', cascade='all, delete')
    budgets = db.relationship('Budget', back_populates='user', cascade='all, delete')
    categories = db.relationship('Category', back_populates='user', cascade='all, delete')
    savings_goals = db.relationship('SavingsGoal', back_populates='user', cascade='all, delete')
