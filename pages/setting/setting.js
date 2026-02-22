// pages/setting/setting.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    userInfo: null,
    isLoggedIn: false,
    stats: {
      likes: 0,
      collects: 0,
      history: 0
    },
    menuItems: [
      { id: 'mylikes', title: '我的点赞', icon: '/images/love.png', count: 0 },
      { id: 'mycollects', title: '我的收藏', icon: '/images/collect.png', count: 0 },
      { id: 'history', title: '浏览历史', icon: '/images/see.png', count: 0 },
      { id: 'about', title: '关于我们', icon: '/images/class_white.png' },
      { id: 'feedback', title: '意见反馈', icon: '/images/class_black.png' },
      { id: 'settings', title: '设置', icon: '/images/bar_mine.png' }
    ]
  },

  onLoad: function (options) {
    this.checkLoginStatus()
  },

  onShow: function() {
    this.checkLoginStatus()
    if (this.data.isLoggedIn) {
      this.loadUserStats()
    }
  },

  // 检查登录状态
  checkLoginStatus: function() {
    const isLoggedIn = app.globalData.isLoggedIn
    const userInfo = app.globalData.userInfo
    
    this.setData({
      isLoggedIn: isLoggedIn,
      userInfo: userInfo
    })
  },

  // 加载用户统计数据
  loadUserStats: async function() {
    try {
      // TODO: 从后端获取真实数据
      // const res = await apiService.getUserStats()
      
      // 模拟数据
      this.setData({
        stats: {
          likes: 12,
          collects: 8,
          history: 25
        },
        'menuItems[0].count': 12,
        'menuItems[1].count': 8,
        'menuItems[2].count': 25
      })
    } catch (err) {
      console.error('加载统计数据失败：', err)
    }
  },

  // 登录按钮点击事件
  login: function() {
    wx.navigateTo({
      url: '/pages/login/login'
    })
  },

  // 菜单项点击事件
  onMenuClick: function(e) {
    const menuId = e.currentTarget.dataset.id
    
    if (!this.data.isLoggedIn && menuId !== 'about' && menuId !== 'feedback') {
      wx.showToast({
        title: '请先登录',
        icon: 'none',
        duration: 2000
      })
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' })
      }, 2000)
      return
    }

    switch(menuId) {
      case 'mylikes':
        wx.showToast({ title: '功能开发中', icon: 'none' })
        break
      case 'mycollects':
        wx.showToast({ title: '功能开发中', icon: 'none' })
        break
      case 'history':
        wx.showToast({ title: '功能开发中', icon: 'none' })
        break
      case 'about':
        wx.showModal({
          title: '关于我们',
          content: '这是一个传播乡村文化的微信小程序，致力于让更多人了解和喜爱中华传统乡村文化。传承文化，弘扬精神，让乡村文化在现代社会中焕发新的生机。',
          showCancel: false,
          confirmText: '我知道了',
          confirmColor: '#8B7355'
        })
        break
      case 'feedback':
        wx.showModal({
          title: '意见反馈',
          content: '如有问题或建议，请发送邮件至：feedback@village-culture.com',
          showCancel: false,
          confirmText: '好的',
          confirmColor: '#8B7355'
        })
        break
      case 'settings':
        wx.showToast({ title: '功能开发中', icon: 'none' })
        break
    }
  },

  // 退出登录
  logout: function() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      confirmText: '确定',
      cancelText: '取消',
      confirmColor: '#F56C6C',
      success: (res) => {
        if (res.confirm) {
          app.logout()
          this.setData({
            isLoggedIn: false,
            userInfo: null,
            stats: {
              likes: 0,
              collects: 0,
              history: 0
            }
          })
          wx.showToast({
            title: '已退出登录',
            icon: 'success',
            duration: 2000
          })
        }
      }
    })
  },

  onPullDownRefresh: function () {
    this.checkLoginStatus()
    if (this.data.isLoggedIn) {
      this.loadUserStats()
    }
    wx.stopPullDownRefresh()
  }
})
