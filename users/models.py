from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For following system 
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-created_at']
    
    @property
    def followers_count(self):
        # """Get number of followers"""
        return self.followers.count()
    
    @property
    def following_count(self):
        # """Get number of users this user is following"""
        return self.following.count()
