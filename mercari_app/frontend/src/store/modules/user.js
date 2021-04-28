const state = {
    user: '',
    email: '',
    password: '',
  }
    
const getters = {
user: state => state.user,
email: state => state.email,
password: state => state.password,
}

const mutations = {
signUp (state, authInfo) {
    state.user = authInfo.user
    state.email = authInfo.email
    state.password = authInfo.password
},
}

const actions = {
signUp ({ commit }, authInfo) {
    commit('signUp', authInfo)
},
}
  
export default {
namespaced: true,
state,
getters,
actions,
mutations
}