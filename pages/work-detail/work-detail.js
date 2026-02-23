// pages/work-detail/work-detail.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    systemInfo: {},
    workId: null,
    work: {},
    swipers: [],
    likeCount: 0,
    collectCount: 0,
    isLiked: false,
    isCollected: false,
    relatedList: []
  },

  onLoad: function (options) {
    var that = this
    
    // 获取内容ID
    if (options.id) {
      this.setData({ workId: options.id })
      this.loadDetail(options.id)
    }
    
    // 获取系统信息
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })
  },

  onShow: function() {
    // 每次显示页面时检查用户互动状态
    if (app.globalData.isLoggedIn && this.data.workId) {
      this.loadInteractionStatus(this.data.workId)
    }
  },

  // 加载内容详情
  loadDetail: async function(id) {
    try {
      const res = await apiService.getDetail(parseInt(id))
      
      if (res.code === 0) {
        const work = res.data
        
        // 设置轮播图（使用主图）
        const swipers = [
          { id: 1, url: work.image },
          { id: 2, url: work.image },
          { id: 3, url: work.image }
        ]
        
        this.setData({ 
          work: work,
          swipers: swipers,
          likeCount: work.likeCount || 0,
          collectCount: work.collectCount || 0
        })
        
        // 加载相关推荐
        this.loadRelated(work.categoryId)
        
        // 记录浏览历史
        this.addHistory(id)
        
        // 加载用户互动状态
        if (app.globalData.isLoggedIn) {
          this.loadInteractionStatus(id)
        }
      }
    } catch (err) {
      console.error('加载详情失败：', err)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载用户互动状态
  loadInteractionStatus: async function(id) {
    try {
      const res = await apiService.getInteractionStatus(id)
      if (res.code === 0) {
        this.setData({
          isLiked: res.data.isLiked,
          isCollected: res.data.isCollected
        })
      }
    } catch (err) {
      console.error('加载互动状态失败：', err)
    }
  },

  // 加载相关推荐
  loadRelated: async function(categoryId) {
    try {
      // 使用相似推荐接口
      const res = await apiService.getSimilarRecommend(this.data.workId, 5)
      if (res.code === 0) {
        // 过滤掉当前内容
        const related = res.data.filter(item => item.id !== parseInt(this.data.workId))
        
        this.setData({
          relatedList: related
        })
      }
    } catch (err) {
      console.error('加载相关推荐失败：', err)
      // 如果相似推荐失败，尝试按分类加载
      try {
        const res = await apiService.getByCategory(categoryId)
        if (res.code === 0) {
          const related = res.data.list
            .filter(item => item.id !== parseInt(this.data.workId))
            .slice(0, 5)
          
          this.setData({
            relatedList: related
          })
        }
      } catch (e) {
        console.error('按分类加载也失败：', e)
      }
    }
  },

  // 记录浏览历史
  addHistory: async function(id) {
    try {
      if (app.globalData.isLoggedIn) {
        await apiService.addHistory(id)
      }
    } catch (err) {
      console.error('记录浏览历史失败：', err)
    }
  },

  // 点赞功能
  handleLike: async function() {
    if (!app.globalData.isLoggedIn) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' })
      }, 1500)
      return
    }

    try {
      const { isLiked, workId, likeCount } = this.data
      
      if (isLiked) {
        // 取消点赞
        const res = await apiService.unlike(workId)
        if (res.code === 0) {
          this.setData({
            isLiked: false,
            likeCount: res.data.likeCount || (likeCount - 1)
          })
        }
      } else {
        // 执行点赞
        const res = await apiService.like(workId)
        if (res.code === 0) {
          this.setData({
            isLiked: true,
            likeCount: res.data.likeCount || (likeCount + 1)
          })
        }
      }
    } catch (err) {
      console.error('点赞操作失败：', err)
      wx.showToast({
        title: '操作失败',
        icon: 'none'
      })
    }
  },

  // 收藏功能
  handleCollect: async function() {
    if (!app.globalData.isLoggedIn) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' })
      }, 1500)
      return
    }

    try {
      const { isCollected, workId, collectCount } = this.data
      
      if (isCollected) {
        // 取消收藏
        const res = await apiService.uncollect(workId)
        if (res.code === 0) {
          this.setData({
            isCollected: false,
            collectCount: res.data.collectCount || (collectCount - 1)
          })
          wx.showToast({
            title: '已取消收藏',
            icon: 'success'
          })
        }
      } else {
        // 执行收藏
        const res = await apiService.collect(workId)
        if (res.code === 0) {
          this.setData({
            isCollected: true,
            collectCount: res.data.collectCount || (collectCount + 1)
          })
          wx.showToast({
            title: '收藏成功',
            icon: 'success'
          })
        }
      }
    } catch (err) {
      console.error('收藏操作失败：', err)
      wx.showToast({
        title: '操作失败',
        icon: 'none'
      })
    }
  },

  // 分享功能
  handleShare: function() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  // 跳转到详情
  goToDetail: function(e) {
    const id = e.currentTarget.dataset.id
    wx.redirectTo({
      url: `/pages/work-detail/work-detail?id=${id}`
    })
  },

  // 分享给好友
  onShareAppMessage: function() {
    return {
      title: this.data.work.name || '乡村文化传播',
      path: `/pages/work-detail/work-detail?id=${this.data.workId}`,
      imageUrl: this.data.work.image
    }
  },

  // 分享到朋友圈
  onShareTimeline: function() {
    return {
      title: this.data.work.name || '乡村文化传播',
      query: `id=${this.data.workId}`,
      imageUrl: this.data.work.image
    }
  },

  onPullDownRefresh: function () {
    this.loadDetail(this.data.workId)
    wx.stopPullDownRefresh()
  }
})
