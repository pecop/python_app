<template>
  <div class="search container">
    <div :class="messageClass" role="alert">
      {{ message }}
    </div>
    <button @click="search" class="btn btn-primary">検索</button>
  </div>
</template>

<script>
export default {
  name: 'Search',
  data() {
    return {
      message: '検索条件を入力、選択し、検索ボタンを押して下さい。',
      messageClass: 'alert alert-warning'
    }
  },
  methods: {
    search() {
      eel.search()((message) => {
        this.message = message
        this.messageClass = 'alert alert-success'
      })
    },
  }
}

</script>