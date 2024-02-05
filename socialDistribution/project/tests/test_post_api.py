"""
Test module for post API.

Author: Shalomi Hron
Date: 2023-11-16

Copyright 2023 RESTless Clients
Licensed under The MIT License

Sources: 
https://docs.djangoproject.com/en/4.2/
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.http import urlencode

import uuid
import json

from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Author, Post
from ..serializers import AuthorSerializer, PostSerializer

class PostsTest(APITestCase):
    url_name = "project:posts_api"
    
    @classmethod
    def setUpTestData(cls):
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            Author.objects.create(user=user, displayName=name)
            user.is_active = True
            user.save()

    def setUp(self):
        self.alice = Author.objects.get(displayName="Alice")
        self.bob = Author.objects.get(displayName="Bob")
        self.post1data = {'content': 'post #1', 'published': timezone.now()}
        self.post2data = {'content': 'post #2', 'published': timezone.now()}
        self.post1 = Post.objects.create(**self.post1data, author=self.userObj["Alice"].author, title='POST 1')
        self.post2 = Post.objects.create(**self.post2data, author=self.userObj["Alice"].author, title='POST 2')

    def test_get_posts(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.get(url)

        self.assertEqual(resp.data["type"], "posts")
        self.assertEqual(len(resp.data["items"]), 2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_posts_empty(self):
        self.client.force_authenticate(user=self.userObj["Bob"])
        url = reverse(self.url_name, args=[self.bob.id])
        resp = self.client.get(url)

        self.assertEqual(resp.data["type"], "posts")
        self.assertEqual(len(resp.data["items"]), 0)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_methods_posts_unauthorized(self):
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        resp2 = self.client.post(url)
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_posts_page_exists(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        query = {
            'page': 1,
            'size': 1
        }

        url = reverse(self.url_name, args=[self.alice.id])
        url_str = f"{url}?{urlencode(query)}"
        resp = self.client.get(url_str)
        data = json.loads(resp.content)

        self.assertEqual(resp.data["type"], "posts")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["items"]), 1)

    def test_get_posts_page_out_of_bounds(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        query = {
            'page': 4,
            'size': 2
        }

        url = reverse(self.url_name, args=[self.alice.id])
        url_str = f"{url}?{urlencode(query)}"
        resp = self.client.get(url_str)
        data = json.loads(resp.content)

        self.assertEqual(resp.data["detail"], "Invalid page.")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_method(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])

        resp = self.client.put(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp2 = self.client.delete(url)
        self.assertEqual(resp2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_post(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.post(url, self.post1data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        query = Post.objects.filter(**self.post1data)
        self.assertTrue(query.exists())
        self.assertEqual(len(query), 2) # There should be 2 posts total that match post1data

    def test_author_not_found(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        fake_id = uuid.uuid4()
        url = reverse(self.url_name, args=[fake_id])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class SinglePostTest(APITestCase):
    url_name = "project:single_post_api"

    @classmethod
    def setUpTestData(cls):
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            Author.objects.create(user=user, displayName=name)
            user.is_active = True
            user.save()

    def setUp(self):
        self.alice = Author.objects.get(displayName="Alice")
        self.bob = Author.objects.get(displayName="Bob")
        self.post1data = {'content': 'post #1', 'published': timezone.now()}
        self.post2data = {'content': 'post #2', 'published': timezone.now()}
        self.post1 = Post.objects.create(**self.post1data, author=self.userObj["Alice"].author, title='POST 1')
        self.post2 = Post.objects.create(**self.post2data, author=self.userObj["Alice"].author, title='POST 2')

    def test_get_single_post_own_profile(self):
        self.client.force_authenticate(user=self.userObj["Alice"])

        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        self.assertEqual(resp.data["type"], "post")
        self.assertEqual(resp.data["author"]["displayName"], "Alice")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_single_public_post_diff_profile(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        newpost = Post.objects.create(**self.post1data, author=self.userObj["Bob"].author, title='POST 1')

        url = reverse(self.url_name, args=[self.bob.id, newpost.id])
        resp = self.client.get(url)
        self.assertEqual(resp.data["type"], "post")
        self.assertEqual(resp.data["author"]["displayName"], "Bob")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_not_found(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        fake_author_id = uuid.uuid4()
        fake_post_id = uuid.uuid4()

        # Author not found
        url1 = reverse(self.url_name, args=[fake_author_id, self.post1.id])
        resp1 = self.client.get(url1)
        self.assertEqual(resp1.status_code, status.HTTP_404_NOT_FOUND)

        # Post not found
        url2 = reverse(self.url_name, args=[self.alice.id, fake_post_id])
        resp2 = self.client.get(url2)
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_method(self):
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        resp2 = self.client.post(url)
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)
        resp3 = self.client.put(url)
        self.assertEqual(resp3.status_code, status.HTTP_401_UNAUTHORIZED)
        resp4 = self.client.delete(url)
        self.assertEqual(resp4.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_method(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])

        resp = self.client.patch(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_to_create_post(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        new_post_id = uuid.uuid4()
        url = reverse(self.url_name, args=[self.alice.id, new_post_id])

        # The post does not yet exist
        resp1 = self.client.get(url)
        self.assertEqual(resp1.status_code, status.HTTP_404_NOT_FOUND)

        # Create a new post
        new_data = {'content': 'new post', 'published': timezone.now(), 'author': self.alice.id, 'title': 'new post'}
        resp2 = self.client.put(url, new_data, format='json')
        # self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        query = Post.objects.filter(**self.post1data)
        self.assertTrue(query.exists())
        self.assertEqual(len(query), 1)

    def test_post_to_update_post(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        post = Post.objects.get(title="POST 1")
        self.assertEqual(post.content, "post #1") # The initial value before updates

        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        data = {"content": "content content"}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.data["type"], "post")
        self.assertEqual(resp.data["content"], "content content")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_post(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])

        resp1 = self.client.get(url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        resp2 = self.client.delete(url)
        self.assertEqual(resp2.status_code, status.HTTP_204_NO_CONTENT)
        resp3 = self.client.get(url)
        self.assertEqual(resp3.status_code, status.HTTP_404_NOT_FOUND)
        resp4 = self.client.delete(url)
        self.assertEqual(resp4.status_code, status.HTTP_404_NOT_FOUND)
