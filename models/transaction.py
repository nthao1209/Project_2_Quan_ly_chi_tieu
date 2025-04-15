from . import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    note = db.Column(db.Text)
    #receipt_image_url = db.Column(db.String(255))
    #is_auto_generated = db.Column(db.Boolean, default=False)


    user = db.relationship('User', back_populates='transactions')
    account = db.relationship('Account', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')
