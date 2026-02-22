"""
定时任务调度器
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.crawler import CultureCrawler
from scripts.import_data import import_to_database
from app.services.recommender import init_recommender, recommender

scheduler = BackgroundScheduler()


def scheduled_crawl():
    """定时爬取任务"""
    logger.info('⏰ 开始定时爬取...')

    try:
        # 爬取数据
        crawler = CultureCrawler(upload_folder='uploads')
        data_list = crawler.crawl_all()

        if data_list:
            # 导入数据库
            imported = import_to_database(data_list)
            logger.info(f'✅ 定时爬取完成，新增 {imported} 条数据')
        else:
            logger.warning('⚠️ 未爬取到新数据')

    except Exception as e:
        logger.error(f'❌ 定时爬取失败: {e}')


def update_recommendations():
    """更新推荐系统"""
    logger.info('⏰ 更新推荐系统...')

    try:
        init_recommender()
        logger.info('✅ 推荐系统更新完成')
    except Exception as e:
        logger.error(f'❌ 推荐系统更新失败: {e}')


def setup_scheduler():
    """设置定时任务"""
    # 每天凌晨2点爬取数据
    scheduler.add_job(
        scheduled_crawl,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_crawl',
        name='每日数据爬取'
    )

    # 每小时更新推荐
    scheduler.add_job(
        update_recommendations,
        trigger=CronTrigger(hour='*'),
        id='hourly_recommend',
        name='每小时推荐更新'
    )

    logger.info('📅 定时任务设置完成')


def start_scheduler():
    """启动调度器"""
    setup_scheduler()
    scheduler.start()
    logger.info('🚀 定时任务调度器已启动')


if __name__ == '__main__':
    start_scheduler()

    # 保持运行
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info('调度器已停止')