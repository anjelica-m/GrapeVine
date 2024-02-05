import { fetchWrapper } from '@/helpers/fetch-wrapper'

export const createPost = async (postData) => {
  const url = `/api/local/posts/`

  try {
    const response = await fetchWrapper.post(url, postData)
    if (!response.ok) {
      throw new Error('Network response was not ok.')
    }
    return await response.json()
  } catch (error) {
    // Handle or throw the error as per your application's error handling logic
    console.error('Error while creating post:', error)
    throw error
  }
}

export const updatePost = async (postId, postData) => {
  const url = `/api/local/posts/${postId}/`
  const response = await fetchWrapper.put(url, postData)
  if (!response.ok) {
    throw new Error('Network response was not ok.')
  }
  return await response.json()
}

export const fetchNotifs = async (authorId) => {
  const url = `/api/authors/${authorId}/notifications`

  const response = await fetchWrapper.get(url);
  if (!response.ok) {
    throw new Error('Error fetching posts')
  }
  return await response.json(); 
}

export const fetchInbox = async (authorId) => {
  const url = `/api/authors/${authorId}/inbox`

  const response = await fetchWrapper.get(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error('Error fetching posts')
  }
  return data.items;
}

export const fetchPost = async (postId) => {
  const url = `/api/local/posts/${postId}`

  const response = await fetchWrapper.get(url)
  if (!response.ok) {
    throw new Error('Error fetching posts')
  }
  return await response.json()
}

export const deletePost = async (postId) => {
  const url = `/api/local/posts/${postId}`;

  const response = await fetchWrapper.delete(url);
  if (!response.ok) {
    throw new Error('Error deleting posts');
  }
}

export const likePost = async (postId) => {
  const url = `/api/local/posts/${postId}/like/`

  const response = await fetchWrapper.post(url)
  if (!response.ok) {
    throw new Error('Error liking posts')
  }
}

export const unlikePost = async (postId) => {
  const url = `/api/local/posts/${postId}/unlike/`

  const response = await fetchWrapper.post(url)
  if (!response.ok) {
    throw new Error('Error unliking posts')
  }
}

export const sharePost = async (post) => {
  const url = `/api/posts/${post.id}/share`

  const response = await fetchWrapper.post(url, post)
  if (!response.ok) {
    throw new Error('Error sharing post')
  }
}

export const fetchComments = async (postId) => {
  const url = `/api/local/posts/${postId}/comments/`

  const response = await fetchWrapper.get(url)
  if (!response.ok) {
    throw new Error('Error unliking posts')
  }
  return await response.json()
}

export const createComment = async (authorId, postId, text) => {
  const url = `/api/authors/${authorId}/posts/${postId}/create_comment`

  const response = await fetchWrapper.post(url, { comment: text })
  if (!response.ok) {
    throw new Error('Error unliking posts')
  }
  return await response.json()
}

export const likeComment = async (postId) => {
  const url = `/api/local/comments/${postId}/like/`

  const response = await fetchWrapper.post(url)
  if (!response.ok) {
    throw new Error('Error liking comment')
  }
}

export const unlikeComment = async (postId) => {
  const url = `/api/local/comments/${postId}/unlike/`

  const response = await fetchWrapper.post(url)
  if (!response.ok) {
    throw new Error('Error unliking comment')
  }
}

import { Parser, HtmlRenderer } from 'commonmark'

export const getMarkdownHTML = function (data) {
  const reader = new Parser()
  const writer = new HtmlRenderer({ safe: true })
  const parsed = reader.parse(data)
  const result = writer.render(parsed)
  return result
}