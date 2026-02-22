from datetime import datetime
from app import db


class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'culture_id', name='uk_user_culture_like'),
    )


class Collect(db.Model):
    __tablename__ = 'collects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'culture_id', name='uk_user_culture_collect'),
    )


class ViewHistory(db.Model):
    __tablename__ = 'view_histories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id', ondelete='CASCADE'), nullable=False)
    view_duration = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserBehavior(db.Model):
    __tablename__ = 'user_behaviors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id', ondelete='CASCADE'), nullable=False)
    behavior_type = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_user_behavior', 'user_id', 'behavior_type'),
        db.Index('idx_culture_behavior', 'culture_id', 'behavior_type'),
    )
