'use strict';
import Promise from './es6-promise.min'

// 导入配置
const config = require('./config.js')

// 使用配置中的API地址
const API_BASE_URL = config.API.BASE_URL

/**
 * 网络请求封装
 */
function request(url, data = {}, method = 'GET', header = {}) {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token')
    
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...header
    }

    wx.request({
      url: url.startsWith('http') ? url : API_BASE_URL + url,
      data: data,
      method: method,
      header: headers,
      success: function(res) {
        if (res.statusCode === 200) {
          if (res.data.code === 0 || res.data.code === 200) {
            resolve(res.data)
          } else {
            wx.showToast({
              title: res.data.message || '请求失败',
              icon: 'none',
              duration: 2000
            })
            reject(res.data)
          }
        } else if (res.statusCode === 401) {
          wx.removeStorageSync('userInfo')
          wx.removeStorageSync('token')
          wx.showToast({
            title: '请重新登录',
            icon: 'none',
            duration: 2000
          })
          setTimeout(() => {
            wx.navigateTo({ url: '/pages/login/login' })
          }, 2000)
          reject(res)
        } else {
          wx.showToast({
            title: '网络错误',
            icon: 'none',
            duration: 2000
          })
          reject(res)
        }
      },
      fail: function(err) {
        wx.showToast({
          title: '网络连接失败',
          icon: 'none',
          duration: 2000
        })
        reject(err)
      }
    })
  })
}

/**
 * API接口定义
 */
const API = {
  USER: {
    WX_LOGIN: '/user/wx-login',
    LOGIN: '/user/login',
    REGISTER: '/user/register',
    GET_CODE: '/user/send-sms',
    GET_INFO: '/user/info',
    UPDATE_INFO: '/user/update',
    LOGOUT: '/user/logout'
  },

  CONTENT: {
    GET_BANNERS: '/content/banners',
    GET_RECOMMEND: '/content/recommend',
    GET_LATEST: '/content/latest',
    GET_DETAIL: '/content/detail',
    SEARCH: '/content/search',
    GET_CATEGORIES: '/content/categories',
    GET_BY_CATEGORY: '/content/category',
    REFRESH: '/content/refresh'  // 新增刷新接口
  },

  INTERACTION: {
    LIKE: '/interaction/like',
    UNLIKE: '/interaction/unlike',
    COLLECT: '/interaction/collect',
    UNCOLLECT: '/interaction/uncollect',
    GET_LIKES: '/interaction/likes',
    GET_COLLECTS: '/interaction/collects',
    GET_HISTORY: '/interaction/history',
    ADD_HISTORY: '/interaction/add-history',
    GET_STATUS: '/interaction/status'  // 新增获取互动状态接口
  },

  RECOMMEND: {
    GET_PERSONAL: '/recommend/personal',
    UPDATE_PREFERENCE: '/recommend/preference',
    GET_HOT: '/recommend/hot',
    GET_SIMILAR: '/recommend/similar',  // 新增相似推荐接口
    REFRESH: '/recommend/refresh'  // 新增刷新推荐接口
  }
}

module.exports = {
  API_BASE_URL,
  API,
  
  get: (url, data) => request(url, data, 'GET'),
  post: (url, data) => request(url, data, 'POST'),
  put: (url, data) => request(url, data, 'PUT'),
  delete: (url, data) => request(url, data, 'DELETE'),
  request: request,

  json2Form: function(json) {
    var str = []
    for(var p in json){
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(json[p]))
    }
    return str.join("&")
  }
}
