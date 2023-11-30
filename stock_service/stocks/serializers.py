from rest_framework import serializers

class StockDataSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    date = serializers.CharField()
    open = serializers.CharField()
    high = serializers.CharField()
    low = serializers.CharField()
    close = serializers.CharField()
    name = serializers.CharField()
