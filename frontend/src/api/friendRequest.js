import { fetchWrapper } from '@/helpers/fetch-wrapper'

export const fetchFriendRequests = async () => {
  const url = `/api/local/follow-requests/`

  const response = await fetchWrapper.get(url)
  if (!response.ok) {
    throw new Error('Error fetching friend requests')
  }
  return await response.json()
}

export const acceptFriendRequest = async (frId) => {
  const url = `/api/local/follow-requests/${frId}/accept/`
  const response = await fetchWrapper.post(url, null)
  if (!response.ok) {
    throw new Error('Error accepting friend request')
  }
}

export const declineFriendRequest = async (frId) => {
  const url = `/api/local/follow-requests/${frId}/decline/`
  const response = await fetchWrapper.post(url, null)
  if (!response.ok) {
    throw new Error('Error rejecting friend request')
  }
}

export const requestFollowAuthor = async (authorId) => {
  const url = `/authors/${authorId}/follow/`
  const response = await fetchWrapper.post(url, { summary: '' })
  if (!response.ok) {
    throw new Error('Error sending friend request')
  }
}

export const unfollowAuthor = async (authorId) => {
  const url = `/api/local/authors/${authorId}/unfollow/`
  const response = await fetchWrapper.post(url, null)
  if (!response.ok) {
    throw new Error('Error unfollowing author')
  }
}
