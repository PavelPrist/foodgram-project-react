from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, mixins, viewsets, generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.response import Response

from .models import User
from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class BaseForFollowViewSets(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class FollowListViewSet(BaseForFollowViewSets):

    def get_queryset(self):
        return User.objects.filter(follower__follower=self.request.user)


class FollowCreateDestroyViewSet(
        generics.DestroyAPIView,
        generics.CreateAPIView,
        BaseForFollowViewSets,):

    def get_queryset(self):
        return self.request.user.author.select_related('follower')

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        author = self.get_object()
        if request.user.id == author.id:
            return Response(
                {'errors': 'Невозможно подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user.author.filter(author=author).exists():
            return Response(
                {'errors': 'Подписаться повторно на одного автора невозможно'},
                status=status.HTTP_400_BAD_REQUEST)
        subscribe_obj = request.user.author.create(author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, author):
        self.request.user.author.filter(author=author).delete()

