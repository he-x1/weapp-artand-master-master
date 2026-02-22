// pages/discover/discover.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    systemInfo: {},
    imgList: [
      {
        id: 1,
        url: '/images/candle.png',
        viewCount: 128,
        likeCount: 36,
        collectCount: 35
      },
      {
        id: 2,
        url: '/images/plate.png',
        viewCount: 95,
        likeCount: 24,
        collectCount: 30
      },
      {
        id: 3,
        url: '/images/Cookie_cutter.png',
        viewCount: 210,
        likeCount: 58,
        collectCount: 40
      }
    ],
    imgListTwo: [
      [
        {
          id: 4,
          url: '/images/cup.png',
          viewCount: 76,
          likeCount: 15,
          collectCount: 90
        },
        {
          id: 5,
          url: '/images/New_Year_pictures.png',
          viewCount: 143,
          likeCount: 42,
          collectCount: 20
        }
      ],
      [
        {
          id: 6,
          url: '/images/stamp.png',
          viewCount: 89,
          likeCount: 27,
          collectCount: 3
        },
        {
          id: 7,
          url: '/images/Shadow_puppetry.png',
          viewCount: 165,
          likeCount: 63,
          collectCount: 78
        }
      ]
    ]
  },

  onLoad: function (options) {
    var that = this
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })
    
    // TODO: 从后端加载真实数据
    // this.loadData()
  },

  // 加载数据
  loadData: async function() {
    try {
      const res = await apiService.getRecommend(1, 10)
      if (res.code === 0) {
        // 处理数据
      }
    } catch (err) {
      console.error('加载数据失败：', err)
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

  onPullDownRefresh: function() {
    this.loadData()
    wx.stopPullDownRefresh()
  }
})
