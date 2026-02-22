// app.js
App({
  onLaunch: function () {
    // 获取本地存储的日志
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    
    // 检查登录状态
    this.checkLoginStatus()
  },

  // 检查登录状态
  checkLoginStatus: function() {
    const userInfo = wx.getStorageSync('userInfo')
    const token = wx.getStorageSync('token')
    if (userInfo && token) {
      this.globalData.userInfo = userInfo
      this.globalData.token = token
      this.globalData.isLoggedIn = true
    }
  },

  // 获取系统信息
  getSystemInfo: function (cb) {
    var that = this
    if (that.globalData.systemInfo) {
      typeof cb == "function" && cb(that.globalData.systemInfo)
    } else {
      wx.getSystemInfo({
        success: function(res) {
          that.globalData.systemInfo = res
          typeof cb == "function" && cb(that.globalData.systemInfo)
        }
      })
    }
  },

  // 用户登录（使用微信登录）
  wxLogin: function(callback) {
    var that = this
    wx.login({
      success: function(res) {
        if (res.code) {
          // 将code发送到后端换取openid和session_key
          // TODO: 对接后端接口
          that.globalData.loginCode = res.code
          typeof callback == "function" && callback(res.code)
        } else {
          console.error('登录失败：' + res.errMsg)
        }
      },
      fail: function(err) {
        console.error('wx.login调用失败：', err)
      }
    })
  },

  // 保存用户信息
  setUserInfo: function(userInfo, token) {
    this.globalData.userInfo = userInfo
    this.globalData.token = token
    this.globalData.isLoggedIn = true
    wx.setStorageSync('userInfo', userInfo)
    wx.setStorageSync('token', token)
  },

  // 退出登录
  logout: function() {
    this.globalData.userInfo = null
    this.globalData.token = null
    this.globalData.isLoggedIn = false
    wx.removeStorageSync('userInfo')
    wx.removeStorageSync('token')
  },

  globalData:{
    userInfo: null,
    systemInfo: null,
    token: null,
    isLoggedIn: false,
    loginCode: null,
    // API基础配置
    apiBaseUrl: 'https://your-api-domain.com/api' // TODO: 替换为实际后端地址
  }
})
