import django_filters
from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Custom filter for recipes
    """
    # Exact match filters
    cuisine = django_filters.CharFilter(
        field_name='cuisine_type', lookup_expr='iexact')
    meal = django_filters.CharFilter(
        field_name='meal_type', lookup_expr='iexact')
    dietary = django_filters.CharFilter(
        field_name='dietary_tags', lookup_expr='iexact')
    difficulty = django_filters.CharFilter(
        field_name='difficulty_level', lookup_expr='iexact')

    # Range filters
    prep_time_min = django_filters.NumberFilter(
        field_name='prep_time', lookup_expr='gte')
    prep_time_max = django_filters.NumberFilter(
        field_name='prep_time', lookup_expr='lte')
    cook_time_min = django_filters.NumberFilter(
        field_name='cook_time', lookup_expr='gte')
    cook_time_max = django_filters.NumberFilter(
        field_name='cook_time', lookup_expr='lte')

    # Servings filter
    servings_min = django_filters.NumberFilter(
        field_name='servings', lookup_expr='gte')
    servings_max = django_filters.NumberFilter(
        field_name='servings', lookup_expr='lte')

    # Author filter
    author = django_filters.CharFilter(
        field_name='author__username', lookup_expr='iexact')

    # Search in title and description
    title_contains = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains')

    class Meta:
        model = Recipe
        fields = [
            'cuisine_type',
            'meal_type',
            'dietary_tags',
            'difficulty_level',
        ]
