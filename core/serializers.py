

from core.models import User

from .exceptions import InvalidUserDataException
from rest_framework import serializers
from .models import Project, Task,Comment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']

    def validate_email(self, value):
        """Check if the email contains an '@' symbol."""
        if '@' not in value:
            raise InvalidUserDataException(detail="Email must contain an '@' symbol.")
        return value


    def validate_password(self, value):
        """Ensure password is at least 6 characters long."""
        if len(value) < 6:
            raise InvalidUserDataException(detail="Password must be at least 6 characters long.")
        return value


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['role'] = user.role
        return token


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'password', 'role']   # Office use email cant be modified

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)



class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_by', 'members', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at']


    def validate_status(self, value):
        valid_statuses = ['TODO', 'IN_PROGRESS', 'DONE']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'task', 'project', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at'] 
