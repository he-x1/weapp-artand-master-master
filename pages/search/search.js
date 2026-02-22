// pages/search/search.js
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    keyword: '',
    historyList: [],
    hotKeywords: ['年画', '皮影戏', '剪纸', '陶瓷', '刺绣', '戏曲'],
    results: [],
    showResults: false,
    loading: false
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
    if (keyword) this.doSearch(keyword)
  },

  doSearch: async function(keyword) {
    this.setData({ loading: true, showResults: true })
    try {
      const res = await apiService.search(keyword)
      if (res.code === 0) {
        this.setData({ results: res.data })
        this.saveHistory(keyword)
      }
    } catch (err) {
      console.error('搜索失败：', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  clearKeyword: function() {
    this.setData({ keyword: '', showResults: false, results: [] })
  },

  cancelSearch: function() {
    wx.navigateBack()
  },

  searchHistory: function(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.doSearch(keyword)
  },

  searchHot: function(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
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
  }
})
