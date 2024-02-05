"""
Test module for author API.

Author: Shalomi Hron
Date: 2023-11-16

Copyright 2023 RESTless Clients
Licensed under The MIT License

Sources: 
https://docs.djangoproject.com/en/4.2/
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlencode

import uuid
import json

from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Author
from ..serializers import AuthorSerializer

class AuthorsTest(APITestCase):
    url_name = "project:get_authors"
    
    @classmethod
    def setUpTestData(cls):
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            Author.objects.create(user=user, displayName=name, host="https://restlessclients-7b4ebf6b9382.herokuapp.com/")
            user.is_active = True
            user.save()

    def setUp(self):
        self.alice = Author.objects.get(displayName="Alice")
        self.bob = Author.objects.get(displayName="Bob")

    def test_get_authors(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name)
        resp = self.client.get(url)

        self.assertEqual(resp.data["type"], "authors")
        self.assertEqual(len(resp.data["items"]), 2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_authors_unauthorized(self):
        url = reverse(self.url_name)
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_authors_page_exists(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        query = {
            'page': 1,
            'size': 1
        }

        url = reverse(self.url_name)
        url_str = f"{url}?{urlencode(query)}"
        resp = self.client.get(url_str)
        data = json.loads(resp.content)

        self.assertEqual(resp.data["type"], "authors")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["items"]), 1)

    def test_get_authors_page_out_of_bounds(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        query = {
            'page': 4,
            'size': 2
        }

        url = reverse(self.url_name)
        url_str = f"{url}?{urlencode(query)}"
        resp = self.client.get(url_str)
        data = json.loads(resp.content)

        self.assertEqual(resp.data["detail"], "Invalid page.")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_method(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp2 = self.client.delete(url)
        self.assertEqual(resp2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SingleAuthorTest(APITestCase):
    url_name = "project:author_api"

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

    def test_get_single_author_own_profile(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        alice = Author.objects.get(displayName="Alice")

        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.get(url)
        self.assertEqual(resp.data["type"], "author")
        self.assertEqual(resp.data["displayName"], "Alice")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        author = AuthorSerializer(data=resp.data)
        self.assertTrue(author.is_valid())
        reconstruct = Author.objects.get(**author.validated_data)
        self.assertEqual(reconstruct, alice)

    def test_get_single_author_diff_profile(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        bob = Author.objects.get(displayName="Bob")

        url = reverse(self.url_name, args=[self.bob.id])
        resp = self.client.get(url)
        self.assertEqual(resp.data["type"], "author")
        self.assertEqual(resp.data["displayName"], "Bob")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        author = AuthorSerializer(data=resp.data)
        self.assertTrue(author.is_valid())
        reconstruct = Author.objects.get(**author.validated_data)
        self.assertEqual(reconstruct, bob)

    def test_update_author_authorized(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        alice = Author.objects.get(displayName="Alice")
        self.assertEqual(alice.github, None) # The initial value before updates

        url = reverse(self.url_name, args=[self.alice.id])
        data = {"github": "https://github.com"}
        resp = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.data["type"], "author")
        self.assertEqual(resp.data["displayName"], "Alice")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        author = AuthorSerializer(data=resp.data)
        self.assertTrue(author.is_valid())
        reconstruct = Author.objects.get(**author.validated_data)

        self.assertEqual(reconstruct, alice) # Confirm it is the same author object
        self.assertEqual(reconstruct.github, "https://github.com") # The updated value

    def test_unauthorized_method(self):
        url = reverse(self.url_name, args=[self.alice.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        resp2 = self.client.post(url)
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_method(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])

        resp = self.client.put(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp2 = self.client.delete(url)
        self.assertEqual(resp2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
