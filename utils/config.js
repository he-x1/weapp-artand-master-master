module.exports = {
  // 应用信息
  APP: {
    NAME: '乡村文化传播',
    VERSION: '1.0.0',
    DESCRIPTION: '传承乡村文化，弘扬民族精神'
  },

  // API配置
  API: {
    BASE_URL: 'http://localhost:5000/api',  // ← 你的后端地址
    TIMEOUT: 10000
  },

  // 主题配置（乡村文化风格）
  THEME: {
    PRIMARY_COLOR: '#8B7355',
    SECONDARY_COLOR: '#D4A574',
    ACCENT_COLOR: '#7A9E7E',
    BG_COLOR: '#F5F1E8',
    CARD_BG: '#FFFFFF',
    TEXT_PRIMARY: '#2C2416',
    TEXT_SECONDARY: '#6B5D52',
    TEXT_HINT: '#9B8B7A',
    BORDER_COLOR: '#E8DFD0',
    SUCCESS_COLOR: '#7A9E7E',
    WARNING_COLOR: '#E6A23C',
    ERROR_COLOR: '#F56C6C',
    INFO_COLOR: '#409EFF'
  },

  CATEGORIES: [
    { id: 1, name: '传统手工', icon: 'craft' },
    { id: 2, name: '表演艺术', icon: 'performance' },
    { id: 3, name: '生产技艺', icon: 'production' },
    { id: 4, name: '风物传说', icon: 'legend' },
    { id: 5, name: '人物传说', icon: 'person' },
    { id: 6, name: '节庆习俗', icon: 'festival' },
    { id: 7, name: '民间文学', icon: 'literature' }
  ],

  STORAGE_KEYS: {
    USER_INFO: 'userInfo',
    TOKEN: 'token',
    SEARCH_HISTORY: 'searchHistory',
    USER_PREFERENCE: 'userPreference'
  },

  PAGE_SIZE: 20
}