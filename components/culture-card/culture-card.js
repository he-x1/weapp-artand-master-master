Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },

  data: {
    defaultImage: '/images/bg.png',
    currentImage: ''
  },

  observers: {
    'item.image': function(image) {
      this.setData({
        currentImage: this.normalizeImage(image)
      })
    }
  },

  lifetimes: {
    attached: function() {
      this.setData({
        currentImage: this.normalizeImage(this.properties.item.image)
      })
    }
  },

  methods: {
    // 标准化图片URL
    normalizeImage: function(image) {
      if (!image) {
        return this.data.defaultImage
      }
      // 如果是本地路径且以/images/开头，保持不变
      // 小程序会自动从项目根目录查找
      if (image.startsWith('/images/')) {
        return image
      }
      // 如果是网络图片，直接返回
      if (image.startsWith('http')) {
        return image
      }
      // 其他情况使用默认图片
      return this.data.defaultImage
    },

    onTap: function() {
      this.triggerEvent('tap', { item: this.properties.item })
    },

    onImageError: function(e) {
      console.warn('图片加载失败:', this.properties.item.image)
      this.setData({
        currentImage: this.data.defaultImage
      })
    },

    onImageLoad: function() {
      // 图片加载成功
    }
  }
})
