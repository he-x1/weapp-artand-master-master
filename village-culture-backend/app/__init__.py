from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # CORS配置 - 允许所有来源
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # JWT配置
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.routes.auth import auth_bp
    from app.routes.culture import culture_bp
    from app.routes.interaction import interaction_bp
    from app.routes.recommend import recommend_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(culture_bp, url_prefix='/api')
    app.register_blueprint(interaction_bp, url_prefix='/api')
    app.register_blueprint(recommend_bp, url_prefix='/api')
    
    # 静态文件服务 - 提供图片访问
    @app.route('/images/<path:filename>')
    def serve_images(filename):
        # 尝试从项目根目录的images文件夹提供图片
        frontend_images = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        if os.path.exists(os.path.join(frontend_images, filename)):
            return send_from_directory(frontend_images, filename)
        # 如果找不到，返回默认图片
        return send_from_directory(frontend_images, 'bg.png')
    
    with app.app_context():
        db.create_all()
    
    return app
