from rest_framework import serializers
from .models import FSJob

class FSJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSJob
        fields = ["id", "description", "result"]

