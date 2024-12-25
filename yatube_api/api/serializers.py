from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from posts.models import Comment, Group, Follow, Post


User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.
    Обрабатывает операции создания и отображения комментариев.
    """
    author = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'post', 'created')

    def create(self, validated_data):
        """Создает комментарий с указанием текущего пользователя как автора."""
        request = self.context.get('request')
        validated_data['author'] = request.user  # type: ignore
        return super().create(validated_data)


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Follow.
    Управляет процессом создания и валидации подписок.
    """
    user = serializers.ReadOnlyField(source='user.username')
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate_following(self, following_user):
        if self.context['request'].user == following_user:
            raise serializers.ValidationError('Вы не можете подписаться '
                                              'на самого себя.')
        if Follow.objects.filter(user=self.context['request'].user,
                                 following=following_user).exists():
            raise serializers.ValidationError('Вы уже подписаны '
                                              'на этого пользователя.')
        return following_user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')
