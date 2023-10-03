import {defineStore} from 'pinia'
import {UserData} from 'src/types/UserData'

export const useUserStore = defineStore('user-store', {
  state: () => {
    return {
      loggedIn: false,
      userData: {} as UserData,
      userDataLoading: false,
      developerMode: false,
    }
  },
  actions: {
    loadUserData() {
      this.userDataLoading = true
      return fetch('/portal/api/userinfo/')
        .then(res => res.json())
        .then(res => {
          if (res.success) {
            this.userData = res.data
            this.loggedIn = true
          }
          // Developer mode is returned regardless of success
          this.developerMode = res.developerMode
        })
        .catch(() => {
          this.userData = null as unknown as UserData
          this.loggedIn = false
        })
        .finally(() => {
          this.userDataLoading = false
        })
    },
    updateName(name: string) {
      this.userData.firstName = name
    }
  },
  getters: {},
})
