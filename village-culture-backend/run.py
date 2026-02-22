import os
from app import create_app
from loguru import logger

logger.add(os.path.join(os.path.dirname(__file__), 'logs', 'app_{time}.log'), rotation='00:00', retention='7 days', level='INFO')
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
