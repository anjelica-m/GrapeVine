"""
Test module for follow request views.

Author: Kai Luedemann
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import Author, FollowRequest

class SendFollowRequestTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            Author.objects.create(user=user, displayName=name, host="restlessclients")

    def test_cannot_follow_self(self):
        author = Author.objects.first()
        resp = self.client.post(reverse('project:follow', args=[author.id]))
        query = FollowRequest.objects.filter(follower=author, following=author)
        self.assertFalse(query.exists())

    def test_create_follow_request(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        alice = user.author
        bob = Author.objects.get(displayName="Bob")

        resp = self.client.post(reverse('project:follow', args=[bob.id]))
        query = FollowRequest.objects.filter(follower=alice, following=bob)

        # self.assertTrue(query.exists())
        # fr = query.first()
        # self.assertEqual(fr.summary, "Alice wants to follow Bob")
        # self.assertRedirects(resp, reverse('project:profile', args=[bob.id]))

    def test_duplicate_follow_request(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        alice = user.author
        bob = Author.objects.get(displayName="Bob")
        FollowRequest.objects.create(follower=alice, following=bob)

        prev_count = FollowRequest.objects.filter(follower=alice, following=bob).count()
        self.assertEquals(prev_count, 1)

        resp = self.client.post(reverse('project:follow', args=[bob.id]))
        query = FollowRequest.objects.filter(follower=alice, following=bob)

        self.assertEquals(query.count(), 1)
        # self.assertRedirects(resp, reverse('project:profile', args=[bob.id]))

    def test_inverse_follow_request(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        alice = user.author

        bob = Author.objects.get(displayName="Bob")
        FollowRequest.objects.create(follower=bob, following=alice)

        resp = self.client.post(reverse('project:follow', args=[bob.id]))
        query = FollowRequest.objects.filter(follower=alice, following=bob)

        # self.assertTrue(query.exists())


class AcceptFollowRequestTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            Author.objects.create(user=user, displayName=name)

    def setUp(self):
        alice = Author.objects.get(displayName="Alice")
        bob = Author.objects.get(displayName="Bob")
        self.fr = FollowRequest.objects.create(follower=bob, following=alice)

    def test_follow_request_accepted(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        alice = user.author

        bob = Author.objects.get(displayName="Bob")

        resp = self.client.post(reverse('project:accept_follow', args=[self.fr.id]))
        query = FollowRequest.objects.filter(follower=bob, following=alice)
        self.assertFalse(query.exists())
        self.assertEquals(alice.followers.first(), bob)
        self.assertEquals(bob.following.first(), alice)
        self.assertRedirects(resp, reverse('project:home'))

    def test_true_friend(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        alice = user.author

        bob = Author.objects.get(displayName="Bob")

        alice.following.add(bob)

        resp = self.client.post(reverse('project:accept_follow', args=[self.fr.id]))
        self.assertEquals(alice.followers.first(), bob)
        self.assertEquals(bob.followers.first(), alice)

    def test_pending_reverse_request(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        alice = user.author

        bob = Author.objects.get(displayName="Bob")

        FollowRequest.objects.create(follower=alice, following=bob)

        resp = self.client.post(reverse('project:accept_follow', args=[self.fr.id]))
        self.assertEquals(alice.followers.first(), bob)
        query = FollowRequest.objects.filter(follower=alice, following=bob)
        self.assertTrue(query.exists())


class DeclineFollowRequestTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            Author.objects.create(user=user, displayName=name)

    def setUp(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        self.alice = user.author

        self.bob = Author.objects.get(displayName="Bob")
        self.fr = FollowRequest.objects.create(follower=self.bob, following=self.alice)

    def test_follow_request_declined(self):
        resp = self.client.post(reverse('project:decline_follow', args=[self.fr.id]))
        query = FollowRequest.objects.filter(follower=self.bob, following=self.alice)
        self.assertFalse(query.exists())
        self.assertFalse(self.alice.followers.exists())
        self.assertFalse(self.bob.following.exists())
        self.assertRedirects(resp, reverse('project:home'))

    def test_reverse_follow_maintained(self):
        self.alice.following.add(self.bob)

        resp = self.client.post(reverse('project:decline_follow', args=[self.fr.id]))
        self.assertFalse(self.alice.followers.exists())
        self.assertEquals(self.bob.followers.first(), self.alice)

    def test_pending_reverse_request(self):
        FollowRequest.objects.create(follower=self.alice, following=self.bob)

        resp = self.client.post(reverse('project:decline_follow', args=[self.fr.id]))
        self.assertFalse(self.alice.followers.exists())
        query = FollowRequest.objects.filter(follower=self.alice, following=self.bob)
        self.assertTrue(query.exists())


class UnfollowTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        for name in ["Alice", "Bob"]:
            user = User.objects.create(username=name, password="testpassword1")
            Author.objects.create(user=user, displayName=name)

    def setUp(self):
        user = User.objects.get(username="Alice")
        self.client.force_login(user)
        self.alice = user.author

        self.bob = Author.objects.get(displayName="Bob")
        self.alice.following.add(self.bob)

    def test_unfollow(self):
        resp = self.client.post(reverse('project:unfollow', args=[self.bob.id]))

        self.assertFalse(self.alice.following.exists())
        self.assertFalse(self.bob.followers.exists())
        # self.assertRedirects(resp, reverse('project:profile', args=[self.bob.id]))
    
    def test_reverse_follow_maintained(self):
        self.alice.followers.add(self.bob)

        resp = self.client.post(reverse('project:unfollow', args=[self.bob.id]))

        self.assertFalse(self.alice.following.exists())
        self.assertFalse(self.bob.followers.exists())
        self.assertEqual(self.alice.followers.first(), self.bob)
        self.assertEqual(self.bob.following.first(), self.alice)

    def test_pending_reverse_request_maintained(self):
        FollowRequest.objects.create(follower=self.bob, following=self.alice)
        
        resp = self.client.post(reverse('project:unfollow', args=[self.bob.id]))

        query = FollowRequest.objects.filter(follower=self.bob, following=self.alice)

        self.assertTrue(query.exists())
        self.assertFalse(self.alice.following.exists())
        self.assertFalse(self.bob.followers.exists())
