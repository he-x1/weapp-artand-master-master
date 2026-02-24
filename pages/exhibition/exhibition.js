// pages/exhibition/exhibition.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    systemInfo: {},
    categories: [],
    activeCategoryId: null,
    currentContent: [],
    currentCategoryName: '',
    loading: false,
    page: 1,
    hasMore: true,
    type: 'category',
    title: ''
  },

  onLoad: function (options) {
    var that = this
    
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })

    if (options.type) {
      const type = options.type
      const title = options.title || ''
      
      this.setData({
        type: type,
        title: title
      })
      
      if (title) {
        wx.setNavigationBarTitle({ title: title })
      }
      
      this.loadDataByType(type)
    } else if (options.categoryId) {
      const categoryId = parseInt(options.categoryId)
      this.setData({
        type: 'category',
        activeCategoryId: categoryId
      })
      this.loadCategories().then(() => {
        this.loadCategoryContent(categoryId)
      })
    } else {
      this.loadCategories().then(() => {
        if (this.data.categories.length > 0) {
          this.setData({ activeCategoryId: this.data.categories[0].id })
          this.loadCategoryContent(this.data.categories[0].id)
        }
      })
    }
  },

  onShow: function() {
    if (this.data.type !== 'category' && app.globalData.isLoggedIn) {
      this.loadDataByType(this.data.type)
    }
  },

  // 标准化图片URL
  normalizeImage: function(image) {
    const defaultImage = '/images/bg.png'
    if (!image) return defaultImage
    if (image.startsWith('http')) return image
    if (image.startsWith('/images/')) return image
    return defaultImage
  },

  // 根据类型加载数据
  loadDataByType: async function(type) {
    if (!app.globalData.isLoggedIn) {
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

    this.setData({ loading: true, page: 1, hasMore: true })
    
    try {
      let res
      let contentList = []
      
      switch(type) {
        case 'likes':
          res = await apiService.getLikes(1, 20)
          if (res.code === 0) {
            contentList = (res.data.list || []).map(item => ({
              ...item,
              image: this.normalizeImage(item.image)
            }))
          }
          break
          
        case 'collects':
          res = await apiService.getCollects(1, 20)
          if (res.code === 0) {
            contentList = (res.data.list || []).map(item => ({
              ...item,
              image: this.normalizeImage(item.image)
            }))
          }
          break
          
        case 'history':
          res = await apiService.getHistory(1, 20)
          if (res.code === 0) {
            contentList = (res.data.list || []).map(item => ({
              ...item,
              image: this.normalizeImage(item.image)
            }))
          }
          break
          
        default:
          await this.loadCategories()
          if (this.data.categories.length > 0) {
            this.setData({ activeCategoryId: this.data.categories[0].id })
            await this.loadCategoryContent(this.data.categories[0].id)
          }
          return
      }
      
      this.setData({
        currentContent: contentList,
        hasMore: res.data ? res.data.hasMore !== false : false,
        loading: false
      })
      
    } catch (err) {
      console.error('加载数据失败：', err)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
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

  // 加载分类列表
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

  // 加载分类内容
  loadCategoryContent: async function(categoryId, isLoadMore = false) {
    if (this.data.loading) return
    
    this.setData({ loading: true })
    
    try {
      const category = this.data.categories.find(c => c.id === categoryId)
      const page = isLoadMore ? this.data.page : 1
      
      const res = await apiService.getByCategory(categoryId, page)
      if (res.code === 0) {
        const newContent = (res.data.list || []).map(item => ({
          ...item,
          image: this.normalizeImage(item.image)
        }))
        const currentContent = isLoadMore 
          ? [...this.data.currentContent, ...newContent]
          : newContent
        
        this.setData({
          currentContent: currentContent,
          currentCategoryName: category ? category.name : '',
          activeCategoryId: categoryId,
          hasMore: res.data.hasMore !== false,
          page: page + 1,
          loading: false
        })
      }
    } catch (err) {
      console.error('加载分类内容失败：', err)
      this.setData({ loading: false })
    }
  },

  // 切换分类
  switchCategory: function(e) {
    const categoryId = e.currentTarget.dataset.id
    
    this.setData({
      page: 1,
      hasMore: true,
      currentContent: []
    })
    
    this.loadCategoryContent(categoryId)
  },

  // 加载更多
  loadMore: function() {
    if (this.data.type === 'category') {
      if (this.data.hasMore && !this.data.loading) {
        this.loadCategoryContent(this.data.activeCategoryId, true)
      }
    } else {
      if (this.data.hasMore && !this.data.loading) {
        this.loadMoreByType()
      }
    }
  },

  // 加载更多（点赞/收藏/历史）
  loadMoreByType: async function() {
    if (!app.globalData.isLoggedIn) return
    
    this.setData({ loading: true })
    
    try {
      let res
      
      switch(this.data.type) {
        case 'likes':
          res = await apiService.getLikes(this.data.page)
          break
        case 'collects':
          res = await apiService.getCollects(this.data.page)
          break
        case 'history':
          res = await apiService.getHistory(this.data.page)
          break
      }
      
      if (res && res.code === 0) {
        const newContent = (res.data.list || []).map(item => ({
          ...item,
          image: this.normalizeImage(item.image)
        }))
        this.setData({
          currentContent: [...this.data.currentContent, ...newContent],
          hasMore: res.data.hasMore !== false,
          page: this.data.page + 1,
          loading: false
        })
      }
    } catch (err) {
      console.error('加载更多失败：', err)
      this.setData({ loading: false })
    }
  },

  // 跳转到详情
  goToDetail: function(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({
      url: `/pages/work-detail/work-detail?id=${item.id}`
    })
  },

  // 图片加载失败
  onImageError: function(e) {
    const index = e.currentTarget.dataset.index
    if (index !== undefined) {
      const currentContent = this.data.currentContent
      currentContent[index].image = '/images/bg.png'
      this.setData({ currentContent })
    }
  },

  // 触底加载更多
  onReachBottom: function() {
    this.loadMore()
  },

  // 下拉刷新
  onPullDownRefresh: function () {
    this.setData({ page: 1, hasMore: true })
    
    if (this.data.type === 'category') {
      this.loadCategoryContent(this.data.activeCategoryId)
    } else {
      this.loadDataByType(this.data.type)
    }
    
    wx.stopPullDownRefresh()
  }
})
