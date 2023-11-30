from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from requests.models import Response


class StockViewTestCase(APITestCase):
    @patch("requests.get")
    def test_get_stock_data(self, mock_requests_get):
        """
        Test retrieving stock data with a mock response from an external API.
        """
        mock_response = "Symbol,Date,Time,Open,High,Low,Close,Name\nAAPL.US,2023-10-25,16:00:00,150.0,152.0,148.0,151.5,Apple Inc."
        mock_requests_get.return_value = Response()
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value._content = mock_response.encode("utf-8")

        url = reverse("stock")

        response = self.client.get(url, {"stock_code": "AAPL.US"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "symbol": "AAPL.US",
                "date": "2023-10-25 16:00:00",
                "open": "150.0",
                "high": "152.0",
                "low": "148.0",
                "close": "151.5",
                "name": "Apple Inc.",
            },
        )

    def test_get_stock_data_missing_stock_code(self):
        """
        Test retrieving stock data with a missing stock code.
        """
        url = reverse("stock")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"error": "Stock code is required."},
        )

    @patch("requests.get")
    def test_get_stock_data_failed_request(self, mock_requests_get):
        """
        Test retrieving stock data with a mock failed external API request.
        """
        mock_requests_get.return_value = Response()
        mock_requests_get.return_value.status_code = 404

        url = reverse("stock")

        response = self.client.get(url, {"stock_code": "AAPL.US"})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_stock_data_real_request(self):
        """
        Test retrieving stock data with a real external API request.
        This test makes a real request, so it may depend on the availability of the external API.
        """
        url = reverse("stock")
        stock_code = "AAPL.US"

        response = self.client.get(url, {"stock_code": stock_code})

        if response.status_code == 200:
            self.assertDictEqual(
                response.data,
                {
                    "symbol": stock_code,
                    "date": response.data["date"],
                    "open": response.data["open"],
                    "high": response.data["high"],
                    "low": response.data["low"],
                    "close": response.data["close"],
                    "name": response.data["name"],
                },
            )
        else:
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
