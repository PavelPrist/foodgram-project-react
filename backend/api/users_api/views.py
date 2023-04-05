from api.paginations import CustomPageNumberPagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination


class BaseForFollowViewSets(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination


class FollowListViewSet(BaseForFollowViewSets):

    def get_queryset(self):
        return User.objects.filter(follower__follower=self.request.user)


class FollowCreateDestroyViewSet(
        generics.DestroyAPIView,
        generics.CreateAPIView,
        BaseForFollowViewSets,):

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        author = self.get_object()
        serializer = self.get_serializer(
            author, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.author.create(author=author)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, author):
        self.request.user.author.filter(author=author).delete()
