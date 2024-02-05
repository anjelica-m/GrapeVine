import { fetchWrapper } from '@/helpers/fetch-wrapper'

export const checkUsername = async (value) => {
  if (!value) {
    return 'Username is required'
  }
  try {
    const response = await fetchWrapper.get(`/api/local/check-username/?username=${value}`)
    const data = await response.json()
    return !data.is_taken
  } catch (error) {
    return false
  }
}

export const signUp = async ({ username, github, password1, password2 }) => {
  // Basic validation
  if (!username || !password1 || !password2) {
    throw new Error('All fields are required')
  }

  const response = await fetchWrapper.post(`/api/local/signup/`, {
    username,
    github,
    password1,
    password2
  })

  if (response.status !== 204) {
    const data = await response.json()
    throw new Error(data.message || 'Error creating user')
  }
}
