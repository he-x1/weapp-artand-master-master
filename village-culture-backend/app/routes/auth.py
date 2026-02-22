from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, User
from loguru import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/user/wx-login', methods=['POST'])
def wx_login():
    try:
        data = request.get_json()
        code = data.get('code')
        if not code:
            return jsonify({'code': 400, 'message': '缺少code参数'}), 400
        
        openid = f'wx_{code}'
        user = User.query.filter_by(openid=openid).first()
        if not user:
            user = User(openid=openid, nickname='微信用户', avatar='/images/avatar.jpg')
            db.session.add(user)
            db.session.commit()
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        token = create_access_token(identity=user.id)
        return jsonify({'code': 0, 'message': 'success', 'data': {'token': token, 'userInfo': user.to_dict()}})
    except Exception as e:
        logger.error(f'微信登录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '登录失败'}), 500

@auth_bp.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')
        
        if not account or not password:
            return jsonify({'code': 400, 'message': '账号和密码不能为空'}), 400
        
        user = User.query.filter_by(phone=account).first()
        if not user or not user.check_password(password):
            return jsonify({'code': 401, 'message': '账号或密码错误'}), 401
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        token = create_access_token(identity=user.id)
        return jsonify({'code': 0, 'message': 'success', 'data': {'token': token, 'userInfo': user.to_dict()}})
    except Exception as e:
        logger.error(f'登录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '登录失败'}), 500

@auth_bp.route('/user/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        mobile = data.get('mobile')
        password = data.get('password')
        
        if not mobile or not password:
            return jsonify({'code': 400, 'message': '手机号和密码不能为空'}), 400
        
        if User.query.filter_by(phone=mobile).first():
            return jsonify({'code': 400, 'message': '该手机号已注册'}), 400
        
        user = User(phone=mobile, nickname=f'用户{mobile[-4:]}')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'code': 0, 'message': '注册成功'})
    except Exception as e:
        db.session.rollback()
        logger.error(f'注册失败: {str(e)}')
        return jsonify({'code': 500, 'message': '注册失败'}), 500

@auth_bp.route('/user/send-sms', methods=['POST'])
def send_sms():
    try:
        data = request.get_json()
        mobile = data.get('mobile')
        if not mobile:
            return jsonify({'code': 400, 'message': '手机号不能为空'}), 400
        return jsonify({'code': 0, 'message': '验证码已发送'})
    except Exception as e:
        logger.error(f'发送验证码失败: {str(e)}')
        return jsonify({'code': 500, 'message': '发送失败'}), 500

@auth_bp.route('/user/info', methods=['GET'])
@jwt_required()
def get_user_info():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        return jsonify({'code': 0, 'message': 'success', 'data': user.to_dict()})
    except Exception as e:
        logger.error(f'获取用户信息失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500
