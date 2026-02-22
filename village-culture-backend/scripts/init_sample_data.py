"""
初始化示例数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Culture, Category
from loguru import logger


def init_sample_data():
    """初始化示例文化数据"""
    app = create_app()

    with app.app_context():
        # 示例数据列表
        sample_data = [
            {
                'name': '苏绣',
                'category_id': 1,
                'description': '苏绣是中国优秀的民族传统工艺之一，是苏州地区刺绣产品的总称。',
                'summary': '苏州传统刺绣',
                'origin': '江苏苏州',
                'heritage_level': '国家级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '景德镇瓷器',
                'category_id': 1,
                'description': '景德镇瓷器以"白如玉、明如镜、薄如纸、声如磬"的独特风格闻名中外。',
                'summary': '景德镇制瓷工艺',
                'origin': '江西景德镇',
                'heritage_level': '国家级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '京剧',
                'category_id': 2,
                'description': '京剧是中国五大戏曲剧种之一，被视为中国国粹。',
                'summary': '中国国粹戏曲',
                'origin': '北京',
                'heritage_level': '国家级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '昆曲',
                'category_id': 2,
                'description': '昆曲是中国古老的戏曲声腔、剧种。',
                'summary': '古老戏曲剧种',
                'origin': '江苏昆山',
                'heritage_level': '世界级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '端午节',
                'category_id': 6,
                'description': '端午节是集拜神祭祖、祈福辟邪、欢庆娱乐和饮食为一体的民俗大节。',
                'summary': '中国传统节日',
                'origin': '中国',
                'heritage_level': '世界级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '春节',
                'category_id': 6,
                'description': '春节是中华民族最隆重的传统佳节。',
                'summary': '最重要的传统节日',
                'origin': '中国',
                'heritage_level': '国家级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '嫦娥奔月',
                'category_id': 4,
                'description': '嫦娥奔月是中国上古时代神话传说故事。',
                'summary': '古代神话传说',
                'origin': '中国',
                'heritage_level': '民间传说',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '少林功夫',
                'category_id': 2,
                'description': '少林功夫是中国武术中体系最庞大的门派，是中华武术的象征。',
                'summary': '中国武术代表',
                'origin': '河南登封',
                'heritage_level': '世界级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '苗族银饰',
                'category_id': 1,
                'description': '苗族银饰是苗族重要的文化标志，精美的工艺在中国民族首饰中占有重要地位。',
                'summary': '苗族传统首饰',
                'origin': '贵州、湖南',
                'heritage_level': '国家级',
                'cover_image': '/images/default_culture.jpg'
            },
            {
                'name': '泥人张',
                'category_id': 1,
                'description': '泥人张彩塑为天津市的一种民间文化，著名的汉族传统手工艺品之一。',
                'summary': '天津彩塑艺术',
                'origin': '天津',
                'heritage_level': '国家级',
                'cover_image': '/images/default_culture.jpg'
            }
        ]

        try:
            imported_count = 0

            for item in sample_data:
                # 检查是否已存在
                existing = Culture.query.filter_by(name=item['name']).first()
                if existing:
                    logger.info(f'数据已存在: {item["name"]}')
                    continue

                # 创建记录
                culture = Culture(
                    name=item['name'],
                    category_id=item['category_id'],
                    description=item.get('description', ''),
                    summary=item.get('summary', ''),
                    origin=item.get('origin', '中国'),
                    heritage_level=item.get('heritage_level'),
                    cover_image=item.get('cover_image', '/images/default_culture.jpg'),
                    source='示例数据',
                    status=1,
                    is_recommend=True,
                    score=50.0
                )

                db.session.add(culture)
                imported_count += 1
                logger.info(f'添加: {item["name"]}')

            db.session.commit()
            logger.info(f'✅ 成功导入 {imported_count} 条示例数据')

        except Exception as e:
            db.session.rollback()
            logger.error(f'❌ 导入失败: {e}')


if __name__ == '__main__':
    logger.info('🚀 开始初始化示例数据...')
    init_sample_data()