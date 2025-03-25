from . import db

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', back_populates='categories')
    budgets = db.relationship('Budget', back_populates='category', cascade='all, delete')