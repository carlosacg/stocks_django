from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.db.models import Count
from typing import Dict, Any, Union
import requests

from api.models import UserRequestHistory
from api.serializers import UserRequestHistorySerializer


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs) -> Response:
        """
        Obtain an authentication token for the user.

        Returns:
            Response: A JSON response containing the user's authentication token, user ID, and email.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = Token.objects.get_or_create(user=user)
            response_data: Dict[str, Any] = {
                "token": token.key,
                "user_id": user.pk,
                "email": user.email,
            }
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockView(APIView):
    """
    API endpoint to allow users to query stock information.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle GET request to retrieve stock information and record user history.

        Returns:
            Response: The API response with stock information or an error message.
        """

        user = request.user

        if user is None:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        stock_code = request.query_params.get("stock_code")

        api_url = f"http://localhost:8000/stock?stock_code={stock_code}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data: Dict[str, Union[str, float]] = response.json()
            formatted_data = {
                "name": data["name"],
                "symbol": data["symbol"],
                "open": float(data["open"]),
                "high": float(data["high"]),
                "low": float(data["low"]),
                "close": float(data["close"]),
            }
            user_request_history = UserRequestHistory(
                date=data["date"],
                name=formatted_data["name"],
                symbol=formatted_data["symbol"],
                open=formatted_data["open"],
                high=formatted_data["high"],
                low=formatted_data["low"],
                close=formatted_data["close"],
                user=request.user,
            )
            user_request_history.save()
            return Response(formatted_data)
        else:
            return Response(
                {"error": "Failed to retrieve stock information"},
                status=response.status_code,
            )


class HistoryView(generics.ListAPIView):
    """
    Returns queries made by current user.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserRequestHistorySerializer

    def get_queryset(self):
        """
        Filter the queryset to get records for the user making the request.

        Returns:
            queryset: Filtered queryset of UserRequestHistory records.
        """
        user = self.request.user
        return UserRequestHistory.objects.filter(user=user).order_by("-date")

#MainCache
class StatsView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    """
    Allows super users to see which are the most queried stocks.
    """

    def get(self, request, *args, **kwargs) -> Response:
        """
        Get the most queried stocks for super users.

        Retrieves the top 5 most queried stocks based on the number of requests.

        Returns:
            Response: A JSON response containing the most queried stocks.
        """
        stats = (
            UserRequestHistory.objects.values("symbol")
            .annotate(times_requested=Count("symbol"))
            .order_by("-times_requested")[:5]
        )

        formatted_stats = [
            {"stock": item["symbol"].lower(), "times_requested": item["times_requested"]}
            for item in stats
        ]

        return Response(formatted_stats)
