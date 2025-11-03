from rest_framework import serializers
from .models import Rating
from users.serializers import UserProfileSerializer


class RatingSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    recipe_title = serializers.CharField(source='recipe.title', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'recipe', 'recipe_title',
                  'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_score(self, value):
        """Validate rating score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value


class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    # """Simplified serializer for creating/updating ratings"""

    class Meta:
        model = Rating
        fields = ['score']

    def validate_score(self, value):
        # """Validate rating score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value
