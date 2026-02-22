"""
带定时任务的应用启动脚本
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from scripts import start_scheduler
from loguru import logger

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logger.add(
    os.path.join(log_dir, 'app_{time}.log'),
    rotation='00:00',
    retention='7 days',
    level='INFO'
)

# 创建应用
app = create_app(os.getenv('FLASK_ENV', 'development'))

# 启动定时任务
with app.app_context():
    try:
        start_scheduler()
        logger.info('✅ 定时任务启动成功')
    except Exception as e:
        logger.error(f'❌ 定时任务启动失败: {e}')

if __name__ == '__main__':
    logger.info('🚀 启动应用...')
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)