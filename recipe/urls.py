from django.urls import path
from .views import (
    RecipeListCreateView,
    RecipeDetailView,
    MyRecipesView,
    RecipeRatingView,
    RecipeSaveView,
)


urlpatterns = [
    path('', RecipeListCreateView.as_view(), name='recipe-list-create'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('my-recipes/', MyRecipesView.as_view(), name='my-recipes'),
    path('<int:pk>/rate/', RecipeRatingView.as_view(), name='recipe-rate'),
]
