from users.serializers import UserSerializer
from .models import Recipe
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'bio']
        extra_kwargs = {
            'bio': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            bio=validated_data.get('bio', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'profile_picture',
            'followers_count', 'following_count', 'is_following',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username',
                            'email', 'created_at', 'updated_at']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.id).exists()
        return False

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra responses
        data['user'] = { 
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'bio': self.user.bio,
        }

        return data


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_username = serializers.CharField(
        source='author.username', read_only=True)
    average_rating = serializers.ReadOnlyField()
    ratings_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    saves_count = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()
    is_saved = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'description',
            'author',
            'author_username',
            'ingredients',
            'instructions',
            'cuisine_type',
            'meal_type',
            'dietary_tags',
            'prep_time',
            'cook_time',
            'total_time',
            'servings',
            'difficulty_level',
            'image',
            'average_rating',
            'ratings_count',
            'comments_count',
            'saves_count',
            'views_count',
            'is_saved',
            'user_rating',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author',
            'views_count',
            'created_at',
            'updated_at'
        ]

    def get_is_saved(self, obj):
        """Check if current user has saved this recipe"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(user=request.user).exists()
        return False

    def get_user_rating(self, obj):
        """Get current user's rating for this recipe"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            if rating:
                return rating.score
        return None

    def validate_title(self, value):
        """Ensure title is not empty and has minimum length"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )
        return value

    def validate_ingredients(self, value):
        """Ensure ingredients field is not empty"""
        if not value.strip():
            raise serializers.ValidationError(
                "Ingredients cannot be empty."
            )
        return value

    def validate_instructions(self, value):
        """Ensure instructions field is not empty"""
        if not value.strip():
            raise serializers.ValidationError(
                "Instructions cannot be empty."
            )
        return value


class RecipeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing recipes"""
    author_username = serializers.CharField(
        source='author.username', read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'description',
            'author_username',
            'cuisine_type',
            'meal_type',
            'difficulty_level',
            'image',
            'average_rating',
            'total_time',
            'servings',
            'created_at',
        ]


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes"""

    class Meta:
        model = Recipe
        fields = [
            'title',
            'description',
            'ingredients',
            'instructions',
            'cuisine_type',
            'meal_type',
            'dietary_tags',
            'prep_time',
            'cook_time',
            'servings',
            'difficulty_level',
            'image',
        ]

    def validate(self, attrs):
        """Additional validation"""
        if attrs.get('prep_time') and attrs['prep_time'] < 0:
            raise serializers.ValidationError({
                "prep_time": "Preparation time cannot be negative."
            })

        if attrs.get('cook_time') and attrs['cook_time'] < 0:
            raise serializers.ValidationError({
                "cook_time": "Cooking time cannot be negative."
            })

        if attrs.get('servings') and attrs['servings'] < 1:
            raise serializers.ValidationError({
                "servings": "Servings must be at least 1."
            })

        return attrs
