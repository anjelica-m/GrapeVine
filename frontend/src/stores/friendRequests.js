import { defineStore } from 'pinia'
import { acceptFriendRequest, declineFriendRequest, fetchFriendRequests } from '@/api/friendRequest'

export const useFriendRequests = defineStore('friendRequests', {
  state: () => {
    return {
      friendRequests: []
    }
  },

  actions: {
    async setup() {
      this.friendRequests = await this.loadFriendRequests()
    },
    async accept(frId) {
      await acceptFriendRequest(frId)
      this.friendRequests = this.friendRequests.filter((request) => request.id !== frId)
    },
    async decline(frId) {
      await declineFriendRequest(frId)
      this.friendRequests = this.friendRequests.filter((request) => request.id !== frId)
    },
    async loadFriendRequests() {
      this.friendRequests = await fetchFriendRequests()
    }
  }
})
