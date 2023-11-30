from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="testpassword"
        )

    def test_user_creation(self):
        """
        Test if a user can be created and if the password is correctly hashed.
        """
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpassword"))


class StockViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="testpassword"
        )
        self.url = reverse("stock")

    def test_stock_view_with_authenticated_user(self):
        """
        Test if a stock view returns HTTP 200 when an authenticated user accesses it.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"stock_code": "ZCMD.US"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stock_view_without_authentication(self):
        """
        Test if a stock view returns HTTP 401 when an unauthenticated user accesses it.
        """
        response = self.client.get(self.url, {"stock_code": "AAPL.US"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HistoryViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="testpassword"
        )
        self.url = reverse("history")

    def test_history_view_with_authenticated_user(self):
        """
        Test if a history view returns HTTP 200 when an authenticated user accesses it.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StatsViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="testAdmin", email="admin@example.com", password="adminpassword"
        )
        self.no_admin_user = User.objects.create_user(
            username="testNoAdmin",
            email="noAdmin@example.com",
            password="noAdminpassword",
        )
        self.url = reverse("stats")

    def test_stats_view_with_admin_user(self):
        """
        Test if a stats view returns HTTP 200 when an admin user accesses it.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stats_view_with_no_admin_user(self):
        """
        Test if a stats view returns HTTP 403 when a non-admin user accesses it.
        """
        self.client.force_authenticate(user=self.no_admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
