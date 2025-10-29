from django.contrib import admin
from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'cuisine_type',
        'meal_type',
        'difficulty_level',
        'servings',
        'created_at'
    ]
    list_filter = [
        'cuisine_type',
        'meal_type',
        'dietary_tags',
        'difficulty_level',
        'created_at'
    ]
    search_fields = ['title', 'description', 'ingredients', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'views_count']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'author', 'image')
        }),
        ('Recipe Details', {
            'fields': ('ingredients', 'instructions', 'servings', 'difficulty_level')
        }),
        ('Categorization', {
            'fields': ('cuisine_type', 'meal_type', 'dietary_tags')
        }),
        ('Time Information', {
            'fields': ('prep_time', 'cook_time')
        }),
        ('Metadata', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('author')
