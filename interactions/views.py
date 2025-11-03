from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from recipe.models import Recipe
from .models import Comment
from rest_framework.exceptions import PermissionDenied

from .serializers import CommentSerializer, CommentCreateUpdateSerializer
# from .permissions import IsCommentAuthorOrReadOnly


class RecipeCommentListCreateView(generics.ListCreateAPIView):
    # """
    # GET: List all comments for a recipe
    # POST: Create a new comment on a recipe
    # """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateUpdateSerializer
        return CommentSerializer

    def get_queryset(self):
        # """Get comments for specific recipe"""
        recipe_id = self.kwargs.get('recipe_pk')
        return Comment.objects.filter(recipe_id=recipe_id).select_related('user', 'recipe')

    def create(self, request, *args, **kwargs):
        # """Create a new comment"""
        recipe_id = self.kwargs.get('recipe_pk')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save comment
        comment = serializer.save(user=request.user, recipe=recipe)

        # Return full comment details
        response_serializer = CommentSerializer(
            comment, context={'request': request})

        return Response({
            "message": "Comment added successfully!",
            "comment": response_serializer.data
        }, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyCommentView(generics.RetrieveUpdateDestroyAPIView):
    # """
    # GET: Retrieve a specific comment
    # PUT/PATCH: Update a comment (author only)
    # DELETE: Delete a comment (author only)
    # """
    queryset = Comment.objects.all().select_related('user', 'recipe')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CommentCreateUpdateSerializer
        return CommentSerializer

    def get_object(self):
        # """Get comment and check permissions"""
        comment = super().get_object()

        # Only author can update/delete
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if comment.user != self.request.user:
                raise PermissionDenied(
                    "You can only edit/delete your own comments.")

        return comment

    def update(self, request, *args, **kwargs):
        # """Update comment"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = CommentSerializer(
            instance, context={'request': request})

        return Response({
            "message": "Comment updated successfully!",
            "comment": response_serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        # """Delete comment"""
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "message": "Comment deleted successfully!"
        }, status=status.HTTP_200_OK)
