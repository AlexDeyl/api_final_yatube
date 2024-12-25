from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from posts.models import Comment, Group, Follow, Post
from .permissions import IsAuthor
from .serializers import (
    PostSerializer, CommentSerializer,
    FollowSerializer, GroupSerializer)

User = get_user_model()


class CommentViewSet(ModelViewSet):
    """
    ViewSet для управления комментариями.
    Поддерживает операции CRUD для комментариев, связанных с конкретным постом.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)

    def get_queryset(self):
        """Возвращает комментарии, связанные с определенным постом."""
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        """Создает комментарий для заданного поста."""
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
    """
    ViewSet для управления постами.
    Поддерживает операции CRUD. Реализована пагинация.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """Создает пост от имени текущего пользователя."""
        serializer.save(author=self.request.user)


class FollowViewSet(ModelViewSet):
    """
    ViewSet для управления подписками.
    Поддерживает операции создания и чтения подписок.
    Реализован поиск по username.
    """
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ['following__username']

    def get_queryset(self):
        """Возвращает подписки текущего пользователя."""
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Создает подписку от имени текущего пользователя."""
        serializer.save(user=self.request.user)


class GroupViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для управления группами.
    Поддерживает только операции чтения.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
