import {defineStore} from "pinia";

interface UserData {
  username: string
  firstName: string
  lastName: string
  isAdmin: boolean
}

export const useUserStore = defineStore("user-store", {
  state: () => {
    return {
      loggedIn: false,
      userData: {} as UserData,
      userDataLoading: false,
    }
  },
  actions: {
    loadUserData() {
      this.userDataLoading = true
      return fetch("/portal/api/userinfo/")
        .then(res => res.json())
        .then(res => {
          if (res.success) {
            this.userData = res.data
            this.loggedIn = true
          }
        })
        .catch(() => {
          this.userData = null as unknown as UserData
          this.loggedIn = false
        })
        .finally(() => {
          this.userDataLoading = false
        })
    }
  },
  getters: {}
})
