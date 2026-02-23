/**
 * API服务模块
 * 统一管理所有API调用，支持mock和真实API切换
 */

const api = require('./api.js')
const mockApi = require('../mock/data.js')
const config = require('./config.js')

/**
 * 是否使用Mock数据（开发阶段设为true，生产环境设为false）
 */
const USE_MOCK = false  // 改为false，使用真实API

/**
 * API服务类
 */
class ApiService {
  constructor() {
    this.useMock = USE_MOCK
  }

  /**
   * 切换Mock模式
   */
  setMockMode(useMock) {
    this.useMock = useMock
  }

  // ===== 用户相关接口 =====

  /**
   * 微信登录
   */
  async wxLogin(code) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: {
          token: 'mock_token_' + Date.now(),
          userInfo: {
            nickName: '用户' + Math.random().toString(36).substr(2, 6),
            avatarUrl: '/images/avatar.jpg'
          }
        }
      }
    }
    return await api.post(api.API.USER.WX_LOGIN, { code })
  }

  /**
   * 手机号登录
   */
  async login(account, password) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: {
          token: 'mock_token_' + Date.now(),
          userInfo: {
            nickName: account,
            avatarUrl: '/images/avatar.jpg'
          }
        }
      }
    }
    return await api.post(api.API.USER.LOGIN, { account, password })
  }

  /**
   * 用户注册
   */
  async register(data) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: null
      }
    }
    return await api.post(api.API.USER.REGISTER, data)
  }

  /**
   * 发送验证码
   */
  async sendSms(mobile, type = 'register') {
    if (this.useMock) {
      return {
        code: 0,
        message: '验证码已发送',
        data: null
      }
    }
    return await api.post(api.API.USER.GET_CODE, { mobile, type })
  }

  /**
   * 获取用户信息
   */
  async getUserInfo() {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: wx.getStorageSync('userInfo')
      }
    }
    return await api.get(api.API.USER.GET_INFO)
  }

  // ===== 内容相关接口 =====

  /**
   * 获取轮播图
   */
  async getBanners() {
    if (this.useMock) {
      return await mockApi.getBanners()
    }
    return await api.get(api.API.CONTENT.GET_BANNERS)
  }

  /**
   * 获取推荐内容
   */
  async getRecommend(page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return await mockApi.getRecommend(page, pageSize)
    }
    return await api.get(api.API.CONTENT.GET_RECOMMEND, { page, pageSize })
  }

  /**
   * 获取最新内容
   */
  async getLatest(page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return await mockApi.getRecommend(page, pageSize) // 复用recommend数据
    }
    return await api.get(api.API.CONTENT.GET_LATEST, { page, pageSize })
  }

  /**
   * 获取内容详情
   */
  async getDetail(id) {
    if (this.useMock) {
      return await mockApi.getDetail(id)
    }
    return await api.get(api.API.CONTENT.GET_DETAIL + '/' + id)
  }

  /**
   * 搜索内容
   */
  async search(keyword, page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return await mockApi.search(keyword)
    }
    return await api.get(api.API.CONTENT.SEARCH, { keyword, page, pageSize })
  }

  /**
   * 获取分类列表
   */
  async getCategories() {
    if (this.useMock) {
      return await mockApi.getCategories()
    }
    return await api.get(api.API.CONTENT.GET_CATEGORIES)
  }

  /**
   * 根据分类获取内容
   */
  async getByCategory(categoryId, page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return await mockApi.getByCategory(categoryId)
    }
    return await api.get(api.API.CONTENT.GET_BY_CATEGORY + '/' + categoryId, { page, pageSize })
  }

  /**
   * 刷新内容（重新爬取数据）
   */
  async refreshContent() {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: { crawled: 15, imported: 5 }
      }
    }
    return await api.post(api.API.CONTENT.REFRESH)
  }

  // ===== 互动相关接口 =====

  /**
   * 点赞
   */
  async like(id) {
    if (this.useMock) {
      return await mockApi.like(id)
    }
    return await api.post(api.API.INTERACTION.LIKE, { id })
  }

  /**
   * 取消点赞
   */
  async unlike(id) {
    if (this.useMock) {
      return await mockApi.unlike(id)
    }
    return await api.post(api.API.INTERACTION.UNLIKE, { id })
  }

  /**
   * 收藏
   */
  async collect(id) {
    if (this.useMock) {
      return await mockApi.collect(id)
    }
    return await api.post(api.API.INTERACTION.COLLECT, { id })
  }

  /**
   * 取消收藏
   */
  async uncollect(id) {
    if (this.useMock) {
      return await mockApi.uncollect(id)
    }
    return await api.post(api.API.INTERACTION.UNCOLLECT, { id })
  }

  /**
   * 获取点赞列表
   */
  async getLikes(page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: { list: [], total: 0 }
      }
    }
    return await api.get(api.API.INTERACTION.GET_LIKES, { page, pageSize })
  }

  /**
   * 获取收藏列表
   */
  async getCollects(page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: { list: [], total: 0 }
      }
    }
    return await api.get(api.API.INTERACTION.GET_COLLECTS, { page, pageSize })
  }

  /**
   * 记录浏览历史
   */
  async addHistory(id) {
    if (this.useMock) {
      return { code: 0, message: 'success' }
    }
    return await api.post(api.API.INTERACTION.ADD_HISTORY, { id })
  }

  /**
   * 获取浏览历史
   */
  async getHistory(page = 1, pageSize = config.PAGE_SIZE) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: { list: [], total: 0 }
      }
    }
    return await api.get(api.API.INTERACTION.GET_HISTORY, { page, pageSize })
  }

  /**
   * 获取互动状态
   */
  async getInteractionStatus(cultureId) {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: { isLiked: false, isCollected: false }
      }
    }
    return await api.get(api.API.INTERACTION.GET_STATUS + '/' + cultureId)
  }

  // ===== 智能推荐相关接口 =====

  /**
   * 获取个性化推荐
   */
  async getPersonalRecommend(pageSize = 10) {
    if (this.useMock) {
      return await mockApi.getRecommend(1, pageSize)
    }
    return await api.get(api.API.RECOMMEND.GET_PERSONAL, { pageSize })
  }

  /**
   * 更新用户偏好
   */
  async updatePreference(preferences) {
    if (this.useMock) {
      return { code: 0, message: 'success' }
    }
    return await api.post(api.API.RECOMMEND.UPDATE_PREFERENCE, preferences)
  }

  /**
   * 获取热门推荐
   */
  async getHotRecommend(limit = 10) {
    if (this.useMock) {
      return await mockApi.getRecommend(1, limit)
    }
    return await api.get(api.API.RECOMMEND.GET_HOT, { limit })
  }

  /**
   * 获取相似内容推荐
   */
  async getSimilarRecommend(cultureId, limit = 5) {
    if (this.useMock) {
      return await mockApi.getRecommend(1, limit)
    }
    return await api.get(api.API.RECOMMEND.GET_SIMILAR + '/' + cultureId, { limit })
  }

  /**
   * 刷新推荐系统
   */
  async refreshRecommendations() {
    if (this.useMock) {
      return {
        code: 0,
        message: 'success',
        data: []
      }
    }
    return await api.post(api.API.RECOMMEND.REFRESH)
  }
}

// 创建单例
const apiService = new ApiService()

module.exports = apiService
