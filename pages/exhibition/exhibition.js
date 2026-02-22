// pages/exhibition/exhibition.js
var app = getApp()
var apiService = require('../../utils/apiService.js')

Page({
  data: {
    systemInfo: {},
    categories: [
      { id: 1, name: '传统手工', count: 45 },
      { id: 2, name: '表演艺术', count: 23 },
      { id: 3, name: '生产技艺', count: 18 },
      { id: 4, name: '风物传说', count: 32 },
      { id: 5, name: '人物传说', count: 28 },
      { id: 6, name: '节庆习俗', count: 15 },
      { id: 7, name: '民间文学', count: 36 }
    ],
    categoryContents: {
      1: [
        { id: 101, name: '年画', category: '传统手工', image: '/images/New_Year_pictures.png', viewCount: 128, likeCount: 36, description: '年画是中国画的一种，始于古代的“门神画”，中国民间艺术之一。' },
        { id: 102, name: '剪纸', category: '传统手工', image: '/images/Cookie_cutter.png', viewCount: 210, likeCount: 58, description: '中国剪纸是一种用剪刀或刻刀在纸上剪刻花纹的民间艺术。' },
        { id: 103, name: '印章', category: '传统手工', image: '/images/stamp.png', viewCount: 89, likeCount: 27, description: '篆刻艺术，是书法和镌刻结合来制作印章的艺术。' },
        { id: 104, name: '蜡染', category: '传统手工', image: '/images/candle.png', viewCount: 165, likeCount: 63, description: '蜡染是我国古老的少数民族民间传统纺织印染手工艺。' },
        { id: 105, name: '彩碟', category: '传统手工', image: '/images/plate.png', viewCount: 95, likeCount: 24, description: '彩碟是一种传统的民间手工艺品，以精美的图案和独特的工艺著称。' }
      ],
      2: [
        { id: 201, name: '皮影戏', category: '表演艺术', image: '/images/Shadow_puppetry.png', viewCount: 143, likeCount: 42, description: '皮影戏是中国民间古老的传统艺术，始于西汉，兴于唐朝，盛于清代。' },
        { id: 202, name: '戏曲', category: '表演艺术', image: '/images/cup.png', viewCount: 76, likeCount: 15, description: '中国传统戏曲是包含文学、音乐、舞蹈、美术、武术、杂技的综合艺术。' }
      ],
      3: [
        { id: 301, name: '陶瓷技艺', category: '生产技艺', image: '/images/cup.png', viewCount: 98, likeCount: 32, description: '陶瓷是陶器和瓷器的总称，中国人早在新石器时代就发明了陶器。' }
      ],
      4: [
        { id: 401, name: '民间传说', category: '风物传说', image: '/images/discover/image_preson@2x.png', viewCount: 156, likeCount: 45, description: '民间传说是民间文学的一种重要形式，反映了劳动人民的愿望和要求。' }
      ],
      5: [
        { id: 501, name: '历史人物', category: '人物传说', image: '/images/discover/image_read@2x.png', viewCount: 112, likeCount: 38, description: '历史人物传说是对历史人物的生平事迹进行艺术加工的传说故事。' }
      ],
      6: [
        { id: 601, name: '春节习俗', category: '节庆习俗', image: '/images/New_Year_pictures.png', viewCount: 234, likeCount: 78, description: '春节是中国最富有特色的传统节日，有着丰富的文化内涵。' }
      ],
      7: [
        { id: 701, name: '民歌民谣', category: '民间文学', image: '/images/discover/image_appreciate@2x.png', viewCount: 145, likeCount: 52, description: '民歌民谣是人民群众在生活实践中创作的诗歌，具有鲜明的民族特色。' }
      ]
    },
    activeCategoryId: 1,
    currentContent: [],
    currentCategoryName: '传统手工'
  },

  onLoad: function (options) {
    var that = this
    
    // 获取设备信息
    app.getSystemInfo(function(res) {
      that.setData({
        systemInfo: res
      })
    })

    // 如果有传入分类ID
    if (options.categoryId) {
      const categoryId = parseInt(options.categoryId)
      const category = this.data.categories.find(c => c.id === categoryId)
      this.setData({
        activeCategoryId: categoryId,
        currentCategoryName: category ? category.name : '传统手工'
      })
    }

    // 初始化显示第一个分类的内容
    this.setData({
      currentContent: this.data.categoryContents[this.data.activeCategoryId]
    })
    
    // TODO: 从后端加载真实数据
    // this.loadCategories()
    // this.loadCategoryContent(this.data.activeCategoryId)
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
  loadCategoryContent: async function(categoryId) {
    try {
      const res = await apiService.getByCategory(categoryId)
      if (res.code === 0) {
        this.setData({
          currentContent: res.data
        })
      }
    } catch (err) {
      console.error('加载分类内容失败：', err)
    }
  },

  // 切换分类
  switchCategory: function(e) {
    const categoryId = e.currentTarget.dataset.id
    const category = this.data.categories.find(c => c.id === categoryId)
    
    this.setData({
      activeCategoryId: categoryId,
      currentContent: this.data.categoryContents[categoryId],
      currentCategoryName: category ? category.name : '传统手工'
    })
    
    // TODO: 从后端加载
    // this.loadCategoryContent(categoryId)
  },

  // 加载更多
  loadMore: function() {
    console.log('触发加载更多')
    // TODO: 实现加载更多逻辑
  },

  // 跳转到详情
  goToDetail: function(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({
      url: `/pages/work-detail/work-detail?id=${item.id}&name=${item.name}`
    })
  },

  onPullDownRefresh: function () {
    wx.stopPullDownRefresh()
  }
})
