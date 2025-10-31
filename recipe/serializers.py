from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
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
            return obj.saved_by.filter(id=request.user.id).exists()
        return False

    def get_user_rating(self, obj):
        """Get current user's rating for this recipe"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(id=request.user.id).first()
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
