from . import db

class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='moderator')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    logs = db.relationship('AdminLog', back_populates='admin', cascade='all, delete')