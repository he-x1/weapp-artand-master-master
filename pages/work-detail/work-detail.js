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
    relatedList: [],
    loading: true
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
      this.setData({ loading: true })
      const res = await apiService.getDetail(parseInt(id))
      
      if (res.code === 0) {
        const work = res.data
        
        // 设置轮播图（使用主图）
        const swipers = work.images 
          ? work.images.split(',').map((url, index) => ({ id: index + 1, url: url.trim() }))
          : [{ id: 1, url: work.image }]
        
        this.setData({ 
          work: work,
          swipers: swipers.length > 0 ? swipers : [{ id: 1, url: work.image }],
          likeCount: work.likeCount || 0,
          collectCount: work.collectCount || 0,
          loading: false
        })
        
        // 加载相关推荐
        this.loadRelated(work.categoryId)
        
        // 记录浏览历史
        this.addHistory(id)
        
        // 加载用户互动状态
        if (app.globalData.isLoggedIn) {
          this.loadInteractionStatus(id)
        }
      } else {
        wx.showToast({
          title: '内容不存在',
          icon: 'none'
        })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (err) {
      console.error('加载详情失败：', err)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载用户互动状态
  loadInteractionStatus: async function(id) {
    if (!app.globalData.isLoggedIn) return
    
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
      wx.showModal({
        title: '提示',
        content: '请先登录后再进行点赞',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/login' })
          }
        }
      })
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
            likeCount: res.data.likeCount || Math.max(0, likeCount - 1)
          })
          wx.showToast({
            title: '已取消点赞',
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: res.message || '操作失败',
            icon: 'none'
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
          wx.showToast({
            title: '点赞成功',
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: res.message || '操作失败',
            icon: 'none'
          })
        }
      }
    } catch (err) {
      console.error('点赞操作失败：', err)
      wx.showToast({
        title: '操作失败，请重试',
        icon: 'none'
      })
    }
  },

  // 收藏功能
  handleCollect: async function() {
    if (!app.globalData.isLoggedIn) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再进行收藏',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/login' })
          }
        }
      })
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
            collectCount: res.data.collectCount || Math.max(0, collectCount - 1)
          })
          wx.showToast({
            title: '已取消收藏',
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: res.message || '操作失败',
            icon: 'none'
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
        } else {
          wx.showToast({
            title: res.message || '操作失败',
            icon: 'none'
          })
        }
      }
    } catch (err) {
      console.error('收藏操作失败：', err)
      wx.showToast({
        title: '操作失败，请重试',
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
    const item = e.currentTarget.dataset.item || e.detail.item
    if (item && item.id) {
      wx.navigateTo({
        url: `/pages/work-detail/work-detail?id=${item.id}`
      })
    }
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

  // 下拉刷新
  onPullDownRefresh: function () {
    this.loadDetail(this.data.workId)
    wx.stopPullDownRefresh()
  },

  // 预览图片
  previewImage: function(e) {
    const urls = this.data.swipers.map(s => s.url)
    const current = e.currentTarget.dataset.url
    wx.previewImage({
      urls: urls,
      current: current
    })
  }
})
