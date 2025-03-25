from . import db

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)
    action = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    admin = db.relationship('Admin', back_populates='logs')
