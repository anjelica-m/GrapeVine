"""
Test module for like API.

Author: Kai Luedemann
Date: 2023-11-16

Copyright 2023 RESTless Clients
Licensed under The MIT License

Sources: 
https://docs.djangoproject.com/en/4.2/
"""

from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.http import urlencode

import uuid
import json

from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Author, PostLike, Post, CommentLike, Comment
from ..serializers import PostLikeSerializer, AuthorSerializer, CommentLikeSerializer

class PostLikeAPITest(APITestCase):
    """Test the PostLike API view."""

    url_name = 'project:api_post_likes'

    @classmethod
    def setUpTestData(cls):
        """Initialize authors and a post."""
        authors = []
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            userid = uuid.uuid4()
            author = Author.objects.create(user=user, displayName=name, id=userid, url=f'http://127.0.0.1:8000/authors/{userid}')
            authors.append(author)
        
        post_data = {
            'content': 'Hello World!',
            'visibility': 'PUBLIC',
            'unlisted': False,
            'published': timezone.now()
        }
        Post.objects.create(**post_data, author=authors[0], title='POST 1')

    def setUp(self):
        """Get authors and comment data."""
        self.alice = Author.objects.get(displayName='Alice')
        self.bob = Author.objects.get(displayName='Bob')
        self.post1 = Post.objects.get(title='POST 1')
        self.like_dict = {
            'author': self.bob,
            'post': self.post1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this post',
        }
        like = PostLike.objects.create(**self.like_dict)
        self.like_json = PostLikeSerializer(like).data
        like.delete()

    def test_get_no_likes(self):
        """Check empty query."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 0)

    def test_get_fields(self):
        """Test the json fields returned."""
        PostLike.objects.create(**self.like_dict)
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

        like = data[0]
        self.assertEqual(like['type'], 'Like')
        self.assertEqual(like['author'], AuthorSerializer(self.bob).data)
        self.assertEqual(like['object'], self.post1.get_url())
        self.assertEqual(like['summary'], self.like_dict['summary'])
        self.assertEqual(like['@context'], self.like_dict['context'])

    def test_get_many_likes(self):
        """Test retrieving a multiple likes."""
        for i in range(3):
            PostLike.objects.create(**self.like_dict)

        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)

    def test_get_author_not_found(self):
        """Test invalid author id."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[uuid.uuid4(), self.post1.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_postid_not_found(self):
        """Test invalid post id."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, uuid.uuid4()])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class CommentLikeAPITest(APITestCase):
    """Test the CommentLike API view."""

    url_name = 'project:api_comment_likes'

    @classmethod
    def setUpTestData(cls):
        """Initialize authors, a post, and a comment."""
        authors = []
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            userid = uuid.uuid4()
            author = Author.objects.create(user=user, displayName=name, id=userid, url=f'http://127.0.0.1:8000/authors/{userid}')
            authors.append(author)
        
        post_data = {
            'content': 'Hello World!',
            'visibility': 'PUBLIC',
            'unlisted': False,
            'published': timezone.now()
        }
        post = Post.objects.create(**post_data, author=authors[0], title='POST 1')
        comment_data = {
            'comment': "Nice post!",
            'post': post,
            'author': authors[1],
            'published': timezone.now()
        }
        Comment.objects.create(**comment_data)

    def setUp(self):
        """Get authors and comment data."""
        self.alice = Author.objects.get(displayName='Alice')
        self.bob = Author.objects.get(displayName='Bob')
        self.post1 = Post.objects.get(title='POST 1')
        self.comment1 = Comment.objects.get(comment='Nice post!')
        self.like_dict = {
            'author': self.bob,
            'comment': self.comment1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this comment',
        }
        like = CommentLike.objects.create(**self.like_dict)
        self.like_json = CommentLikeSerializer(like).data
        like.delete()

    def test_get_no_likes(self):
        """Check empty query."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id, self.comment1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 0)

    def test_get_fields(self):
        """Test the json fields returned."""
        CommentLike.objects.create(**self.like_dict)
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id, self.comment1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

        like = data[0]
        self.assertEqual(like['type'], 'Like')
        self.assertEqual(like['author'], AuthorSerializer(self.bob).data)
        self.assertEqual(like['object'], self.comment1.get_url())
        self.assertEqual(like['summary'], self.like_dict['summary'])
        self.assertEqual(like['@context'], self.like_dict['context'])

    def test_get_many_likes(self):
        """Test retrieving a multiple likes."""
        for i in range(3):
            CommentLike.objects.create(**self.like_dict)

        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id, self.comment1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)

    def test_get_author_not_found(self):
        """Test invalid author id."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[uuid.uuid4(), self.post1.id, self.comment1.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_postid_not_found(self):
        """Test invalid post id."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, uuid.uuid4(), self.comment1.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_commentid_not_found(self):
        """Test invalid comment id."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id, uuid.uuid4()])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class LikedAPITest(APITestCase):
    """Test the Liked API view."""

    url_name = 'project:api_user_liked'

    @classmethod
    def setUpTestData(cls):
        """Initialize authors, a post, and a comment."""
        authors = []
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            userid = uuid.uuid4()
            author = Author.objects.create(user=user, displayName=name, id=userid, url=f'http://127.0.0.1:8000/authors/{userid}')
            authors.append(author)
        
        post_data = {
            'content': 'Hello World!',
            'visibility': 'PUBLIC',
            'unlisted': False,
            'published': timezone.now()
        }
        post = Post.objects.create(**post_data, author=authors[0], title='POST 1')
        comment_data = {
            'comment': "Nice post!",
            'post': post,
            'author': authors[1],
            'published': timezone.now()
        }
        Comment.objects.create(**comment_data)

    def setUp(self):
        """Get authors and comment data."""
        self.alice = Author.objects.get(displayName='Alice')
        self.bob = Author.objects.get(displayName='Bob')
        self.post1 = Post.objects.get(title='POST 1')
        self.comment1 = Comment.objects.get(comment='Nice post!')

    def get_comment_json(self, like_dict):
        """Helper method to get the JSON for a CommentLike"""
        like = CommentLike.objects.create(**like_dict)
        like_json = CommentLikeSerializer(like).data
        like.delete()
        return like_json
    
    def get_post_json(self, like_dict):
        """Helped method to get the JSON for a PostLike"""
        like = PostLike.objects.create(**like_dict)
        like_json = PostLikeSerializer(like).data
        like.delete()
        return like_json

    def test_get_no_likes(self):
        """Check empty query."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data['type'], 'liked')
        self.assertEqual(len(data['items']), 0)

    def test_get_postlike(self):
        """Test getting a postlike."""
        like_dict = {
            'author': self.bob,
            'post': self.post1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this post',
        }
        PostLike.objects.create(**like_dict)
        self.client.force_authenticate(user=self.userObj["Bob"])
        url = reverse(self.url_name, args=[self.bob.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0], self.get_post_json(like_dict))

    def test_get_commentlike(self):
        """Test getting a commentlike."""
        like_dict = {
            'author': self.bob,
            'comment': self.comment1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this comment',
        }
        CommentLike.objects.create(**like_dict)
        self.client.force_authenticate(user=self.userObj["Bob"])
        url = reverse(self.url_name, args=[self.bob.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0], self.get_comment_json(like_dict))

    def test_get_mixed_likes(self):
        """Test retrieving both post and comment likes."""
        post_like_dict = {
            'author': self.bob,
            'post': self.post1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this post',
        }
        PostLike.objects.create(**post_like_dict)

        comment_like_dict = {
            'author': self.bob,
            'comment': self.comment1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this comment',
        }
        CommentLike.objects.create(**comment_like_dict)

        self.client.force_authenticate(user=self.userObj["Bob"])
        url = reverse(self.url_name, args=[self.bob.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['items']), 2)

        # Note: Right now we concatenate with posts first
        self.assertEqual(data['items'][0], self.get_post_json(post_like_dict))
        self.assertEqual(data['items'][1], self.get_comment_json(comment_like_dict))

    def test_get_author_not_found(self):
        """Test invalid author id."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[uuid.uuid4()])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class LikeInboxAPITest(APITestCase):
    """Test posting likes to the inbox."""

    url_name = 'project:inbox_api'

    @classmethod
    def setUpTestData(cls):
        """Initialize authors, a post, and a comment."""
        authors = []
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            userid = uuid.uuid4()
            author = Author.objects.create(user=user, displayName=name, id=userid, url=f'http://127.0.0.1:8000/authors/{userid}')
            authors.append(author)
        
        post_data = {
            'content': 'Hello World!',
            'visibility': 'PUBLIC',
            'unlisted': False,
            'published': timezone.now()
        }
        post = Post.objects.create(**post_data, author=authors[0], title='POST 1')
        comment_data = {
            'comment': "Nice post!",
            'post': post,
            'author': authors[1],
            'published': timezone.now()
        }
        Comment.objects.create(**comment_data)

    def setUp(self):
        """Get authors and comment data."""
        self.alice = Author.objects.get(displayName='Alice')
        self.bob = Author.objects.get(displayName='Bob')
        self.post1 = Post.objects.get(title='POST 1')
        self.comment1 = Comment.objects.get(comment='Nice post!')

    def get_comment_json(self, like_dict):
        """Helper method to get the JSON for a CommentLike"""
        like = CommentLike.objects.create(**like_dict)
        like_json = CommentLikeSerializer(like).data
        like.delete()
        return like_json
    
    def get_post_json(self, like_dict):
        """Helped method to get the JSON for a PostLike"""
        like = PostLike.objects.create(**like_dict)
        like_json = PostLikeSerializer(like).data
        like.delete()
        return like_json
    
    def test_like_post(self):
        """Test liking a post"""
        post_like_dict = {
            'author': self.bob,
            'post': self.post1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this post',
        }
        post_like_json = self.get_post_json(post_like_dict)
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.post(url, post_like_json, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        query = PostLike.objects.filter(**post_like_dict)
        self.assertTrue(query.exists())
    
    def test_like_comment(self):
        """Test liking a comment"""
        like_dict = {
            'author': self.alice,
            'comment': self.comment1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this post',
        }
        like_json = self.get_comment_json(like_dict)
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.bob.id])
        resp = self.client.post(url, like_json, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        query = CommentLike.objects.filter(**like_dict)
        self.assertTrue(query.exists())

    def test_missing_field(self):
        """Test sending a like with a missing field."""
        post_like_dict = {
            'author': self.bob,
            'post': self.post1,
            'context': 'http://127.0.0.1:8000/',
            'summary': 'Bob likes this post',
        }
        post_like_json = self.get_post_json(post_like_dict)
        post_like_json.pop('summary')
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.post(url, post_like_json, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        query = PostLike.objects.filter(**post_like_dict)
        self.assertFalse(query.exists())

    # def test_author_not_found(self):
    #     """Test sending a like from an invalid author."""
    #     post_like_dict = {
    #         'author': self.bob,
    #         'post': self.post1,
    #         'context': 'http://127.0.0.1:8000/',
    #         'summary': 'Bob likes this post',
    #     }
    #     post_like_json = self.get_post_json(post_like_dict)
    #     post_like_json['author'] = {
    #         "type": "author",
    #         "id": "http://127.0.0.1:8000/authors/5a8f27e3-8dec-4060-968d-75fd9b331f8e",
    #         "url": "http://127.0.0.1:8000/authors/5a8f27e3-8dec-4060-968d-75fd9b331f8e",
    #         "host": "http://127.0.0.1:8000/",
    #         "displayName": "ww2",
    #         "github": "https://github.com",
    #         "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    #     }

    #     self.client.force_authenticate(user=self.userObj["Alice"])
    #     url = reverse(self.url_name, args=[self.alice.id])
    #     print(post_like_json)
    #     resp = self.client.post(url, post_like_json, format='json')

    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    #     query = PostLike.objects.filter(**post_like_dict)
    #     self.assertFalse(query.exists())
