from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q
from .models import Recipe
from .serializers import (
    RecipeSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer
)
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


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
    """
    GET: Retrieve a specific recipe
    PUT: Update a recipe (author only)
    PATCH: Partially update a recipe (author only)
    DELETE: Delete a recipe (author only)
    """
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
        """Override update to return custom response"""
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
        """Override destroy to return custom response"""
        instance = self.get_object()
        recipe_title = instance.title
        self.perform_destroy(instance)

        return Response({
            "message": f"Recipe '{recipe_title}' deleted successfully!"
        }, status=status.HTTP_200_OK)


class MyRecipesView(generics.ListAPIView):
    """
    GET: Get all recipes by the current authenticated user
    """
    serializer_class = RecipeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only recipes by current user"""
        return Recipe.objects.filter(author=self.request.user).order_by('-created_at')
