"""
个性化推荐系统
基于协同过滤和内容特征的混合推荐算法
"""
from app.models import db, User, Culture, UserBehavior, Like, Collect, ViewHistory
from sqlalchemy import func, and_
from collections import defaultdict
from datetime import datetime
import numpy as np
from loguru import logger


class RecommenderSystem:
    """推荐系统"""

    def __init__(self):
        self.user_item_matrix = None
        self.item_similarity = None

    def build_user_item_matrix(self):
        """构建用户-物品矩阵"""
        # 获取所有用户行为数据
        behaviors = UserBehavior.query.all()

        # 用户-物品评分矩阵
        user_items = defaultdict(dict)
        users = set()
        items = set()

        for behavior in behaviors:
            user_id = behavior.user_id
            item_id = behavior.culture_id

            # 根据行为类型设置权重
            weight_map = {
                'view': 1.0,
                'like': 2.0,
                'collect': 3.0,
                'share': 4.0
            }
            weight = weight_map.get(behavior.behavior_type, 1.0)

            # 累加权重
            if item_id in user_items[user_id]:
                user_items[user_id][item_id] += weight
            else:
                user_items[user_id][item_id] = weight

            users.add(user_id)
            items.add(item_id)

        self.user_item_matrix = user_items
        return users, items

    def calculate_item_similarity(self):
        """计算物品相似度"""
        # 构建物品-用户倒排表
        item_users = defaultdict(set)

        for user_id, items in self.user_item_matrix.items():
            for item_id, rating in items.items():
                item_users[item_id].add(user_id)

        # 计算物品相似度（基于余弦相似度）
        item_similarity = defaultdict(dict)

        items = list(item_users.keys())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item_i = items[i]
                item_j = items[j]

                # 计算共同用户
                common_users = item_users[item_i] & item_users[item_j]

                if len(common_users) > 0:
                    # 计算相似度
                    sum_i = sum(self.user_item_matrix[u].get(item_i, 0) for u in common_users)
                    sum_j = sum(self.user_item_matrix[u].get(item_j, 0) for u in common_users)

                    if sum_i > 0 and sum_j > 0:
                        similarity = len(common_users) / (sum_i * sum_j) ** 0.5
                        item_similarity[item_i][item_j] = similarity
                        item_similarity[item_j][item_i] = similarity

        self.item_similarity = item_similarity

    def recommend_by_cf(self, user_id, n=10):
        """基于协同过滤的推荐"""
        if not self.user_item_matrix:
            self.build_user_item_matrix()

        if not self.item_similarity:
            self.calculate_item_similarity()

        # 用户已交互的物品
        user_items = self.user_item_matrix.get(user_id, {})
        if not user_items:
            return []

        # 计算推荐分数
        recommendations = defaultdict(float)

        for item_id, rating in user_items.items():
            # 找相似的物品
            similar_items = self.item_similarity.get(item_id, {})
            for similar_item, similarity in similar_items.items():
                if similar_item not in user_items:
                    recommendations[similar_item] += similarity * rating

        # 排序并返回TopN
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [item_id for item_id, score in sorted_recs[:n]]

    def recommend_by_content(self, user_id, n=10):
        """基于内容的推荐"""
        # 获取用户喜欢的分类
        user_behaviors = UserBehavior.query.filter_by(user_id=user_id).all()

        if not user_behaviors:
            return []

        # 统计用户偏好的分类
        category_preferences = defaultdict(float)
        for behavior in user_behaviors:
            culture = Culture.query.get(behavior.culture_id)
            if culture:
                weight_map = {'view': 1.0, 'like': 2.0, 'collect': 3.0, 'share': 4.0}
                weight = weight_map.get(behavior.behavior_type, 1.0)
                category_preferences[culture.category_id] += weight

        # 获取用户已交互的物品
        interacted_ids = {b.culture_id for b in user_behaviors}

        # 推荐相似分类的内容
        recommended = []
        for category_id, preference_score in sorted(category_preferences.items(),
                                                    key=lambda x: x[1], reverse=True):
            # 获取该分类下未交互的内容
            cultures = Culture.query.filter(
                and_(Culture.category_id == category_id,
                     Culture.status == 1,
                     ~Culture.id.in_(interacted_ids))
            ).order_by(Culture.score.desc()).limit(n).all()

            recommended.extend([c.id for c in cultures])

            if len(recommended) >= n:
                break

        return recommended[:n]

    def recommend_hybrid(self, user_id, n=10):
        """混合推荐：协同过滤 + 内容推荐"""
        # 协同过滤推荐
        cf_items = self.recommend_by_cf(user_id, n=n)

        # 内容推荐
        content_items = self.recommend_by_content(user_id, n=n)

        # 合并推荐结果（加权融合）
        item_scores = defaultdict(float)

        for i, item_id in enumerate(cf_items):
            item_scores[item_id] += (n - i) * 0.6  # 协同过滤权重0.6

        for i, item_id in enumerate(content_items):
            item_scores[item_id] += (n - i) * 0.4  # 内容推荐权重0.4

        # 排序并返回
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
        return [item_id for item_id, score in sorted_items[:n]]

    def get_hot_items(self, n=10):
        """获取热门内容"""
        cultures = Culture.query.filter_by(status=1).order_by(
            Culture.view_count.desc(),
            Culture.like_count.desc()
        ).limit(n).all()

        return [c.id for c in cultures]

    def update_scores(self):
        """更新内容分数"""
        cultures = Culture.query.filter_by(status=1).all()

        for culture in cultures:
            # 计算热度分数
            score = (
                    culture.view_count * 0.1 +
                    culture.like_count * 1.0 +
                    culture.collect_count * 2.0 +
                    culture.share_count * 3.0
            )

            # 时间衰减因子（越新越靠前）
            days = (datetime.utcnow() - culture.created_at).days
            time_decay = 1.0 / (1.0 + days * 0.01)

            culture.score = score * time_decay

        db.session.commit()
        logger.info('✅ 内容分数更新完成')


# 全局推荐器实例
recommender = RecommenderSystem()


def get_personal_recommendations(user_id, n=10):
    """获取个性化推荐"""
    # 检查用户是否有行为数据
    behavior_count = UserBehavior.query.filter_by(user_id=user_id).count()

    if behavior_count < 3:
        # 新用户，推荐热门内容
        logger.info(f'用户 {user_id} 行为数据不足，推荐热门内容')
        return recommender.get_hot_items(n)
    else:
        # 老用户，使用混合推荐
        logger.info(f'用户 {user_id} 使用混合推荐')
        return recommender.recommend_hybrid(user_id, n)


def init_recommender():
    """初始化推荐系统"""
    logger.info('🚀 初始化推荐系统...')
    recommender.build_user_item_matrix()
    recommender.calculate_item_similarity()
    recommender.update_scores()
    logger.info('✅ 推荐系统初始化完成')
