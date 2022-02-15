from rest_framework import serializers


from .models import Credit
from django.contrib.auth import get_user_model, authenticate


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            phone_number = validated_data['phone_number'],
            email=validated_data['email'],
            name = validated_data['name'],
            password = validated_data['password']
        )
        return user

    class Meta:
        model = get_user_model()
        fields = [
            'pk',
            'phone_number',
            'email',
            'name',
            'password'
            ]


class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        fields = [
            'pk',
            'user',
            'credit',
            'expiration_date',
        ]


