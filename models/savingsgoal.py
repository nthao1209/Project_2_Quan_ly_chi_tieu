from . import db

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    goal_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Numeric(15, 2), nullable=False)
    start_time = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text) 

    
    user = db.relationship('User', back_populates='savings_goals')
