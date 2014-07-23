# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Group
from django.utils import timezone

from djangobb_forum.models import Category, Forum, Topic, Post


class TestHiddenCategory(TestCase):
    fixtures = ['test_forum.json']

    def setUp(self):
        self.superuser = User.objects.get(username='djangobb')

        self.secret_category = Category.objects.get(pk=3)  # Secret category
        self.secret_forum = Forum.objects.get(pk=4)  # Secret forum
        self.secret_topic = Topic.objects.create(forum=self.secret_forum,
                                                 user=self.superuser,
                                                 name="Secret Topic",
                                                 updated=timezone.now())  # Secret topic

        self.secret_forum_url = reverse('djangobb:forum', args=(self.secret_forum.pk,))
        self.secret_topic_url = reverse('djangobb:topic', args=(self.secret_topic.pk,))
        self.search_url = reverse('djangobb:search')

        self.secret_category_tag = '<optgroup label="%s">' % self.secret_category.name

    def test_hidden_categories_for_superuser(self):
        """
        Superuser can view the secret forum
        """
        self.assertTrue(self.client.login(username='djangobb', password='djangobb'))
        response = self.client.get(self.secret_forum_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.secret_category_tag)

        response = self.client.get(self.secret_topic_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.secret_category_tag)

        response = self.client.get(self.search_url)
        self.assertContains(response, self.secret_category_tag)

        self.client.logout()

    def test_hidden_categories_for_user_in_secret_group(self):
        """
        User from a secret group can view the secret forum
        """
        self.assertTrue(self.client.login(username='slav0nic', password='slav0nic'))
        response = self.client.get(self.secret_forum_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.secret_category_tag)

        response = self.client.get(self.secret_topic_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.secret_category_tag)

        response = self.client.get(self.search_url)
        self.assertContains(response, self.secret_category_tag)

        self.client.logout()

    def test_hidden_categories_for_anonymous(self):
        """
        Anonymous users can't view the secret forum
        """
        response = self.client.get(self.secret_forum_url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(self.secret_topic_url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(self.search_url)
        self.assertNotContains(response, self.secret_category_tag)

    def test_moderator_move_topic(self):
        """
        Moderators can't vew the secret category if they are not in the secret group
        and also can't move any topics there.
        """
        user = User.objects.get(username='alafin')

        # Make the user as moderator
        forum = Forum.objects.get(pk=1)
        topic = forum.topics.first()
        forum.moderators.add(user)

        self.assertTrue(self.client.login(username=user.username, password=user.username))

        # Test choosing a forum to move the topic
        moderate_url = reverse('djangobb:moderate', args=(forum.pk,))
        post_data = {
            'move_topics': 1,
            'topic_id': topic.pk,
        }
        response = self.client.post(moderate_url, post_data, follow=True)
        self.assertNotContains(response, self.secret_category_tag)

        # Test moving a topic to the secret forum
        move_topic_url = reverse('djangobb:move_topic')
        post_data = {
            'topic_id': topic.pk,
            'to_forum': self.secret_forum.pk,
        }
        response = self.client.post(move_topic_url, post_data, follow=True)
        self.assertEqual(response.status_code, 403)

        self.client.logout()