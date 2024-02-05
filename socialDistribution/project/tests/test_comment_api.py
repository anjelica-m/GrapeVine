"""
Test module for comment API.

Author: Kai Luedemann
Date: 2023-11-16

Copyright 2023 RESTless Clients
Licensed under The MIT License

Sources:
https://docs.djangoproject.com/en/4.2/
https://stackoverflow.com/questions/4995279/including-a-querystring-in-a-django-core-urlresolvers-reverse-call
"""

from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.http import urlencode

import uuid
import json

from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Author, Comment, Post
from ..serializers import CommentSerializer, AuthorSerializer

class CommentAPITest(APITestCase):
    """Test the Comment API view."""

    url_name = 'project:comment_api'

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
        self.comm_dict = {
            'author': self.bob,
            'comment': 'test',
            'post': self.post1,
            'published': timezone.now(),
            'contentType': 'a'
        }
        comm = Comment.objects.create(**self.comm_dict)
        self.comm_json = CommentSerializer(comm).data
        comm.delete()

    def test_get_no_comments(self):
        """Check empty query."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['comments']), 0)
        self.assertEqual(data['page'], 1)

    def test_get_fields(self):
        """Test the json fields returned."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        Comment.objects.create(**self.comm_dict)
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['type'], 'comments')
        self.assertEqual(data['page'], 1)

        post_url = self.post1.get_url()
        self.assertEqual(data['post'], post_url)
        self.assertEqual(data['id'], f"{post_url}/comments")

    def test_get_full_page(self):
        """Test retrieving a full page."""
        for i in range(3):
            Comment.objects.create(**self.comm_dict)
        query = {
            'page': 1,
            'size': 2
        }

        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        url_str = f"{url}?{urlencode(query)}"
        resp = self.client.get(url_str)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['comments']), 2)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['size'], 2)

    def test_get_last_page(self):
        """Test retrieving a non-full page."""
        for i in range(3):
            Comment.objects.create(**self.comm_dict)
        query = {
            'page': 2,
            'size': 2
        }

        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        url_str = f"{url}?{urlencode(query)}"
        resp = self.client.get(url_str)
        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['page'], 2)
        self.assertEqual(data['size'], 2)

    def test_post_valid_comment(self):
        """Check that a valid comment is posted."""
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.post(url, self.comm_json, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        query = Comment.objects.filter(**self.comm_dict)
        self.assertTrue(query.exists())

    def test_post_missing_field(self):
        """Test that a missing field results in status code 400"""
        data = {
            **self.comm_json
        }
        data.pop('comment')
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        query = Comment.objects.filter(**self.comm_dict)
        self.assertFalse(query.exists())

    def test_post_wrong_type(self):
        """Test invalid object type."""
        data = {
            **self.comm_json,
            'type': 'like'
        }
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        query = Comment.objects.filter(**self.comm_dict)
        self.assertFalse(query.exists())

    def test_post_author_not_found(self):
        """Test comment author not in database. 
        Note: May want to change implementation to create author instead"""
        data = {
            **self.comm_json,
            'author': {
                "type": "author",
                "id": "http://127.0.0.1:8000/authors/5a8f27e3-8dec-4060-968d-75fd9b331f8e",
                "url": "http://127.0.0.1:8000/authors/5a8f27e3-8dec-4060-968d-75fd9b331f8e",
                "host": "http://127.0.0.1:8000/",
                "displayName": "ww2",
                "github": "",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            }
        }
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        query = Comment.objects.filter(**self.comm_dict)
        self.assertFalse(query.exists())

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

    def test_post_same_author(self):
        """Test commenting on your own post."""
        data = {
            **self.comm_json,
            'author': AuthorSerializer(self.alice).data
        }
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        test = {
            **self.comm_dict,
            'author': self.alice
        }
        query = Comment.objects.filter(**test)
        self.assertTrue(query.exists())

    def test_post_duplicate_comment(self):
        """Test writing a duplicate comment"""
        Comment.objects.create(**self.comm_dict)
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id, self.post1.id])
        resp = self.client.post(url, self.comm_json, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        query = Comment.objects.filter(**self.comm_dict)
        self.assertTrue(query.count(), 2)
        