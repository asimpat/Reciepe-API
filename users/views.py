from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, FollowSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "User registered successfully!",
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    # """
    # GET: Retrieve user profile
    # PUT/PATCH: Update user profile
    # """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Profile updated successfully!",
            "user": serializer.data
        })


class UserDetailView(generics.RetrieveAPIView):
    """
    View any user's public profile
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'


class FollowUserView(APIView):
    # """
    # POST: Follow/unfollow a user (toggle)
    # GET: Check if you're following a user
    # """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        """Check if current user is following this user"""
        user_to_check = get_object_or_404(User, username=username)
        is_following = request.user.following.filter(
            id=user_to_check.id).exists()

        return Response({
            "is_following": is_following
        })

    def post(self, request, username):
        """Toggle follow/unfollow"""
        user_to_follow = get_object_or_404(User, username=username)

        # Can't follow yourself
        if user_to_follow == request.user:
            return Response({
                "error": "You cannot follow yourself."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if already following
        if request.user.following.filter(id=user_to_follow.id).exists():
            # Unfollow
            request.user.following.remove(user_to_follow)
            return Response({
                "message": f"You have unfollowed {user_to_follow.username}.",
                "is_following": False
            }, status=status.HTTP_200_OK)
        else:
            # Follow
            request.user.following.add(user_to_follow)
            return Response({
                "message": f"You are now following {user_to_follow.username}!",
                "is_following": True
            }, status=status.HTTP_200_OK)

 
class FollowersListView(generics.ListAPIView):
    # """
    # GET: List all followers of a user 
    # """
    serializer_class = FollowSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.followers.all()

    def list(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "user": username,
            "followers_count": queryset.count(),
            "followers": serializer.data
        })


class FollowingListView(generics.ListAPIView):
    # """
    # GET: List all users that a user is following
    # """
    serializer_class = FollowSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.following.all()

    def list(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "user": username,
            "following_count": queryset.count(),
            "following": serializer.data
        })
