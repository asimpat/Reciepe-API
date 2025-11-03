from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Recipe(models.Model):
    CUISINE_CHOICES = [
        ('italian', 'Italian'),
        ('chinese', 'Chinese'),
        ('mexican', 'Mexican'),
        ('indian', 'Indian'),
        ('french', 'French'),
        ('japanese', 'Japanese'),
        ('thai', 'Thai'),
        ('mediterranean', 'Mediterranean'),
        ('american', 'American'),
        ('african', 'African'),
        ('other', 'Other'),
    ]

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('dessert', 'Dessert'),
        ('appetizer', 'Appetizer'),
        ('beverage', 'Beverage'),
    ]

    DIETARY_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('gluten_free', 'Gluten Free'),
        ('dairy_free', 'Dairy Free'),
        ('keto', 'Keto'),
        ('paleo', 'Paleo'),
        ('low_carb', 'Low Carb'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
        ('none', 'None'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    # Recipe Content
    ingredients = models.TextField(help_text="List ingredients, one per line")
    instructions = models.TextField(
        help_text="Step-by-step cooking instructions")

    # Categorization
    cuisine_type = models.CharField(
        max_length=50,
        choices=CUISINE_CHOICES,
        default='other'
    )
    meal_type = models.CharField(
        max_length=50,
        choices=MEAL_TYPE_CHOICES,
        default='dinner'
    )
    dietary_tags = models.CharField(
        max_length=50,
        choices=DIETARY_CHOICES,
        default='none',
        blank=True
    )

    # Additional Details
    prep_time = models.IntegerField(
        help_text="Preparation time in minutes",
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )
    cook_time = models.IntegerField(
        help_text="Cooking time in minutes",
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )
    servings = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=1
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )

    # Media
    image = models.ImageField(
        upload_to='recipe_images/',
        blank=True,
        null=True
    )

    # Engagement Metrics
    views_count = models.IntegerField(default=0)

    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="saved_recipes",
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['cuisine_type']),
            models.Index(fields=['meal_type']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return self.title

    @property
    def total_time(self):
        # Calculate total cooking time
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook

    @property
    def average_rating(self):
        # Calculate average rating from all ratings
        ratings = self.recipe_ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return 0

    @property
    def ratings_count(self):
        # """Get total number of ratings"""
        return self.recipe_ratings.count()

    @property
    def comments_count(self):
        # """Get total number of comments"""
        return self.comments.count()

    @property
    def saves_count(self):
        # """Get total number of saves"""
        return self.saved_by.count()


class Rating(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ratings'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')  # Prevent duplicate user ratings
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title} ({self.score})"
