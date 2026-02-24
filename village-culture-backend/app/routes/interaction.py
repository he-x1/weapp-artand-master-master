from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from functools import wraps
from app.models import db, Culture, Like, Collect, ViewHistory, UserBehavior
from loguru import logger

interaction_bp = Blueprint('interaction', __name__)

def optional_jwt(fn):
    """可选JWT认证装饰器 - 如果token存在则验证，不存在则继续"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # 获取Authorization header
            auth_header = request.headers.get('Authorization', '')
            if auth_header and auth_header.startswith('Bearer '):
                # 有token才验证
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

@interaction_bp.route('/interaction/like', methods=['POST'])
@jwt_required()
def like():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        culture_id = data.get('id')
        if not culture_id:
            return jsonify({'code': 400, 'message': '缺少参数'}), 400
        if Like.query.filter_by(user_id=user_id, culture_id=culture_id).first():
            return jsonify({'code': 400, 'message': '已点赞'}), 400
        like_record = Like(user_id=user_id, culture_id=culture_id)
        db.session.add(like_record)
        culture = Culture.query.get(culture_id)
        if culture:
            culture.like_count += 1
        behavior = UserBehavior(user_id=user_id, culture_id=culture_id, behavior_type='like', weight=2.0)
        db.session.add(behavior)
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success', 'data': {'likeCount': culture.like_count if culture else 0}})
    except Exception as e:
        db.session.rollback()
        logger.error(f'点赞失败: {str(e)}')
        return jsonify({'code': 500, 'message': '操作失败'}), 500

@interaction_bp.route('/interaction/unlike', methods=['POST'])
@jwt_required()
def unlike():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        culture_id = data.get('id')
        like_record = Like.query.filter_by(user_id=user_id, culture_id=culture_id).first()
        if not like_record:
            return jsonify({'code': 400, 'message': '未点赞'}), 400
        db.session.delete(like_record)
        culture = Culture.query.get(culture_id)
        if culture and culture.like_count > 0:
            culture.like_count -= 1
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success', 'data': {'likeCount': culture.like_count if culture else 0}})
    except Exception as e:
        db.session.rollback()
        logger.error(f'取消点赞失败: {str(e)}')
        return jsonify({'code': 500, 'message': '操作失败'}), 500

@interaction_bp.route('/interaction/collect', methods=['POST'])
@jwt_required()
def collect():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        culture_id = data.get('id')
        if not culture_id:
            return jsonify({'code': 400, 'message': '缺少参数'}), 400
        if Collect.query.filter_by(user_id=user_id, culture_id=culture_id).first():
            return jsonify({'code': 400, 'message': '已收藏'}), 400
        collect_record = Collect(user_id=user_id, culture_id=culture_id)
        db.session.add(collect_record)
        culture = Culture.query.get(culture_id)
        if culture:
            culture.collect_count += 1
        behavior = UserBehavior(user_id=user_id, culture_id=culture_id, behavior_type='collect', weight=3.0)
        db.session.add(behavior)
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success', 'data': {'collectCount': culture.collect_count if culture else 0}})
    except Exception as e:
        db.session.rollback()
        logger.error(f'收藏失败: {str(e)}')
        return jsonify({'code': 500, 'message': '操作失败'}), 500

@interaction_bp.route('/interaction/uncollect', methods=['POST'])
@jwt_required()
def uncollect():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        culture_id = data.get('id')
        collect_record = Collect.query.filter_by(user_id=user_id, culture_id=culture_id).first()
        if not collect_record:
            return jsonify({'code': 400, 'message': '未收藏'}), 400
        db.session.delete(collect_record)
        culture = Culture.query.get(culture_id)
        if culture and culture.collect_count > 0:
            culture.collect_count -= 1
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success', 'data': {'collectCount': culture.collect_count if culture else 0}})
    except Exception as e:
        db.session.rollback()
        logger.error(f'取消收藏失败: {str(e)}')
        return jsonify({'code': 500, 'message': '操作失败'}), 500

@interaction_bp.route('/interaction/add-history', methods=['POST'])
@optional_jwt
def add_history():
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        culture_id = data.get('id')
        
        if not culture_id:
            return jsonify({'code': 400, 'message': '缺少参数'}), 400
        
        if not user_id:
            # 未登录用户不记录历史
            return jsonify({'code': 0, 'message': 'success'})
        
        culture = Culture.query.get(culture_id)
        if not culture:
            return jsonify({'code': 404, 'message': '内容不存在'}), 404
        
        # 更新或创建浏览历史
        history = ViewHistory.query.filter_by(user_id=user_id, culture_id=culture_id).first()
        if history:
            history.created_at = db.func.now()
        else:
            history = ViewHistory(user_id=user_id, culture_id=culture_id)
            db.session.add(history)
        
        # 记录用户行为
        behavior = UserBehavior(user_id=user_id, culture_id=culture_id, behavior_type='view', weight=1.0)
        db.session.add(behavior)
        
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success'})
    except Exception as e:
        db.session.rollback()
        logger.error(f'记录浏览历史失败: {str(e)}')
        return jsonify({'code': 500, 'message': '操作失败'}), 500

# 获取用户点赞列表
@interaction_bp.route('/interaction/likes', methods=['GET'])
@optional_jwt
def get_likes():
    try:
        user_id = get_current_user_id()
        
        if not user_id:
            return jsonify({'code': 0, 'message': 'success', 'data': {'list': [], 'total': 0, 'page': 1, 'pageSize': 20, 'hasMore': False}})
        
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        
        # 查询用户点赞记录
        likes_query = Like.query.filter_by(user_id=user_id).order_by(Like.created_at.desc())
        pagination = likes_query.paginate(page=page, per_page=page_size, error_out=False)
        
        # 获取对应的文化内容
        culture_ids = [like.culture_id for like in pagination.items]
        cultures = Culture.query.filter(Culture.id.in_(culture_ids)).all()
        culture_dict = {c.id: c for c in cultures}
        
        result_list = []
        for like in pagination.items:
            culture = culture_dict.get(like.culture_id)
            if culture:
                item = culture.to_dict()
                item['likedAt'] = like.created_at.strftime('%Y-%m-%d %H:%M:%S') if like.created_at else None
                result_list.append(item)
        
        result = {
            'list': result_list,
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'hasMore': pagination.has_next
        }
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取点赞列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

# 新增：获取用户收藏列表
@interaction_bp.route('/interaction/collects', methods=['GET'])
@optional_jwt
def get_collects():
    try:
        user_id = get_current_user_id()
        
        if not user_id:
            return jsonify({'code': 0, 'message': 'success', 'data': {'list': [], 'total': 0, 'page': 1, 'pageSize': 20, 'hasMore': False}})
        
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        
        # 查询用户收藏记录
        collects_query = Collect.query.filter_by(user_id=user_id).order_by(Collect.created_at.desc())
        pagination = collects_query.paginate(page=page, per_page=page_size, error_out=False)
        
        # 获取对应的文化内容
        culture_ids = [collect.culture_id for collect in pagination.items]
        cultures = Culture.query.filter(Culture.id.in_(culture_ids)).all()
        culture_dict = {c.id: c for c in cultures}
        
        result_list = []
        for collect in pagination.items:
            culture = culture_dict.get(collect.culture_id)
            if culture:
                item = culture.to_dict()
                item['collectedAt'] = collect.created_at.strftime('%Y-%m-%d %H:%M:%S') if collect.created_at else None
                result_list.append(item)
        
        result = {
            'list': result_list,
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'hasMore': pagination.has_next
        }
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取收藏列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

# 新增：获取用户浏览历史
@interaction_bp.route('/interaction/history', methods=['GET'])
@optional_jwt
def get_history():
    try:
        user_id = get_current_user_id()
        
        if not user_id:
            return jsonify({'code': 0, 'message': 'success', 'data': {'list': [], 'total': 0, 'page': 1, 'pageSize': 20, 'hasMore': False}})
        
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        
        # 查询用户浏览历史
        history_query = ViewHistory.query.filter_by(user_id=user_id).order_by(ViewHistory.created_at.desc())
        pagination = history_query.paginate(page=page, per_page=page_size, error_out=False)
        
        # 获取对应的文化内容
        culture_ids = [h.culture_id for h in pagination.items]
        cultures = Culture.query.filter(Culture.id.in_(culture_ids)).all()
        culture_dict = {c.id: c for c in cultures}
        
        result_list = []
        for history in pagination.items:
            culture = culture_dict.get(history.culture_id)
            if culture:
                item = culture.to_dict()
                item['viewedAt'] = history.created_at.strftime('%Y-%m-%d %H:%M:%S') if history.created_at else None
                result_list.append(item)
        
        result = {
            'list': result_list,
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'hasMore': pagination.has_next
        }
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取浏览历史失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

# 检查用户对某内容的互动状态（支持未登录状态）
@interaction_bp.route('/interaction/status/<int:culture_id>', methods=['GET'])
@optional_jwt
def get_interaction_status(culture_id):
    try:
        user_id = get_current_user_id()

        if not user_id:
            # 未登录状态返回默认值
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'isLiked': False,
                    'isCollected': False
                }
            })

        is_liked = Like.query.filter_by(user_id=user_id, culture_id=culture_id).first() is not None
        is_collected = Collect.query.filter_by(user_id=user_id, culture_id=culture_id).first() is not None

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'isLiked': is_liked,
                'isCollected': is_collected
            }
        })
    except Exception as e:
        logger.error(f'获取互动状态失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500
