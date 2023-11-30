# encoding: utf-8

from django.contrib import admin
from django.urls import path

from api import views as api_views

urlpatterns = [
    path('token-auth', api_views.CustomObtainAuthToken.as_view(), name='token-auth'),
    path('stock', api_views.StockView.as_view(), name='stock'),
    path('history', api_views.HistoryView.as_view(), name='history'),
    path('stats', api_views.StatsView.as_view(), name='stats'),
    path('admin', admin.site.urls),
]
