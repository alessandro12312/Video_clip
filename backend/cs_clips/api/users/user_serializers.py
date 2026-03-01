# User serializer
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import override as translation_override
from rest_framework import serializers

User = get_user_model()


# Generale
class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )
    followers_count = serializers.IntegerField(read_only=True, default=0)
    following_count = serializers.IntegerField(read_only=True, default=0)
    is_followed_by_me = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "bio",
            "created_at",
            "updated_at",
            "followers",
            "following",
            "followers_count",
            "following_count",
            "is_followed_by_me",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "username",
            "email",
            "followers",
            "following",
        )

    def run_validation(self, data=serializers.empty):
        """Forza localizzazione italiana per messaggi di validazione."""
        with translation_override("it"):
            return super().run_validation(data)


# User registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def run_validation(self, data=serializers.empty):
        """Forza localizzazione italiana per tutti i messaggi di validazione."""
        with translation_override("it"):
            return super().run_validation(data)

    def validate_password(self, value):
        """Valida la password con i 4 validator Django standard."""
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
