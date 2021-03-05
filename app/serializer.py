from rest_framework import serializers
from app.models import User

class SearchUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('created_time', )