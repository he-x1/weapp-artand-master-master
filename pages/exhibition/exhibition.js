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
    type: 'category', // category, likes, collects, history
    title: ''
  },

  onLoad: function (options) {
    var that = this
    
    // 获取设备信息
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })

    // 根据参数决定加载类型
    if (options.type) {
      const type = options.type
      const title = options.title || ''
      
      this.setData({
        type: type,
        title: title
      })
      
      // 设置页面标题
      if (title) {
        wx.setNavigationBarTitle({ title: title })
      }
      
      // 加载对应类型的数据
      this.loadDataByType(type)
    } else if (options.categoryId) {
      // 分类浏览模式
      const categoryId = parseInt(options.categoryId)
      this.setData({
        type: 'category',
        activeCategoryId: categoryId
      })
      this.loadCategories().then(() => {
        this.loadCategoryContent(categoryId)
      })
    } else {
      // 默认加载所有分类
      this.loadCategories().then(() => {
        if (this.data.categories.length > 0) {
          this.setData({ activeCategoryId: this.data.categories[0].id })
          this.loadCategoryContent(this.data.categories[0].id)
        }
      })
    }
  },

  // 根据类型加载数据
  loadDataByType: async function(type) {
    this.setData({ loading: true })
    
    try {
      let res
      let contentList = []
      
      switch(type) {
        case 'likes':
          res = await apiService.getLikes(this.data.page)
          if (res.code === 0) {
            contentList = res.data.list || []
          }
          break
          
        case 'collects':
          res = await apiService.getCollects(this.data.page)
          if (res.code === 0) {
            contentList = res.data.list || []
          }
          break
          
        case 'history':
          res = await apiService.getHistory(this.data.page)
          if (res.code === 0) {
            contentList = res.data.list || []
          }
          break
          
        default:
          // 分类模式
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
        const newContent = res.data.list || []
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
    
    // 重置页码
    this.setData({
      page: 1,
      hasMore: true
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
        const newContent = res.data.list || []
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

  // 触底加载更多
  onReachBottom: function() {
    this.loadMore()
  },

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
