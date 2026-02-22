// components/culture-card/culture-card.js
Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },

  data: {

  },

  methods: {
    onTap: function() {
      this.triggerEvent('tap', { item: this.properties.item })
    }
  }
})
