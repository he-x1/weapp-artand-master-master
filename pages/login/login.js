// pages/login/login.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

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
          success: async function(loginRes) {
            if (loginRes.code) {
              try {
                // 调用后端微信登录接口
                const result = await apiService.wxLogin(loginRes.code)
                
                if (result.code === 0) {
                  // 合并用户信息
                  const userInfo = {
                    ...result.data.userInfo,
                    ...res.userInfo
                  }
                  
                  app.setUserInfo(userInfo, result.data.token)
                  
                  wx.showToast({
                    title: '登录成功',
                    icon: 'success',
                    duration: 2000
                  })
                  
                  setTimeout(function() {
                    wx.navigateBack()
                  }, 2000)
                } else {
                  wx.showToast({
                    title: result.message || '登录失败',
                    icon: 'none',
                    duration: 2000
                  })
                }
              } catch (err) {
                console.error('微信登录失败：', err)
                wx.showToast({
                  title: '登录失败',
                  icon: 'none',
                  duration: 2000
                })
              }
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
  formSubmit: async function(e) {
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

    try {
      // 调用后端登录接口
      const result = await apiService.login(formData.account, formData.password)
      
      if (result.code === 0) {
        app.setUserInfo(result.data.userInfo, result.data.token)
        
        wx.showToast({
          title: '登录成功',
          icon: 'success',
          duration: 2000
        })
        
        setTimeout(function() {
          wx.navigateBack()
        }, 2000)
      } else {
        wx.showToast({
          title: result.message || '登录失败',
          icon: 'none',
          duration: 2000
        })
      }
    } catch (err) {
      console.error('登录失败：', err)
      wx.showToast({
        title: '登录失败',
        icon: 'none',
        duration: 2000
      })
    } finally {
      that.setData({ loading: false })
    }
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
