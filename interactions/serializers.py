from rest_framework import serializers
from .models import Rating, Comment
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
        # """Validate rating score is between 1 and 5"""
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


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    recipe_title = serializers.CharField(source='recipe.title', read_only=True)
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'recipe', 'recipe_title',
                  'comment', 'is_author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_is_author(self, obj):
        # """Check if current user is the comment author"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def validate_comment(self, value):
        # """Validate comment is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        if len(value) < 2:
            raise serializers.ValidationError(
                "Comment must be at least 2 characters long.")
        return value


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    # """Simplified serializer for creating/updating comments"""

    class Meta:
        model = Comment
        fields = ['comment']

    def validate_comment(self, value):
        # """Validate comment is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        if len(value) < 2:
            raise serializers.ValidationError(
                "Comment must be at least 2 characters long.")
        return value


class SavedRecipeSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    recipe_details = serializers.SerializerMethodField()

    class Meta:
        model = SavedRecipe
        fields = ['id', 'user', 'recipe', 'recipe_details', 'saved_at']
        read_only_fields = ['id', 'user', 'saved_at']

    def get_recipe_details(self, obj):
        """Get basic recipe details"""
        from recipe.serializers import RecipeListSerializer
        return RecipeListSerializer(obj.recipe, context=self.context).data
