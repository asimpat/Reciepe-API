
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegisterView, LoginView, ProfileView, UserDetailView,
                    FollowUserView, FollowersListView, FollowingListView)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('<str:username>/follow/', FollowUserView.as_view(),
         name='follow-user'),
    path('<str:username>/followers/', FollowersListView.as_view(),
         name='followers-list'),
    path('<str:username>/following/',
         FollowingListView.as_view(), name='following-list')
]
