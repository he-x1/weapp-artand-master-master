from flask import Blueprint, request, jsonify
from app.models import db, Culture, Category
from sqlalchemy import or_
from loguru import logger

culture_bp = Blueprint('culture', __name__)

@culture_bp.route('/content/banners', methods=['GET'])
def get_banners():
    try:
        banners = Culture.query.filter_by(is_recommend=True, status=1).order_by(Culture.score.desc()).limit(5).all()
        result = [{'id': item.id, 'image': item.cover_image, 'title': item.name, 'link': f'/pages/work-detail/work-detail?id={item.id}'} for item in banners]
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取轮播图失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@culture_bp.route('/content/recommend', methods=['GET'])
def get_recommend():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        pagination = Culture.query.filter_by(status=1, is_recommend=True).order_by(Culture.score.desc(), Culture.created_at.desc()).paginate(page=page, per_page=page_size, error_out=False)
        result = {'list': [item.to_dict() for item in pagination.items], 'total': pagination.total, 'page': page, 'pageSize': page_size, 'hasMore': pagination.has_next}
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取推荐内容失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@culture_bp.route('/content/latest', methods=['GET'])
def get_latest():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        pagination = Culture.query.filter_by(status=1).order_by(Culture.created_at.desc()).paginate(page=page, per_page=page_size, error_out=False)
        result = {'list': [item.to_dict() for item in pagination.items], 'total': pagination.total, 'page': page, 'pageSize': page_size, 'hasMore': pagination.has_next}
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取最新内容失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@culture_bp.route('/content/detail/<int:id>', methods=['GET'])
def get_detail(id):
    try:
        culture = Culture.query.get(id)
        if not culture:
            return jsonify({'code': 404, 'message': '内容不存在'}), 404
        culture.view_count += 1
        db.session.commit()
        return jsonify({'code': 0, 'message': 'success', 'data': culture.to_dict()})
    except Exception as e:
        logger.error(f'获取内容详情失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@culture_bp.route('/content/search', methods=['GET'])
def search():
    try:
        keyword = request.args.get('keyword', '')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        
        if not keyword:
            return jsonify({'code': 400, 'message': '关键词不能为空'}), 400
        
        # 分页搜索
        query = Culture.query.filter(
            Culture.status == 1, 
            or_(Culture.name.contains(keyword), Culture.description.contains(keyword))
        ).order_by(Culture.score.desc())
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        result = {
            'list': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'hasMore': pagination.has_next
        }
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'搜索失败: {str(e)}')
        return jsonify({'code': 500, 'message': '搜索失败'}), 500

@culture_bp.route('/content/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
        return jsonify({'code': 0, 'message': 'success', 'data': [cat.to_dict() for cat in categories]})
    except Exception as e:
        logger.error(f'获取分类失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

@culture_bp.route('/content/category/<int:category_id>', methods=['GET'])
def get_by_category(category_id):
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        pagination = Culture.query.filter_by(category_id=category_id, status=1).order_by(Culture.score.desc()).paginate(page=page, per_page=page_size, error_out=False)
        result = {'list': [item.to_dict() for item in pagination.items], 'total': pagination.total, 'page': page, 'pageSize': page_size, 'hasMore': pagination.has_next}
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        logger.error(f'获取分类内容失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败'}), 500

# 新增：刷新内容（重新爬取数据）
@culture_bp.route('/content/refresh', methods=['POST'])
def refresh_content():
    """刷新内容数据"""
    try:
        from scripts.crawler import CultureCrawler
        from scripts.import_data import import_to_database
        import os
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_folder = os.path.join(project_root, 'uploads')
        
        # 执行爬虫
        crawler = CultureCrawler(upload_folder=upload_folder)
        data_list = crawler.crawl_all()
        
        if data_list:
            # 导入数据库
            imported = import_to_database(data_list)
            
            # 更新推荐系统分数
            from app.services.recommender import recommender
            recommender.update_scores()
            
            return jsonify({
                'code': 0, 
                'message': 'success',
                'data': {
                    'crawled': len(data_list),
                    'imported': imported
                }
            })
        else:
            return jsonify({'code': 0, 'message': '没有新数据', 'data': {'crawled': 0, 'imported': 0}})
    except Exception as e:
        logger.error(f'刷新内容失败: {str(e)}')
        return jsonify({'code': 500, 'message': '刷新失败'}), 500
