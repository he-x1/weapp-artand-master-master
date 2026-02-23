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
      description: '年画是中国画的一种，始于古代的"门神画"，中国民间艺术之一，亦是常见的民间工艺品之一。',
      summary: '年画是中国民间艺术中的瑰宝，以纸为材料，用剪刀或刻刀剪刻出各种图案，寓意吉祥，寄托美好愿望。',
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
      description: '皮影戏是中国民间古老的传统艺术，始于西汉，兴于唐朝。皮影戏又称"影子戏"或"灯影戏"，是一种以兽皮或纸板做成的人物剪影以表演故事的民间戏剧。',
      summary: '皮影戏是中国古老的民间艺术，以兽皮或纸板剪影表演故事，始于西汉，是中国民间艺术的珍贵遗产。',
      viewCount: 89,
      likeCount: 45,
      collectCount: 28,
      createTime: '2024-01-20',
      tags: ['传统技艺', '表演艺术', '非遗']
    },
    {
      id: 3,
      name: '景泰蓝',
      category: '传统手工',
      categoryId: 1,
      image: '/images/Cookie_cutter.png',
      description: '景泰蓝，中国的著名特种金属工艺品类之一，到明代景泰年间这种工艺技术制作达到了最巅峰，制作出的工艺品最为精美而著名。',
      summary: '景泰蓝是中国著名的特种金属工艺品，以精美的工艺和独特的风格闻名于世，是中华传统工艺的瑰宝。',
      viewCount: 156,
      likeCount: 67,
      collectCount: 45,
      createTime: '2024-02-01',
      tags: ['传统技艺', '金属工艺', '非遗']
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
    { id: 7, name: '民间文学', icon: 'literature', count: 20 }
  ]
}

/**
 * 模拟API方法
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
  getRecommend: async (page = 1, pageSize = 20) => {
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

  // 获取详情
  getDetail: async (id) => {
    await delay()
    const item = mockData.cultures.find(c => c.id === id)
    return {
      code: 0,
      message: 'success',
      data: item || null
    }
  },

  // 搜索
  search: async (keyword) => {
    await delay()
    const results = mockData.cultures.filter(c =>
      c.name.includes(keyword) || c.description.includes(keyword)
    )

    return {
      code: 0,
      message: 'success',
      data: {
        list: results,
        total: results.length,
        page: 1,
        pageSize: 20,
        hasMore: false
      }
    }
  },

  // 根据分类获取内容
  getByCategory: async (categoryId) => {
    await delay()
    const results = mockData.cultures.filter(c => c.categoryId === categoryId)

    return {
      code: 0,
      message: 'success',
      data: {
        list: results,
        total: results.length,
        page: 1,
        pageSize: 20,
        hasMore: false
      }
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
      data: { likeCount: item ? item.likeCount : 0 }
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
      data: { likeCount: item ? item.likeCount : 0 }
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
      data: { collectCount: item ? item.collectCount : 0 }
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
      data: { collectCount: item ? item.collectCount : 0 }
    }
  }
}

module.exports = mockApi
