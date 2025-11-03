from django.urls import path
from .views import (
    RecipeCommentListCreateView,
    RetrieveUpdateDestroyCommentView
)

urlpatterns = [
    path('recipes/<int:recipe_pk>/comments/',
         RecipeCommentListCreateView.as_view(), name='recipe-comments'),
    path('comments/<int:pk>/', RetrieveUpdateDestroyCommentView.as_view(), name='comment-detail'),
]
