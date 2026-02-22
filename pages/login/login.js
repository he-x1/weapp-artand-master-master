// pages/login/login.js
var app = getApp()
var api = require('../../utils/api.js')

Page({
  data: {
    canIUseGetUserProfile: false,
    loading: false
  },

  onLoad: function() {
    // 检查是否支持getUserProfile
    if (wx.getUserProfile) {
      this.setData({
        canIUseGetUserProfile: true
      })
    }
  },

  // 微信授权登录
  getUserProfile: function() {
    var that = this
    that.setData({ loading: true })

    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: function(res) {
        console.log('获取用户信息成功：', res.userInfo)
        
        // 获取登录code
        wx.login({
          success: function(loginRes) {
            if (loginRes.code) {
              // TODO: 将code和userInfo发送到后端进行登录
              // 目前模拟登录成功
              const mockToken = 'mock_token_' + Date.now()
              app.setUserInfo(res.userInfo, mockToken)
              
              wx.showToast({
                title: '登录成功',
                icon: 'success',
                duration: 2000
              })
              
              setTimeout(function() {
                wx.navigateBack()
              }, 2000)
            } else {
              console.error('登录失败：' + loginRes.errMsg)
              wx.showToast({
                title: '登录失败',
                icon: 'none',
                duration: 2000
              })
            }
            that.setData({ loading: false })
          }
        })
      },
      fail: function(err) {
        console.error('获取用户信息失败：', err)
        wx.showToast({
          title: '授权失败',
          icon: 'none',
          duration: 2000
        })
        that.setData({ loading: false })
      }
    })
  },

  // 表单提交（手机号登录）
  formSubmit: function(e) {
    var that = this
    var formData = e.detail.value
    
    if (!formData.account || !formData.password) {
      wx.showToast({
        title: '请输入账号和密码',
        icon: 'none',
        duration: 2000
      })
      return
    }

    that.setData({ loading: true })

    // TODO: 对接后端登录接口
    // api.post(api.LOGIN, formData).then(res => {
    //   if (res.data.code === 200) {
    //     app.setUserInfo(res.data.userInfo, res.data.token)
    //     wx.showToast({ title: '登录成功', icon: 'success' })
    //     setTimeout(() => { wx.navigateBack() }, 2000)
    //   } else {
    //     wx.showToast({ title: res.data.message, icon: 'none' })
    //   }
    //   that.setData({ loading: false })
    // }).catch(err => {
    //   console.error('登录失败：', err)
    //   wx.showToast({ title: '登录失败', icon: 'none' })
    //   that.setData({ loading: false })
    // })

    // 模拟登录成功
    setTimeout(function() {
      const mockUserInfo = {
        nickName: formData.account,
        avatarUrl: '/images/avatar.jpg'
      }
      const mockToken = 'mock_token_' + Date.now()
      app.setUserInfo(mockUserInfo, mockToken)
      
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 2000
      })
      
      setTimeout(function() {
        wx.navigateBack()
      }, 2000)
      
      that.setData({ loading: false })
    }, 1000)
  },

  // 跳转到注册页
  goToRegister: function() {
    wx.navigateTo({
      url: '/pages/register/register'
    })
  },

  onPullDownRefresh: function() {
    wx.stopPullDownRefresh()
  }
})
