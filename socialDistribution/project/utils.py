from django.shortcuts import get_object_or_404

from project.models import *
from project.serializers import PostSerializer

import requests


def update_followers(author):
    for fr in FollowRequest.objects.filter(follower=author):
        following = fr.following
        node = Node.objects.filter(host=following.host)
        if node.count():
            node = node.first()
            url = f"{node.apiURL}/authors/{following.id}/followers/{author.id}"
            auth = (node.nodeName, node.nodeCred)
            resp = requests.get(url, auth=auth)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('isFollower', True) and data:
                    fr.delete()
                    author.following.add(following)


def create_local_post(author_id, post_id):
    author = get_object_or_404(Author, pk=author_id)
    # TODO: Bad url construction
    if "im-a-teapot" in author.host:
        auth = ("teapot", "rooibos")
        url = f"https://im-a-teapot-41db2c906820.herokuapp.com/authors/{author.pk}/posts/{post_id}"
    elif "silk-cmput404" in author.host:
        auth = ("restlessclients", "django100")
        url = f"https://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{author.pk}/posts/{post_id}"
    
    resp = requests.get(url, auth=auth)
    serializer = PostSerializer(data=resp.json())
    if serializer.is_valid():
        return serializer.save()
    return None


def send_to_inbox(obj, recipient, serializer, notification=None):
    data = serializer(instance=obj).data
    # Fix using host as foreign key to node
    node = Node.objects.filter(host=recipient.host)
    if node.count():
        node = node.first()
        url = f"{node.apiURL}authors/{recipient.id}/inbox"
        auth = (node.nodeName, node.nodeCred)
        resp = requests.post(url,json=data, auth=auth)
    else:
        # Would need to check type anyway
        if notification is None:
            recipient.streamPosts.add(obj)
        else:
            Notification.objects.create(**notification)
    return data


def create_post(post_dict, recipient=None):
    post = Post.objects.create(**post_dict)
    update_followers(post.author)
    if post.visibility != Post.VisibilityChoice.PRIVATE:
        for follower in post.author.followers.all():
            send_to_inbox(post, follower, PostSerializer)
    elif recipient is not None:
        send_to_inbox(post, recipient, PostSerializer)
    return post


def addOrGetRemoteAuthor(remoteAuthor):
    if remoteAuthor["host"]=="https://im-a-teapot-41db2c906820.herokuapp.com/":
        index = 5
    elif remoteAuthor["host"]=="https://silk-cmput404-project-21e5c91727a7.herokuapp.com":
        index = 5
    elif remoteAuthor["host"]=="https://restlessclients-7b4ebf6b9382.herokuapp.com/":
        index = 4
        # remoteAuthor["host"]="https://im-a-teapot-41db2c906820.herokuapp.com/"
        # index = 5
    else:
        index = 4
    if remoteAuthor["id"][-1] != '/':
        index = -1
    else:
        index = -2
    # print(remoteAuthor)
    author_id = remoteAuthor["id"].split('/')[index]
    query = Author.objects.filter(pk=author_id)
    # print("p1", remoteAuthor)
    if query.count() == 0:
        user = User.objects.create_user(username=author_id, password="inactive")
        user.is_active = False # This user should remain inactive
        user.save()
        # print("p2", remoteAuthor)

        if (remoteAuthor["profileImage"] is None):
            # TODO: change the default value / avoid hardcoding
            # We don't want to allow null values
            remoteAuthor["profileImage"] = "https://clipart-library.com/img/1331574.jpg" # "https://i.imgur.com/k7XVwpB.jpeg"
        
        author = Author.objects.create(user=user, id=author_id,  url=remoteAuthor["url"],
                host=remoteAuthor["host"], displayName = remoteAuthor["displayName"], github=remoteAuthor["github"],
                profileImage=remoteAuthor["profileImage"])
        return author.save()
    return query.first()


def addOrGetRemotePost(remotePost, author):
    """Fetch a remote post if it does not exist"""
    if remotePost['id'][-1] == '/':
        ind = -2
    else:
        ind = -1
    query = Post.objects.filter(pk=remotePost["id"].split("/")[ind])

    if (remotePost["content"] is None):
            # We don't want to allow null values
            remotePost["content"] = " "

    if query.count() == 0:
        remotePost = Post.objects.create(author=author, title=remotePost["title"],
                id=remotePost["id"].split("/")[ind], source=remotePost["source"], origin=remotePost["origin"],
                description=remotePost["description"], contentType=remotePost["contentType"],
                content=remotePost["content"], categories=remotePost["categories"],
                count=remotePost["count"], published=remotePost["published"],
                visibility=remotePost["visibility"], unlisted=remotePost["unlisted"]
        )
        return remotePost.save()
    return query.first()


def addOrGetRemoteComment(remoteComment, post):
    """Fetch a remote comment if it does not exist"""
    try:
        if remoteComment['id'][-1] == '/':
            ind = -2
        else:
            ind = -1
    except:
        print("bad data: ignored")
        return
    query = Comment.objects.filter(pk=remoteComment["id"].split("/")[ind])
    if query.count() == 0:
        # The author might not exist yet
        author = addOrGetRemoteAuthor(remoteComment['author'])

        remoteComment = Comment.objects.create(author=author, post=post,
                comment=remoteComment["comment"], contentType=remoteComment["contentType"],
                id=remoteComment["id"].split("/")[ind], published=remoteComment["published"]
        )
        return remoteComment.save()
    return query.first()


def addOrGetRemotePostLike(remotePostLike, post):
    """Fetch a remote post like if it does not exist"""
    # Since we do not have access to the postLike's ID, use the summary to check for existance
    query = PostLike.objects.filter(summary=remotePostLike["summary"])

    if query.count() == 0:
        author = addOrGetRemoteAuthor(remotePostLike['author'])

        # Catch badly formatted fields:
        if not("summary" in remotePostLike):
            remotePostLike["summary"] = str(author.displayName) + " likes this"
        if not("context" in remotePostLike):
            remotePostLike["context"] = "http://127.0.0.1:8000/"

        remotePostLike = PostLike.objects.create(author=author, post=post,
                summary=remotePostLike["summary"], context=remotePostLike["context"]#,
        )
        return remotePostLike.save()
    return query.first()


def addOrGetRemoteCommentLike(remoteCommentLike, comment):
    """Fetch a remote comment like if it does not exist"""

    # Since we do not have access to the commentLike's ID, use the summary to check for existance
    query = CommentLike.objects.filter(summary=remoteCommentLike["summary"])

    if query.count() == 0:
        author = addOrGetRemoteAuthor(remoteCommentLike['author'])

        # Catch badly formatted fields:
        if not("summary" in remoteCommentLike):
            remoteCommentLike["summary"] = str(author.displayName) + " likes this"
        if not("context" in remoteCommentLike):
            remoteCommentLike["context"] = "http://127.0.0.1:8000/"

        remoteCommentLike = CommentLike.objects.create(author=author, comment=comment,
                summary=remoteCommentLike["summary"], context=remoteCommentLike["context"]
        )
        return remoteCommentLike.save()
    return query.first()