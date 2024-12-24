from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model
from posts.models import Post, Comment, Group, Follow
from .serializers import (
    PostSerializer, CommentSerializer,
    FollowSerializer, GroupSerializer)
from .permissions import IsAuthor

User = get_user_model()


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise PermissionDenied("Вы не можете изменять чужие комментарии.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Вы не можете удалить этот комментарий.')
        instance.delete()


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_username = self.request.data.get('following')  # type: ignore
        if following_username == self.request.user.username:  # type: ignore
            raise ValidationError('Нельзя подписаться на самого себя.')
        following_user = User.objects.filter(
            username=following_username).first()
        if not following_user:
            raise ValidationError('Пользователь для подписки не найден.')
        if Follow.objects.filter(user=self.request.user,
                                 following=following_user).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')
        serializer.save(user=self.request.user, following=following_user)


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
