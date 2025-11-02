from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Recipe
from .serializers import (
    RecipeSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer
)
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from interactions.models import Rating
from interactions.serializers import RatingSerializer, RatingCreateUpdateSerializer


class RecipeListCreateView(generics.ListCreateAPIView):
  
    queryset = Recipe.objects.all().select_related('author')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'ingredients']
    ordering_fields = ['created_at', 'title', 'prep_time', 'cook_time']
    ordering = ['-created_at']
  

    def get_serializer_class(self):
        """Use different serializers for list and create"""
        if self.request.method == 'POST':
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def get_queryset(self):
        """
        Apply filters based on query parameters
        """
        queryset = super().get_queryset()

        # Filter by cuisine type
        cuisine = self.request.query_params.get('cuisine', None)
        if cuisine:
            queryset = queryset.filter(cuisine_type=cuisine)

        # Filter by meal type
        meal = self.request.query_params.get('meal', None)
        if meal:
            queryset = queryset.filter(meal_type=meal)

        # Filter by dietary tags
        dietary = self.request.query_params.get('dietary', None)
        if dietary:
            queryset = queryset.filter(dietary_tags=dietary)

        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        # Filter by author
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)

        return queryset

    def perform_create(self, serializer):
        """Set the author to the current user when creating"""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to return custom response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return full recipe details
        recipe = Recipe.objects.get(id=serializer.instance.id)
        response_serializer = RecipeSerializer(
            recipe, context={'request': request})

        return Response({
            "message": "Recipe created successfully!",
            "recipe": response_serializer.data
        }, status=status.HTTP_201_CREATED)


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all().select_related('author')
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_field = 'pk'

    def get_serializer_class(self):
        """Use different serializers for retrieve and update"""
        if self.request.method in ['PUT', 'PATCH']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment view count"""
        instance = self.get_object()

        # Increment view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full recipe details
        response_serializer = RecipeSerializer(
            instance, context={'request': request})

        return Response({
            "message": "Recipe updated successfully!",
            "recipe": response_serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        recipe_title = instance.title
        self.perform_destroy(instance)

        return Response({
            "message": f"Recipe '{recipe_title}' deleted successfully!"
        }, status=status.HTTP_200_OK)


class RecipeRatingView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingCreateUpdateSerializer

    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        rating = Rating.objects.filter(
            user=request.user, recipe=recipe).first()

        if rating:
            serializer = RatingSerializer(rating)
            return Response(serializer.data)

        return Response({
            "message": "You haven't rated this recipe yet."
        }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        """Rate a recipe (create or update)"""
        recipe = get_object_or_404(Recipe, pk=pk)

        # Check if user is rating their own recipe
        if recipe.author == request.user:
            return Response({
                "error": "You cannot rate your own recipe."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create or update rating
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'score': serializer.validated_data['score']}
        )

        # Return response
        response_serializer = RatingSerializer(
            rating, context={'request': request})

        if created:
            message = f"You rated '{recipe.title}' {rating.score}/5 stars!"
        else:
            message = f"Your rating for '{recipe.title}' has been updated to {rating.score}/5 stars!"

        return Response({
            "message": message,
            "rating": response_serializer.data,
            "recipe_average_rating": recipe.average_rating
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk):
        """Remove user's rating from a recipe"""
        recipe = get_object_or_404(Recipe, pk=pk)
        rating = Rating.objects.filter(
            user=request.user, recipe=recipe).first()

        if not rating:
            return Response({
                "error": "You haven't rated this recipe."
            }, status=status.HTTP_404_NOT_FOUND)

        rating.delete()

        return Response({
            "message": f"Your rating for '{recipe.title}' has been removed."
        }, status=status.HTTP_200_OK)


class MyRecipesView(generics.ListAPIView):
    serializer_class = RecipeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by('-created_at')
