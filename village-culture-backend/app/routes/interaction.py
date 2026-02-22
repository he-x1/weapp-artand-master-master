from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Culture, Like, Collect, ViewHistory, UserBehavior
from loguru import logger

interaction_bp = Blueprint('interaction', __name__)

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
@jwt_required()
def add_history():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        culture_id = data.get('id')
        if not culture_id:
            return jsonify({'code': 400, 'message': '缺少参数'}), 400
        history = ViewHistory(user_id=user_id, culture_id=culture_id)
        db.session.add(history)
        behavior = UserBehavior(user_id=user_id, culture_id=culture_id, behavior_type='view', weight=1.0)
        db.session.add(behavior)
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success'})
    except Exception as e:
        db.session.rollback()
        logger.error(f'记录浏览历史失败: {str(e)}')
        return jsonify({'code': 500, 'message': '操作失败'}), 500
