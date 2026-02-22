// pages/register/register.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    phoneNumber: '',
    verificationCode: '',
    password: '',
    confirmPassword: '',
    countdown: 0,
    isSending: false,
    loading: false
  },

  // 输入手机号
  onPhoneInput: function(e) {
    this.setData({
      phoneNumber: e.detail.value
    })
  },

  // 输入验证码
  onCodeInput: function(e) {
    this.setData({
      verificationCode: e.detail.value
    })
  },

  // 输入密码
  onPasswordInput: function(e) {
    this.setData({
      password: e.detail.value
    })
  },

  // 确认密码
  onConfirmPasswordInput: function(e) {
    this.setData({
      confirmPassword: e.detail.value
    })
  },

  // 发送验证码
  sendVerificationCode: async function() {
    const { phoneNumber, isSending, countdown } = this.data
    
    // 检查是否正在发送或倒计时中
    if (isSending || countdown > 0) {
      return
    }

    // 验证手机号格式
    if (!phoneNumber || !/^1[3-9]\d{9}$/.test(phoneNumber)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    this.setData({ isSending: true })

    try {
      const res = await apiService.sendSms(phoneNumber, 'register')
      
      if (res.code === 0) {
        wx.showToast({
          title: '验证码已发送',
          icon: 'success'
        })
        
        // 开始倒计时
        this.startCountdown()
      } else {
        wx.showToast({
          title: res.message || '发送失败',
          icon: 'none'
        })
      }
    } catch (err) {
      console.error('发送验证码失败：', err)
      wx.showToast({
        title: '发送失败',
        icon: 'none'
      })
    } finally {
      this.setData({ isSending: false })
    }
  },

  // 开始倒计时
  startCountdown: function() {
    let countdown = 60
    this.setData({ countdown })
    
    const timer = setInterval(() => {
      countdown--
      if (countdown <= 0) {
        clearInterval(timer)
        this.setData({ countdown: 0 })
      } else {
        this.setData({ countdown })
      }
    }, 1000)
  },

  // 提交注册
  formSubmit: async function() {
    const { phoneNumber, verificationCode, password, confirmPassword } = this.data

    // 验证输入
    if (!phoneNumber || !/^1[3-9]\d{9}$/.test(phoneNumber)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    if (!verificationCode || verificationCode.length !== 6) {
      wx.showToast({
        title: '请输入6位验证码',
        icon: 'none'
      })
      return
    }

    if (!password || password.length < 6) {
      wx.showToast({
        title: '密码至少6位',
        icon: 'none'
      })
      return
    }

    if (password !== confirmPassword) {
      wx.showToast({
        title: '两次密码不一致',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      const res = await apiService.register({
        mobile: phoneNumber,
        code: verificationCode,
        password: password
      })

      if (res.code === 0) {
        wx.showToast({
          title: '注册成功',
          icon: 'success',
          duration: 2000
        })

        // 自动登录
        setTimeout(() => {
          this.autoLogin(phoneNumber, password)
        }, 2000)
      } else {
        wx.showToast({
          title: res.message || '注册失败',
          icon: 'none'
        })
      }
    } catch (err) {
      console.error('注册失败：', err)
      wx.showToast({
        title: '注册失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 自动登录
  autoLogin: async function(account, password) {
    try {
      const res = await apiService.login(account, password)
      
      if (res.code === 0) {
        app.setUserInfo(res.data.userInfo, res.data.token)
        
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (err) {
      console.error('自动登录失败：', err)
      // 跳转到登录页
      wx.redirectTo({
        url: '/pages/login/login'
      })
    }
  },

  onPullDownRefresh: function() {
    wx.stopPullDownRefresh()
  }
})
