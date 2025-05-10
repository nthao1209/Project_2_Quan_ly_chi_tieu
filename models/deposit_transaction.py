from . import db

class DepositTransaction(db.Model):
    __tablename__ = 'deposit_transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    goal_id = db.Column(db.Integer, db.ForeignKey('savings_goals.goal_id'), nullable=False)  
    deposit_amount = db.Column(db.Numeric(10, 2), nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    to_account_id= db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)  
    deposit_date = db.Column(db.TIMESTAMP(timezone=True), nullable=False) 
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())  
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), onupdate=db.func.now())  

    goal = db.relationship('SavingsGoal', backref='deposit_transactions', lazy=True)
    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    to_account = db.relationship('Account', foreign_keys=[to_account_id])
