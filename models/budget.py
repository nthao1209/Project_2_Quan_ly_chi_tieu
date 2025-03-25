from . import db

class Budget(db.Model):
    __tablename__ = 'budget'
    budget_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    limit_amount = db.Column(db.Numeric(15, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='budgets')
    category = db.relationship('Category', back_populates='budgets')