from . import db
class Account(db.Model):
    __tablename__ = 'accounts'
    account_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(10), default='VND')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='accounts')
    transactions = db.relationship('Transaction', back_populates='account', cascade='all, delete')