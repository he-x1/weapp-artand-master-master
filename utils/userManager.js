/**
 * 用户状态管理模块
 */

const app = getApp()
const config = require('./config.js')

/**
 * 用户管理类
 */
class UserManager {
  constructor() {
    this.userInfo = null
    this.token = null
    this.isLoggedIn = false
  }

  /**
   * 初始化用户状态
   */
  init() {
    this.userInfo = wx.getStorageSync(config.STORAGE_KEYS.USER_INFO)
    this.token = wx.getStorageSync(config.STORAGE_KEYS.TOKEN)
    this.isLoggedIn = !!(this.userInfo && this.token)
  }

  /**
   * 登录
   */
  login(userInfo, token) {
    this.userInfo = userInfo
    this.token = token
    this.isLoggedIn = true
    
    wx.setStorageSync(config.STORAGE_KEYS.USER_INFO, userInfo)
    wx.setStorageSync(config.STORAGE_KEYS.TOKEN, token)
    
    // 更新全局数据
    app.globalData.userInfo = userInfo
    app.globalData.token = token
    app.globalData.isLoggedIn = true
  }

  /**
   * 退出登录
   */
  logout() {
    this.userInfo = null
    this.token = null
    this.isLoggedIn = false
    
    wx.removeStorageSync(config.STORAGE_KEYS.USER_INFO)
    wx.removeStorageSync(config.STORAGE_KEYS.TOKEN)
    
    // 更新全局数据
    app.globalData.userInfo = null
    app.globalData.token = null
    app.globalData.isLoggedIn = false
  }

  /**
   * 获取用户信息
   */
  getUserInfo() {
    return this.userInfo
  }

  /**
   * 获取Token
   */
  getToken() {
    return this.token
  }

  /**
   * 检查是否登录
   */
  checkLogin() {
    return this.isLoggedIn
  }

  /**
   * 更新用户信息
   */
  updateUserInfo(newInfo) {
    this.userInfo = { ...this.userInfo, ...newInfo }
    wx.setStorageSync(config.STORAGE_KEYS.USER_INFO, this.userInfo)
    app.globalData.userInfo = this.userInfo
  }

  /**
   * 获取用户偏好设置
   */
  getUserPreference() {
    return wx.getStorageSync(config.STORAGE_KEYS.USER_PREFERENCE) || {
      categories: [],
      notifications: true,
      theme: 'light'
    }
  }

  /**
   * 更新用户偏好设置
   */
  updateUserPreference(preference) {
    const currentPreference = this.getUserPreference()
    const newPreference = { ...currentPreference, ...preference }
    wx.setStorageSync(config.STORAGE_KEYS.USER_PREFERENCE, newPreference)
    return newPreference
  }
}

// 创建单例
const userManager = new UserManager()

module.exports = userManager
