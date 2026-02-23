// pages/search/search.js
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    keyword: '',
    historyList: [],
    hotKeywords: ['年画', '皮影戏', '剪纸', '陶瓷', '刺绣', '戏曲'],
    results: [],
    showResults: false,
    loading: false,
    page: 1,
    hasMore: true,
    total: 0
  },

  onLoad: function(options) {
    this.loadHistory()
    if (options.keyword) {
      this.setData({ keyword: options.keyword })
      this.doSearch(options.keyword)
    }
  },

  loadHistory: function() {
    const history = wx.getStorageSync('searchHistory') || []
    this.setData({ historyList: history })
  },

  saveHistory: function(keyword) {
    let history = this.data.historyList.filter(item => item !== keyword)
    history.unshift(keyword)
    if (history.length > 10) history = history.slice(0, 10)
    wx.setStorageSync('searchHistory', history)
    this.setData({ historyList: history })
  },

  onInput: function(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch: function() {
    const keyword = this.data.keyword.trim()
    if (keyword) {
      this.setData({ page: 1, results: [], hasMore: true })
      this.doSearch(keyword)
    }
  },

  doSearch: async function(keyword, isLoadMore = false) {
    if (this.data.loading) return
    
    this.setData({ loading: true, showResults: true })
    
    try {
      const page = isLoadMore ? this.data.page : 1
      const res = await apiService.search(keyword, page)
      
      if (res.code === 0) {
        const newResults = res.data.list || res.data || []
        const results = isLoadMore ? [...this.data.results, ...newResults] : newResults
        
        this.setData({
          results: results,
          total: res.data.total || results.length,
          hasMore: res.data.hasMore !== false,
          page: page + 1
        })
        
        if (!isLoadMore) {
          this.saveHistory(keyword)
        }
      }
    } catch (err) {
      console.error('搜索失败：', err)
      wx.showToast({
        title: '搜索失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  clearKeyword: function() {
    this.setData({ 
      keyword: '', 
      showResults: false, 
      results: [],
      page: 1,
      hasMore: true
    })
  },

  cancelSearch: function() {
    wx.navigateBack()
  },

  searchHistory: function(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword, page: 1, results: [] })
    this.doSearch(keyword)
  },

  searchHot: function(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword, page: 1, results: [] })
    this.doSearch(keyword)
  },

  clearHistory: function() {
    wx.showModal({
      title: '提示',
      content: '确定清空搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('searchHistory')
          this.setData({ historyList: [] })
        }
      }
    })
  },

  goToDetail: function(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({ url: `/pages/work-detail/work-detail?id=${item.id}` })
  },

  // 触底加载更多
  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading && this.data.keyword) {
      this.doSearch(this.data.keyword, true)
    }
  }
})
