import requests
import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import StockDataSerializer
from typing import Dict


class StockView(APIView):
    """
    API view for retrieving stock data from Stooq.
    """

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle GET requests for stock data.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response containing stock data.
        """
        stock_code = request.query_params.get("stock_code")

        if not stock_code:
            return Response(
                {"error": "Stock code is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        api_url = f"https://stooq.com/q/l/?s={stock_code}&f=sd2t2ohlcvn&h&e=csv"

        try:
            response = requests.get(api_url)

            if response.status_code != 200:
                return Response(
                    {"error": "Failed to fetch data from stooq.com."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            csv_data = response.text.strip()
            csv_reader = csv.reader(csv_data.splitlines())
            header = next(csv_reader)

            column_indexes: Dict[str, int] = {header[i]: i for i in range(len(header))}

            stock_data = {}
            for row in csv_reader:
                stock_data = {
                    "symbol": row[column_indexes["Symbol"]],
                    "date": f"{row[column_indexes['Date']]} {row[column_indexes['Time']]}",
                    "open": row[column_indexes["Open"]],
                    "high": row[column_indexes["High"]],
                    "low": row[column_indexes["Low"]],
                    "close": row[column_indexes["Close"]],
                    "name": row[column_indexes["Name"]],
                }
                break

            serializer = StockDataSerializer(data=stock_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
