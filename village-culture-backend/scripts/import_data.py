"""
数据导入脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Culture, Category
from crawler import CultureCrawler
from loguru import logger
import json


def import_to_database(data_list):
    """将爬取的数据导入数据库"""
    app = create_app()

    with app.app_context():
        try:
            imported_count = 0

            for item in data_list:
                # 检查是否已存在（根据名称去重）
                existing = Culture.query.filter_by(name=item['name']).first()
                if existing:
                    logger.info(f'数据已存在，跳过: {item["name"]}')
                    continue

                # 创建新的文化内容记录
                culture = Culture(
                    name=item['name'],
                    category_id=item['category_id'],
                    description=item.get('description', ''),
                    summary=item.get('summary', ''),
                    origin=item.get('origin', '中国'),
                    heritage_level=item.get('heritage_level'),
                    cover_image=item.get('cover_image'),
                    source=item.get('source', ''),
                    source_url=item.get('source_url', ''),
                    status=1,  # 已发布
                    is_recommend=True,
                    score=50.0 + len(item.get('description', '')) / 100  # 基础分数
                )

                db.session.add(culture)
                imported_count += 1

                if imported_count % 10 == 0:
                    db.session.commit()
                    logger.info(f'已导入 {imported_count} 条数据')

            db.session.commit()
            logger.info(f'✅ 导入完成，共导入 {imported_count} 条新数据')

            return imported_count

        except Exception as e:
            db.session.rollback()
            logger.error(f'❌ 导入失败: {e}')
            return 0


def update_statistics():
    """更新统计数据"""
    app = create_app()

    with app.app_context():
        # 更新分类计数
        categories = Category.query.all()
        for category in categories:
            count = Culture.query.filter_by(category_id=category.id, status=1).count()
            logger.info(f'{category.name}: {count} 篇内容')


def main():
    """主函数"""
    logger.info('🚀 开始爬取数据...')

    # 1. 爬取数据
    crawler = CultureCrawler(upload_folder='../uploads')
    data_list = crawler.crawl_all()

    if not data_list:
        logger.warning('⚠️ 没有爬取到数据')
        return

    logger.info(f'📊 共爬取 {len(data_list)} 条数据')

    # 2. 保存原始数据
    with open('crawled_data.json', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)
    logger.info('💾 数据已保存到 crawled_data.json')

    # 3. 导入数据库
    imported = import_to_database(data_list)

    # 4. 更新统计
    update_statistics()

    logger.info(f'✨ 完成！新增 {imported} 条数据')


if __name__ == '__main__':
    main()