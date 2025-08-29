"""
Base test class for security tests
"""
from django.test import TestCase, Client
from django.urls import reverse


class SecurityBaseTest(TestCase):
    """Base class for security-related tests"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.home_url = reverse('api-root')

    def get_response_headers(self, url=None):
        """Get response headers for a given URL"""
        if url is None:
            url = self.home_url
        response = self.client.get(url)
        return response.headers

    def assertSecurityHeader(self, response, header_name, expected_value=None):
        """Assert that a security header is present and optionally check its value"""
        self.assertIn(header_name, response, 
                     f"Header {header_name} not found in response")
        if expected_value:
            self.assertEqual(response[header_name], expected_value,
                           f"Header {header_name} value mismatch")

    def assertNoSecurityHeader(self, response, header_name):
        """Assert that a security header is NOT present"""
        self.assertNotIn(header_name, response,
                        f"Header {header_name} should not be present in response")