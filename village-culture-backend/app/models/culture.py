from datetime import datetime
from app import db


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(100), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cultures = db.relationship('Culture', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'count': self.cultures.count()
        }


class Culture(db.Model):
    __tablename__ = 'cultures'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    summary = db.Column(db.String(500), nullable=True)
    origin = db.Column(db.String(200), nullable=True)
    heritage_level = db.Column(db.String(50), nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    images = db.Column(db.Text, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    collect_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)  # 添加分享计数字段
    score = db.Column(db.Float, default=0.0)
    is_hot = db.Column(db.Boolean, default=False)
    is_recommend = db.Column(db.Boolean, default=True)
    source = db.Column(db.String(200), nullable=True)
    source_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'categoryId': self.category_id,
            'category': self.category.name if self.category else None,
            'description': self.description,
            'summary': self.summary,
            'origin': self.origin,
            'image': self.cover_image,
            'viewCount': self.view_count,
            'likeCount': self.like_count,
            'collectCount': self.collect_count,
            'shareCount': self.share_count,
            'createTime': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }
