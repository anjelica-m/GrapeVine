const formatPullRequestReviewCommentEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  const url = e.payload.comment.html_url
  return `${user} added <a href="${url}">comment</a> to pull request to ${repoName}`
}

const formatPullRequestEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  const action = e.payload.action
  const url = e.payload.pull_request.html_url
  return `${user} ${action} <a href="${url}">pull request</a> on ${repoName}`
}

const formatIssueCommentEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  const action = e.payload.action
  const url = e.payload.comment.html_url
  return `${user} ${action} <a href="${url}">issue comment</a> on ${repoName}`
}

const formatPushEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  return `${user} pushed to <a href="${e.repo.url}">${repoName}</a>`
}

const formatWatchEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  const action = e.payload.action
  return `${user} ${action} watching repo <a href="${e.repo.url}">${repoName}</a>`
}

const formatForkEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  return `${user} forked repo <a href="${e.repo.url}">${repoName}</a>`
}

const formatPublicEvent = (e) => {
  const user = e.actor.login
  const repoName = e.repo.name
  return `${user} published repo <a href="${e.repo.url}">${repoName}</a>`
}

const formatMemberEvent = (e) => {
  const user = e.actor.login
  const action = e.payload.action
  const member = e.payload.member.login
  const repoName = e.repo.name
  return `${user} ${action} ${member} to repo <a href="${e.repo.url}">${repoName}</a>`
}

const eventHandlers = {
  PullRequestReviewCommentEvent: formatPullRequestReviewCommentEvent,
  PullRequestEvent: formatPullRequestEvent,
  IssueCommentEvent: formatIssueCommentEvent,
  PushEvent: formatPushEvent,
  WatchEvent: formatWatchEvent,
  ForkEvent: formatForkEvent,
  PublicEvent: formatPublicEvent,
  MemberEvent: formatMemberEvent
}

export const formatEvent = (e) => {
  const eventType = e.type
  const handler = eventHandlers[eventType]
  if (handler) {
    return handler(e)
  }
}
