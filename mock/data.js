/**
 * 模拟数据模块
 * 用于开发阶段的本地数据模拟
 */

// 模拟延迟
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 模拟数据
 */
const mockData = {
  // 轮播图数据
  banners: [
    {
      id: 1,
      image: '/images/discover/bianzhi.jpg',
      title: '传统编织技艺',
      link: '/pages/work-detail/work-detail?id=1'
    },
    {
      id: 2,
      image: '/images/discover/falang.jpg',
      title: '景泰蓝工艺',
      link: '/pages/work-detail/work-detail?id=2'
    },
    {
      id: 3,
      image: '/images/discover/printing.jpg',
      title: '传统印刷术',
      link: '/pages/work-detail/work-detail?id=3'
    }
  ],

  // 乡村文化内容列表
  cultures: [
    {
      id: 1,
      name: '年画',
      category: '传统手工',
      categoryId: 1,
      image: '/images/New_Year_pictures.png',
      description: '年画是中国画的一种，始于古代的“门神画”，中国民间艺术之一，亦是常见的民间工艺品之一。',
      viewCount: 128,
      likeCount: 36,
      collectCount: 35,
      createTime: '2024-01-15',
      tags: ['传统技艺', '民间艺术', '新年']
    },
    {
      id: 2,
      name: '皮影戏',
      category: '表演艺术',
      categoryId: 2,
      image: '/images/Shadow_puppetry.png',
      description: '皮影戏是中国民间古老的传统艺术，老北京人都叫它“驴皮影”。据史书记载，皮影戏始于西汉，兴于唐朝，盛于清代，元代时期传至西亚和欧洲。',
      viewCount: 95,
      likeCount: 24,
      collectCount: 30,
      createTime: '2024-01-20',
      tags: ['传统艺术', '民间表演', '非遗']
    },
    {
      id: 3,
      name: '剪纸',
      category: '传统手工',
      categoryId: 1,
      image: '/images/Cookie_cutter.png',
      description: '中国剪纸是一种用剪刀或刻刀在纸上剪刻花纹，用于装点生活或配合民俗活动的民间艺术。',
      viewCount: 210,
      likeCount: 58,
      collectCount: 40,
      createTime: '2024-02-01',
      tags: ['传统手工', '民间艺术', '装饰']
    },
    {
      id: 4,
      name: '陶瓷技艺',
      category: '生产技艺',
      categoryId: 3,
      image: '/images/cup.png',
      description: '陶瓷是陶器和瓷器的总称，中国人早在约公元前8000－2000年（新石器时代）就发明了陶器。',
      viewCount: 76,
      likeCount: 15,
      collectCount: 90,
      createTime: '2024-02-05',
      tags: ['传统技艺', '陶瓷', '工艺']
    },
    {
      id: 5,
      name: '印章篆刻',
      category: '传统手工',
      categoryId: 1,
      image: '/images/stamp.png',
      description: '篆刻艺术，是书法（主要是篆书）和镌刻（包括凿、铸）结合，来制作印章的艺术，是汉字特有的艺术形式。',
      viewCount: 143,
      likeCount: 42,
      collectCount: 20,
      createTime: '2024-02-10',
      tags: ['传统技艺', '书法', '艺术']
    },
    {
      id: 6,
      name: '彩碟',
      category: '传统手工',
      categoryId: 1,
      image: '/images/plate.png',
      description: '彩碟是一种传统的民间手工艺品，以其精美的图案和独特的工艺著称。',
      viewCount: 89,
      likeCount: 27,
      collectCount: 3,
      createTime: '2024-02-12',
      tags: ['传统工艺', '装饰艺术']
    },
    {
      id: 7,
      name: '蜡染技艺',
      category: '传统手工',
      categoryId: 1,
      image: '/images/candle.png',
      description: '蜡染是我国古老的少数民族民间传统纺织印染手工艺，古称蜡，与绞缬（扎染）、夹缬（镂空印花）并称为我国古代三大印花技艺。',
      viewCount: 165,
      likeCount: 63,
      collectCount: 78,
      createTime: '2024-02-15',
      tags: ['传统技艺', '印染', '非遗']
    }
  ],

  // 分类数据
  categories: [
    { id: 1, name: '传统手工', icon: 'craft', count: 45 },
    { id: 2, name: '表演艺术', icon: 'performance', count: 23 },
    { id: 3, name: '生产技艺', icon: 'production', count: 18 },
    { id: 4, name: '风物传说', icon: 'legend', count: 32 },
    { id: 5, name: '人物传说', icon: 'person', count: 28 },
    { id: 6, name: '节庆习俗', icon: 'festival', count: 15 },
    { id: 7, name: '民间文学', icon: 'literature', count: 36 }
  ]
}

/**
 * 模拟API响应
 */
const mockApi = {
  // 获取轮播图
  getBanners: async () => {
    await delay()
    return {
      code: 0,
      message: 'success',
      data: mockData.banners
    }
  },

  // 获取推荐内容
  getRecommend: async (page = 1, pageSize = 10) => {
    await delay()
    const start = (page - 1) * pageSize
    const end = start + pageSize
    const list = mockData.cultures.slice(start, end)
    
    return {
      code: 0,
      message: 'success',
      data: {
        list: list,
        total: mockData.cultures.length,
        page: page,
        pageSize: pageSize,
        hasMore: end < mockData.cultures.length
      }
    }
  },

  // 获取内容详情
  getDetail: async (id) => {
    await delay()
    const item = mockData.cultures.find(c => c.id === id)
    
    if (!item) {
      return {
        code: 404,
        message: '内容不存在',
        data: null
      }
    }
    
    return {
      code: 0,
      message: 'success',
      data: item
    }
  },

  // 搜索内容
  search: async (keyword) => {
    await delay()
    const results = mockData.cultures.filter(c => 
      c.name.includes(keyword) || 
      c.category.includes(keyword) ||
      c.tags.some(tag => tag.includes(keyword))
    )
    
    return {
      code: 0,
      message: 'success',
      data: results
    }
  },

  // 根据分类获取内容
  getByCategory: async (categoryId) => {
    await delay()
    const results = mockData.cultures.filter(c => c.categoryId === categoryId)
    
    return {
      code: 0,
      message: 'success',
      data: results
    }
  },

  // 获取分类列表
  getCategories: async () => {
    await delay()
    return {
      code: 0,
      message: 'success',
      data: mockData.categories
    }
  },

  // 点赞
  like: async (id) => {
    await delay(200)
    const item = mockData.cultures.find(c => c.id === id)
    if (item) {
      item.likeCount++
    }
    
    return {
      code: 0,
      message: 'success',
      data: { likeCount: item.likeCount }
    }
  },

  // 取消点赞
  unlike: async (id) => {
    await delay(200)
    const item = mockData.cultures.find(c => c.id === id)
    if (item && item.likeCount > 0) {
      item.likeCount--
    }
    
    return {
      code: 0,
      message: 'success',
      data: { likeCount: item.likeCount }
    }
  },

  // 收藏
  collect: async (id) => {
    await delay(200)
    const item = mockData.cultures.find(c => c.id === id)
    if (item) {
      item.collectCount++
    }
    
    return {
      code: 0,
      message: 'success',
      data: { collectCount: item.collectCount }
    }
  },

  // 取消收藏
  uncollect: async (id) => {
    await delay(200)
    const item = mockData.cultures.find(c => c.id === id)
    if (item && item.collectCount > 0) {
      item.collectCount--
    }
    
    return {
      code: 0,
      message: 'success',
      data: { collectCount: item.collectCount }
    }
  }
}

module.exports = mockApi
