from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Culture, UserBehavior
from loguru import logger

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend/personal', methods=['GET'])
@jwt_required()
def get_personal_recommend():
    try:
        user_id = get_jwt_identity()
        page_size = request.args.get('pageSize', 10, type=int)
        user_behaviors = UserBehavior.query.filter_by(user_id=user_id).all()
        if not user_behaviors:
            hot_cultures = Culture.query.filter_by(status=1, is_hot=True).order_by(Culture.score.desc()).limit(page_size).all()
            return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in hot_cultures]})
        category_ids = [b.culture.category_id for b in user_behaviors if b.culture]
        if not category_ids:
            hot_cultures = Culture.query.filter_by(status=1).order_by(Culture.view_count.desc()).limit(page_size).all()
            return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in hot_cultures]})
        from collections import Counter
        category_counter = Counter(category_ids)
        top_categories = [cat_id for cat_id, _ in category_counter.most_common(3)]
        viewed_ids = [b.culture_id for b in user_behaviors]
        recommendations = Culture.query.filter(Culture.category_id.in_(top_categories), Culture.status == 1, ~Culture.id.in_(viewed_ids)).order_by(Culture.score.desc()).limit(page_size).all()
        if len(recommendations) < page_size:
            hot_cultures = Culture.query.filter(Culture.status == 1, ~Culture.id.in_(viewed_ids), ~Culture.id.in_([r.id for r in recommendations])).order_by(Culture.score.desc()).limit(page_size - len(recommendations)).all()
            recommendations.extend(hot_cultures)
        return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in recommendations]})
    except Exception as e:
        logger.error(f'个性化推荐失败: {str(e)}')
        return jsonify({'code': 500, 'message': '推荐失败'}), 500

@recommend_bp.route('/recommend/hot', methods=['GET'])
def get_hot_recommend():
    try:
        limit = request.args.get('limit', 10, type=int)
        hot_cultures = Culture.query.filter_by(status=1).order_by(Culture.view_count.desc(), Culture.like_count.desc()).limit(limit).all()
        return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in hot_cultures]})
    except Exception as e:
        logger.error(f'获取热门推荐失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@recommend_bp.route('/recommend/preference', methods=['POST'])
@jwt_required()
def update_preference():
    try:
        return jsonify({'code': 0, 'message': 'success'})
    except Exception as e:
        logger.error(f'更新用户偏好失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败'}), 500
