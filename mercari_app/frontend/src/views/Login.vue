<template>
  <div class="login">
    <img class="logo" alt="Mercari logo" src="../assets/mercari.png">

    <div class="container">
      <div v-if="isError" class="alert alert-danger" role="alert">
        {{ alertMessage }}
      </div>
      <form method="post" @submit.prevent="signUp">
        <h1 class="my-5">ログイン</h1>
        <div class="form-group row justify-content-center m-0 mb-2">
            <label for="email" class="col-3 col-form-label">メールアドレス</label>
            <div class="col-5">
                <input type="email" name="email" id="email" class="form-control" v-model="email" placeholder="vue@firebase.com">
            </div>
        </div>
        <div class="form-group row justify-content-center m-0 mb-2">
            <label for="password" class="col-3 col-form-label">パスワード</label>
            <div class="col-5">
                <input type="password" name="password" id="password" class="form-control" v-model="password" autocomplete="off" placeholder="6文字以上">
            </div>
        </div>
        <button class="btn btn-primary btn-lg my-3">ログイン</button>
      </form>
    </div>
  </div>
</template>

<script>
import firebase from 'firebase/app'
import 'firebase/auth'

export default {
  name: 'Signup',
  data() {
    return {
      user: '',
      email: '',
      password: '',
      alertMessage: '',
      isError: false,
    }
  },

  methods: {
    signUp() {
      firebase.auth().createUserWithEmailAndPassword(this.email, this.password)
      .then((response) => {
        // response.user.updateProfile({
        //   displayName: this.user
        // })
        const authInfo = {
          user: this.user,
          email: this.email,
          password: this.password,
        }

        this.$store.dispatch('user/signUp', authInfo)
        this.$router.push('/search')

      })
      .catch(error => {
        this.alertMessage = error.message
        this.isError = true
      });
    }
  }
}
</script>

<style scoped>
.logo {
  width: 50%;
}
</style>