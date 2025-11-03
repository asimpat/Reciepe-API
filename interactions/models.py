from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    # """
    # Rating model for recipes
    # """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    recipe = models.ForeignKey(
        'recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='interaction_ratings'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'recipe')  # One rating per user per recipe
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipe', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.score}/5"


class Comment(models.Model):
    # """
    # Comment model for recipes
    # """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    recipe = models.ForeignKey(
        'recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipe', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} commented on {self.recipe.title}"
