from . import db

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    __table_args__ = (
        db.CheckConstraint('type IN ("Chi tiêu", "Thu nhập")'),
    )


    user = db.relationship('User', back_populates='categories')
    budgets = db.relationship('Budget', back_populates='category', cascade='all, delete')
    transactions = db.relationship('Transaction', back_populates='category', cascade='all, delete')
