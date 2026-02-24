// pages/index/index.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    systemInfo: {},
    banners: [],
    categories: [],
    contentList: [],
    currentTab: 0,
    loading: false,
    hasMore: true,
    page: 1
  },

  onLoad: function() {
    var that = this
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })
    
    this.loadBanners()
    this.loadCategories()
    this.loadContent()
  },

  // 标准化图片URL
  normalizeImage: function(image) {
    const defaultImage = '/images/bg.png'
    if (!image) return defaultImage
    if (image.startsWith('http')) return image
    if (image.startsWith('/images/')) return image
    return defaultImage
  },

  // 加载轮播图
  loadBanners: async function() {
    try {
      const res = await apiService.getBanners()
      if (res.code === 0) {
        const banners = res.data.map(item => ({
          ...item,
          image: this.normalizeImage(item.image)
        }))
        this.setData({
          banners: banners
        })
      }
    } catch (err) {
      console.error('加载轮播图失败：', err)
    }
  },

  // 加载分类
  loadCategories: async function() {
    try {
      const res = await apiService.getCategories()
      if (res.code === 0) {
        this.setData({
          categories: res.data
        })
      }
    } catch (err) {
      console.error('加载分类失败：', err)
    }
  },

  // 加载内容列表
  loadContent: async function(isRefresh = false) {
    if (this.data.loading) return
    
    this.setData({ loading: true })
    
    try {
      const page = isRefresh ? 1 : this.data.page
      const res = this.data.currentTab === 0 
        ? await apiService.getRecommend(page)
        : await apiService.getLatest(page)
      
      if (res.code === 0) {
        const newList = (res.data.list || res.data || []).map(item => ({
          ...item,
          image: this.normalizeImage(item.image)
        }))
        const contentList = isRefresh ? newList : [...this.data.contentList, ...newList]
        
        this.setData({
          contentList: contentList,
          hasMore: res.data.hasMore !== false,
          page: page + 1,
          loading: false
        })
      }
    } catch (err) {
      console.error('加载内容失败：', err)
      this.setData({ loading: false })
    }
  },

  // 切换Tab
  switchTab: function(e) {
    const tab = parseInt(e.currentTarget.dataset.tab)
    if (tab !== this.data.currentTab) {
      this.setData({
        currentTab: tab,
        contentList: [],
        page: 1,
        hasMore: true
      })
      
      setTimeout(() => {
        this.loadContent(true)
      }, 100)
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

  // 轮播图点击
  onBannerTap: function(e) {
    const item = e.currentTarget.dataset.item
    if (item.link) {
      wx.navigateTo({
        url: item.link
      })
    }
  },

  // 分类点击
  onCategoryTap: function(e) {
    const categoryId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/exhibition/exhibition?categoryId=${categoryId}`
    })
  },

  // 内容点击
  onContentTap: function(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({
      url: `/pages/work-detail/work-detail?id=${item.id}`
    })
  },

  // 下拉刷新
  onPullDownRefresh: async function() {
    this.setData({
      page: 1,
      hasMore: true
    })
    
    await Promise.all([
      this.loadBanners(),
      this.loadContent(true)
    ])
    
    wx.stopPullDownRefresh()
  },

  // 触底加载更多
  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadContent()
    }
  }
})
