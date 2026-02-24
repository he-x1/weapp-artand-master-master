// pages/discover/discover.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    systemInfo: {},
    recommendList: [],
    hotList: [],
    loading: false,
    page: 1,
    hasMore: true
  },

  onLoad: function (options) {
    var that = this
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })
    
    // 加载数据
    this.loadData()
  },

  onShow: function() {
    // 每次显示时刷新个性化推荐
    this.loadPersonalRecommend()
  },

  // 加载数据
  loadData: async function() {
    this.setData({ loading: true })
    
    try {
      // 并行加载个性化推荐和热门推荐
      const [personalRes, hotRes] = await Promise.all([
        this.loadPersonalRecommend(),
        apiService.getHotRecommend(6)
      ])
      
      if (hotRes.code === 0) {
        this.setData({
          hotList: hotRes.data || []
        })
      }
    } catch (err) {
      console.error('加载数据失败：', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  // 加载个性化推荐
  loadPersonalRecommend: async function() {
    try {
      let res
      if (app.globalData.isLoggedIn) {
        // 已登录用户获取个性化推荐
        res = await apiService.getPersonalRecommend(10)
      } else {
        // 未登录用户获取热门推荐
        res = await apiService.getHotRecommend(10)
      }
      
      if (res.code === 0) {
        this.setData({
          recommendList: res.data || []
        })
      }
    } catch (err) {
      console.error('加载个性化推荐失败：', err)
    }
  },

  // 刷新推荐
  onRefresh: async function() {
    wx.showLoading({ title: '刷新中...' })
    
    try {
      if (app.globalData.isLoggedIn) {
        await apiService.refreshRecommendations()
      }
      await this.loadPersonalRecommend()
      
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    } catch (err) {
      console.error('刷新失败：', err)
      wx.showToast({
        title: '刷新失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 搜索
  onSearch: function(e) {
    const keyword = e.detail.value
    if (keyword) {
      wx.navigateTo({
        url: `/pages/search/search?keyword=${keyword}`
      })
    }
  },

  // 跳转到详情页
  goToDetail: function(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({
      url: `/pages/work-detail/work-detail?id=${item.id}`
    })
  },

  // 精选内容图片加载失败
  onRecommendImageError: function(e) {
    const index = e.currentTarget.dataset.index
    if (index !== undefined) {
      const recommendList = this.data.recommendList
      recommendList[index].image = '/images/bg.png'
      this.setData({ recommendList })
    }
  },

  // 下拉刷新
  onPullDownRefresh: async function() {
    await this.loadData()
    wx.stopPullDownRefresh()
  }
})
