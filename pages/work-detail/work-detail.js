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
    loading: true,
    defaultImage: '/images/bg.png'
  },

  onLoad: function (options) {
    var that = this
    
    if (options.id) {
      this.setData({ workId: options.id })
      this.loadDetail(options.id)
    }
    
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })
  },

  onShow: function() {
    if (app.globalData.isLoggedIn && this.data.workId) {
      this.loadInteractionStatus(this.data.workId)
    }
  },

  // 标准化图片URL
  normalizeImage: function(image) {
    if (!image) {
      return this.data.defaultImage
    }
    if (image.startsWith('http')) {
      return image
    }
    if (image.startsWith('/images/')) {
      return image
    }
    return this.data.defaultImage
  },

  // 加载内容详情
  loadDetail: async function(id) {
    try {
      this.setData({ loading: true })
      const res = await apiService.getDetail(parseInt(id))

      if (res.code === 0) {
        const work = res.data

        // 标准化图片
        work.image = this.normalizeImage(work.image)
        
        // 设置轮播图
        let swipers = []
        if (work.images) {
          swipers = work.images.split(',')
            .map((url, index) => ({ id: index + 1, url: this.normalizeImage(url.trim()) }))
            .filter(s => s.url)
        }

        if (swipers.length === 0) {
          swipers = [{ id: 1, url: work.image || this.data.defaultImage }]
        }

        this.setData({
          work: work,
          swipers: swipers,
          likeCount: work.likeCount || 0,
          collectCount: work.collectCount || 0,
          loading: false
        })
        
        this.loadRelated(work.categoryId)
        this.addHistory(id)
        
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
      const res = await apiService.getSimilarRecommend(this.data.workId, 5)
      if (res.code === 0) {
        const related = res.data
          .filter(item => item.id !== parseInt(this.data.workId))
          .map(item => ({
            ...item,
            image: this.normalizeImage(item.image)
          }))
        
        this.setData({
          relatedList: related
        })
      }
    } catch (err) {
      console.error('加载相关推荐失败：', err)
      try {
        const res = await apiService.getByCategory(categoryId)
        if (res.code === 0) {
          const related = res.data.list
            .filter(item => item.id !== parseInt(this.data.workId))
            .slice(0, 5)
            .map(item => ({
              ...item,
              image: this.normalizeImage(item.image)
            }))
          
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
      await apiService.addHistory(id)
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
  },

  // 图片加载失败处理
  onSwiperImageError: function(e) {
    console.warn('轮播图加载失败:', e.detail)
    const index = e.currentTarget.dataset.index
    if (index !== undefined) {
      const swipers = this.data.swipers
      swipers[index].url = this.data.defaultImage
      this.setData({ swipers })
    }
  },

  // 相关推荐图片加载失败处理
  onRelatedImageError: function(e) {
    console.warn('相关推荐图片加载失败:', e.detail)
    const index = e.currentTarget.dataset.index
    if (index !== undefined) {
      const relatedList = this.data.relatedList
      relatedList[index].image = this.data.defaultImage
      this.setData({ relatedList })
    }
  }
})
