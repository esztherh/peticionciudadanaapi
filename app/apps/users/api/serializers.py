from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers


# User = settings.AUTH_USER_MODEL
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user

class ProfileSerializer(serializers.ModelSerializer):
    createdAt = serializers.CharField(source='date_joined')
    permissions = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'createdAt', 'permissions',)


class DropdownUserSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('value', 'label')

    def get_label(self,instance):
        return "%s" % (instance.username)
