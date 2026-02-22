from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
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
    
    with app.app_context():
        db.create_all()
    
    return app
