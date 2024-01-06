"""
Tests for health check api
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
    """Test the health check api"""
    def test_health_check(self):
        """Test health check api"""
        client = APIClient()
        url = reverse('health-check')
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
