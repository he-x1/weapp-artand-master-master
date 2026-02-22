/**
 * 智能推荐引擎
 * 基于用户行为和偏好的个性化推荐系统
 */

const config = require('./config.js')

class RecommendEngine {
  constructor() {
    this.userPreference = null
    this.behaviorHistory = []
  }

  /**
   * 初始化用户偏好
   */
  initUserPreference() {
    this.userPreference = wx.getStorageSync(config.STORAGE_KEYS.USER_PREFERENCE) || {
      categories: [],      // 喜欢的分类
      keywords: [],        // 搜索关键词
      viewHistory: [],     // 浏览历史
      likeHistory: [],     // 点赞历史
      collectHistory: []   // 收藏历史
    }
  }

  /**
   * 记录用户行为
   * @param {String} type - 行为类型: view, like, collect, search
   * @param {Object} data - 行为数据
   */
  recordBehavior(type, data) {
    this.initUserPreference()
    
    switch(type) {
      case 'view':
        this.recordView(data)
        break
      case 'like':
        this.recordLike(data)
        break
      case 'collect':
        this.recordCollect(data)
        break
      case 'search':
        this.recordSearch(data)
        break
    }
    
    this.savePreference()
  }

  /**
   * 记录浏览行为
   */
  recordView(data) {
    const history = this.userPreference.viewHistory
    
    // 移除旧的浏览记录
    const index = history.findIndex(item => item.id === data.id)
    if (index > -1) {
      history.splice(index, 1)
    }
    
    // 添加到最前面
    history.unshift({
      id: data.id,
      categoryId: data.categoryId,
      timestamp: Date.now()
    })
    
    // 最多保留50条
    if (history.length > 50) {
      history.pop()
    }
    
    // 更新分类偏好
    this.updateCategoryPreference(data.categoryId)
  }

  /**
   * 记录点赞行为
   */
  recordLike(data) {
    const history = this.userPreference.likeHistory
    
    if (data.isLike) {
      // 添加点赞记录
      history.push({
        id: data.id,
        categoryId: data.categoryId,
        timestamp: Date.now()
      })
      
      // 增加分类权重
      this.updateCategoryPreference(data.categoryId, 2)
    } else {
      // 移除点赞记录
      const index = history.findIndex(item => item.id === data.id)
      if (index > -1) {
        history.splice(index, 1)
      }
    }
  }

  /**
   * 记录收藏行为
   */
  recordCollect(data) {
    const history = this.userPreference.collectHistory
    
    if (data.isCollect) {
      // 添加收藏记录
      history.push({
        id: data.id,
        categoryId: data.categoryId,
        timestamp: Date.now()
      })
      
      // 增加分类权重（收藏权重更高）
      this.updateCategoryPreference(data.categoryId, 3)
    } else {
      // 移除收藏记录
      const index = history.findIndex(item => item.id === data.id)
      if (index > -1) {
        history.splice(index, 1)
      }
    }
  }

  /**
   * 记录搜索行为
   */
  recordSearch(keyword) {
    const keywords = this.userPreference.keywords
    
    // 移除重复项
    const index = keywords.indexOf(keyword)
    if (index > -1) {
      keywords.splice(index, 1)
    }
    
    // 添加到最前面
    keywords.unshift(keyword)
    
    // 最多保留20个
    if (keywords.length > 20) {
      keywords.pop()
    }
  }

  /**
   * 更新分类偏好
   */
  updateCategoryPreference(categoryId, weight = 1) {
    const categories = this.userPreference.categories
    
    const index = categories.findIndex(item => item.id === categoryId)
    
    if (index > -1) {
      categories[index].score += weight
    } else {
      categories.push({
        id: categoryId,
        score: weight
      })
    }
    
    // 按分数排序
    categories.sort((a, b) => b.score - a.score)
    
    // 只保留前5个最喜欢的分类
    if (categories.length > 5) {
      categories.splice(5)
    }
  }

  /**
   * 保存偏好设置
   */
  savePreference() {
    wx.setStorageSync(config.STORAGE_KEYS.USER_PREFERENCE, this.userPreference)
  }

  /**
   * 获取推荐分类（基于用户偏好）
   */
  getRecommendCategories() {
    this.initUserPreference()
    
    return this.userPreference.categories
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(item => item.id)
  }

  /**
   * 获取推荐关键词
   */
  getRecommendKeywords() {
    this.initUserPreference()
    
    return this.userPreference.keywords.slice(0, 5)
  }

  /**
   * 计算内容推荐分数
   * @param {Object} content - 内容数据
   * @returns {Number} 推荐分数
   */
  calculateRecommendScore(content) {
    this.initUserPreference()
    
    let score = 0
    
    // 分类匹配加分
    const categoryScore = this.userPreference.categories.find(
      item => item.id === content.categoryId
    )
    if (categoryScore) {
      score += categoryScore.score * 10
    }
    
    // 未浏览过加分
    const viewed = this.userPreference.viewHistory.some(
      item => item.id === content.id
    )
    if (!viewed) {
      score += 5
    }
    
    // 热度加分
    score += Math.min(content.viewCount / 100, 10)
    score += Math.min(content.likeCount / 10, 5)
    score += Math.min(content.collectCount / 5, 3)
    
    return score
  }

  /**
   * 排序推荐内容
   * @param {Array} contents - 内容列表
   * @returns {Array} 排序后的内容
   */
  sortRecommendContents(contents) {
    return contents
      .map(content => ({
        ...content,
        recommendScore: this.calculateRecommendScore(content)
      }))
      .sort((a, b) => b.recommendScore - a.recommendScore)
  }
}

// 创建单例
const recommendEngine = new RecommendEngine()

module.exports = recommendEngine
