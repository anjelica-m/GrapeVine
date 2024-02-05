"""
Test module for follow request API.

Author: Kai Luedemann
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

import uuid

from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Author, FollowRequest
from ..serializers import FollowRequestSerializer, AuthorSerializer

class FollowRequestSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        data = {
            "github": "http://www.github.com",
            "url": "http://www.google.com",
            "host": "::1"
        }
        
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            Author.objects.create(user=user, displayName=name, **data)

    def setUp(self):
        self.alice = Author.objects.get(displayName="Alice")
        self.bob = Author.objects.get(displayName="Bob")
        self.summary = "Bob wants to follow Alice"
        self.fr = FollowRequest.objects.create(follower=self.bob, following=self.alice, summary=self.summary)

    def test_follow_request_serialized(self):
        serializer = FollowRequestSerializer(self.fr)
        obj_type = serializer.data["type"]
        summary = serializer.data["summary"]
        follower = AuthorSerializer(data=serializer.data["actor"])
        following = AuthorSerializer(data=serializer.data["object"])
        
        self.assertEquals(obj_type, "Follow")
        self.assertEquals(summary, self.summary)
        self.assertTrue(follower.is_valid())
        self.assertTrue(following.is_valid())
        self.assertEquals(Author.objects.get(**follower.validated_data), self.bob)
        self.assertEquals(Author.objects.get(**following.validated_data), self.alice)


    def test_follow_request_deserialized(self):
        data = {
            "type": "Follow",
            "summary": self.summary,
            "actor": AuthorSerializer(self.bob).data,
            "object": AuthorSerializer(self.alice).data
        }

        serializer = FollowRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        follower = Author.objects.get(**serializer.validated_data["follower"])
        following = Author.objects.get(**serializer.validated_data["following"])
        summary = serializer.validated_data["summary"]
        fr = FollowRequest.objects.get(follower=follower, following=following, summary=summary)
        self.assertEquals(fr, self.fr)

    def test_invalid_request(self):
        data = {
            "blah": "blah"
        }
        # Should probably check type field as well!
        serializer = FollowRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class FollowRequestAPITest(APITestCase):
    url_name = "project:api_follow_request"

    @classmethod
    def setUpTestData(cls):
        data = {
            "github": "http://www.github.com",
            "url": "http://www.google.com",
            "host": "::1"
        }
        
        cls.userObj = {"Alice": "", "Bob": ""}
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            cls.userObj[name] = user
            Author.objects.create(user=user, displayName=name, **data)

    def setUp(self):
        self.alice = Author.objects.get(displayName="Alice")
        self.bob = Author.objects.get(displayName="Bob")
        self.summary = "Bob wants to follow Alice"
        fr = FollowRequest.objects.create(follower=self.bob, following=self.alice, summary=self.summary)
        self.serializer = FollowRequestSerializer(fr)
        fr.delete()

    def test_posted_successfully(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])

        resp = self.client.post(url, self.serializer.data, format='json')

        query = FollowRequest.objects.filter(follower=self.bob, following=self.alice, summary=self.summary)
        self.assertTrue(query.exists())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_author_not_found(self):
        self.client.force_authenticate(user=self.userObj["Alice"])
        fake_id = uuid.uuid4()
        url = reverse(self.url_name, args=[fake_id])

        resp = self.client.post(url, self.serializer.data, format='json')
        query = FollowRequest.objects.filter(follower=self.bob, following=self.alice, summary=self.summary)
        self.assertFalse(query.exists())
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_bad_data(self):
        # Need to test more of these cases depending on how we want it to work
        self.client.force_authenticate(user=self.userObj["Alice"])
        url = reverse(self.url_name, args=[self.alice.id])
        data = self.serializer.data
        data.pop("summary")

        resp = self.client.post(url, data, format='json')
        query = FollowRequest.objects.filter(follower=self.bob, following=self.alice)
        self.assertFalse(query.exists())
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
