from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from app.models import Culture, UserBehavior, Like, Collect, ViewHistory, db
from app.services.recommender import recommender, get_personal_recommendations
from loguru import logger
from collections import Counter

recommend_bp = Blueprint('recommend', __name__)

def optional_jwt(fn):
    """可选JWT认证装饰器 - 如果token存在则验证，不存在则继续"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header and auth_header.startswith('Bearer '):
                verify_jwt_in_request(optional=True)
            return fn(*args, **kwargs)
        except Exception as e:
            logger.warning(f'JWT验证失败，继续以未登录状态处理: {str(e)}')
            return fn(*args, **kwargs)
    return wrapper

def get_current_user_id():
    """安全地获取当前用户ID"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.replace('Bearer ', '').strip()
        if not token:
            return None
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception as e:
        logger.warning(f'获取用户ID失败: {str(e)}')
        return None

@recommend_bp.route('/recommend/personal', methods=['GET'])
@optional_jwt
def get_personal_recommend():
    """获取个性化推荐"""
    try:
        user_id = get_current_user_id()
        page_size = request.args.get('pageSize', 10, type=int)

        # 如果未登录，返回热门内容
        if not user_id:
            hot_cultures = Culture.query.filter_by(status=1).order_by(
                Culture.view_count.desc(),
                Culture.like_count.desc()
            ).limit(page_size).all()
            return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in hot_cultures]})

        # 使用推荐系统获取推荐内容ID列表
        recommended_ids = get_personal_recommendations(user_id, n=page_size)

        if not recommended_ids:
            # 如果没有推荐结果，返回热门内容
            hot_cultures = Culture.query.filter_by(status=1).order_by(
                Culture.view_count.desc(),
                Culture.like_count.desc()
            ).limit(page_size).all()
            return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in hot_cultures]})

        # 获取推荐的文化内容
        cultures = Culture.query.filter(Culture.id.in_(recommended_ids), Culture.status == 1).all()

        # 按推荐顺序排序
        culture_dict = {c.id: c for c in cultures}
        sorted_cultures = [culture_dict[cid] for cid in recommended_ids if cid in culture_dict]

        return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in sorted_cultures]})
    except Exception as e:
        logger.error(f'个性化推荐失败: {str(e)}')
        return jsonify({'code': 500, 'message': '推荐失败'}), 500

@recommend_bp.route('/recommend/hot', methods=['GET'])
def get_hot_recommend():
    """获取热门推荐"""
    try:
        limit = request.args.get('limit', 10, type=int)
        hot_cultures = Culture.query.filter_by(status=1).order_by(
            Culture.view_count.desc(), 
            Culture.like_count.desc()
        ).limit(limit).all()
        return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in hot_cultures]})
    except Exception as e:
        logger.error(f'获取热门推荐失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@recommend_bp.route('/recommend/preference', methods=['POST'])
@jwt_required()
def update_preference():
    """更新用户偏好"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        return jsonify({'code': 0, 'message': 'success'})
    except Exception as e:
        logger.error(f'更新用户偏好失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败'}), 500

@recommend_bp.route('/recommend/similar/<int:culture_id>', methods=['GET'])
def get_similar(culture_id):
    """获取相似内容推荐"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        # 获取当前内容
        culture = Culture.query.get(culture_id)
        if not culture:
            return jsonify({'code': 404, 'message': '内容不存在'}), 404
        
        # 基于分类推荐相似内容
        similar_cultures = Culture.query.filter(
            Culture.category_id == culture.category_id,
            Culture.id != culture_id,
            Culture.status == 1
        ).order_by(Culture.score.desc()).limit(limit).all()
        
        return jsonify({'code': 0, 'message': 'success', 'data': [item.to_dict() for item in similar_cultures]})
    except Exception as e:
        logger.error(f'获取相似推荐失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@recommend_bp.route('/recommend/refresh', methods=['POST'])
@jwt_required()
def refresh_recommendations():
    """刷新推荐系统"""
    try:
        user_id = get_jwt_identity()
        
        # 重新构建用户-物品矩阵
        recommender.build_user_item_matrix()
        recommender.calculate_item_similarity()
        recommender.update_scores()
        
        # 获取新的推荐
        recommended_ids = get_personal_recommendations(user_id, n=10)
        cultures = Culture.query.filter(Culture.id.in_(recommended_ids), Culture.status == 1).all()
        culture_dict = {c.id: c for c in cultures}
        sorted_cultures = [culture_dict[cid] for cid in recommended_ids if cid in culture_dict]
        
        return jsonify({
            'code': 0, 
            'message': 'success', 
            'data': [item.to_dict() for item in sorted_cultures]
        })
    except Exception as e:
        logger.error(f'刷新推荐失败: {str(e)}')
        return jsonify({'code': 500, 'message': '刷新失败'}), 500
