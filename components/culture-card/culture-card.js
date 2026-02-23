// components/culture-card/culture-card.js
Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },

  data: {
    defaultImage: '/images/class_white.png',
    currentImage: ''
  },

  observers: {
    'item.image': function(image) {
      // 当图片URL变化时，更新当前图片
      this.setData({
        currentImage: image || this.data.defaultImage
      })
    }
  },

  lifetimes: {
    attached: function() {
      // 初始化图片
      this.setData({
        currentImage: this.properties.item.image || this.data.defaultImage
      })
    }
  },

  methods: {
    onTap: function() {
      this.triggerEvent('tap', { item: this.properties.item })
    },

    onImageError: function() {
      // 图片加载失败时，使用默认图片
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
