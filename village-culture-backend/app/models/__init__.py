from app import db
from app.models.user import User
from app.models.culture import Culture, Category
from app.models.interaction import Like, Collect, ViewHistory, UserBehavior

__all__ = ['db', 'User', 'Culture', 'Category', 'Like', 'Collect', 'ViewHistory', 'UserBehavior']
