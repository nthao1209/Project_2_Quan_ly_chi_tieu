from . import db

class TransferTransaction(db.Model):
    __tablename__ = 'transfer_transactions'
    transfer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)

    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transfer_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    note = db.Column(db.Text)

    user = db.relationship('User')
    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    to_account = db.relationship('Account', foreign_keys=[to_account_id])
