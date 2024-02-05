"""
Test module for miscellaneous views.

Author: Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Author


# Test signup and login
class AuthenticationTest(APITestCase):
    def setUp(self):
        testuser = User.objects.create_user(username="user1", password="test1")
        Author.objects.create(user=testuser, displayName="user1")
        testuser.is_active = True
        testuser.save()

    def test_signup_valid(self):
        request = {
            'username': 'user2',
            'password1': 'test2test',
            'password2': 'test2test'
        }

        response = self.client.post(
            reverse("project:signup"),
            request,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    def test_login_valid(self):
        request = {
            'username': 'user1',
            'password': 'test1'
        }

        response = self.client.post(
            reverse('token_obtain_pair'),
            request,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileEditViewTest(TestCase):
    def setUp(self):
        testuser = User.objects.create_user(username="user1", password="test1")
        Author.objects.create(user=testuser, displayName="user1")
        self.client.force_login(testuser)
        self.author = testuser.author

    def test_edit_profile(self):
        url = reverse("project:profile_edit")

        request = {'github': 'github.com',
                   'bio': 'test bio'
                   }

        response = self.client.post(
            url,
            request
        )

        self.assertRedirects(response, '/edit/', status_code=status.HTTP_302_FOUND,
                             target_status_code=status.HTTP_200_OK, fetch_redirect_response=True)
