// components/search-bar/search-bar.js
Component({
  properties: {
    placeholder: {
      type: String,
      value: '搜索乡村文化...'
    },
    value: {
      type: String,
      value: ''
    },
    showButton: {
      type: Boolean,
      value: false
    }
  },

  data: {

  },

  methods: {
    onInput: function(e) {
      const value = e.detail.value
      this.setData({ value })
      this.triggerEvent('input', { value })
    },

    onConfirm: function() {
      this.triggerEvent('search', { value: this.data.value })
    },

    onClear: function() {
      this.setData({ value: '' })
      this.triggerEvent('clear')
      this.triggerEvent('input', { value: '' })
    }
  }
})
