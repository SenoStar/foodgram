from drf_extra_fields.fields import Base64ImageField
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.constants import MIN_VALUE
from recipes.models import (
    User,
    Subscription,
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)
from .validators import validate_password_length


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    password = serializers.CharField(
        validators=[validate_password_length],
        write_only=True
    )

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserGetSerializer(UserSerializer):
    """Сериализатор получения пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.follower.filter(user=request.user).exists()
        return False

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления подписки."""

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return SubscriptionsSerializer(
            instance.author,
            context={
                'request':
                    request
            }
        ).data

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя',
            )
        ]


class SubscriptionsSerializer(CustomUserGetSerializer):
    """Сериализатор списка подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.authored_recipes.all()
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                recipes = recipes[:int(recipes_limit)]
        return RecipeSubscriptionsSerializer(
            recipes,
            many=True,
            context={
                'request': request
            }
        ).data

    def get_recipes_count(self, obj):
        return obj.authored_recipes.count()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )


class TagGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор получения доступных ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(
        source='ingredient'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/изменения рецепта."""

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientPostSerializer(
        many=True,
        source='recipe_ingredients',
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE
    )

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=request.user,
                **validated_data
            )
            recipe.tags.set(tags)
            ingredient_list = [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(
                        id=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount'),
                ) for ingredient in ingredients
            ]
            RecipeIngredient.objects.bulk_create(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')

        instance.tags.clear()
        instance.tags.set(tags)

        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)

        ingredient_list = [
            RecipeIngredient(
                recipe=instance,
                ingredient=Ingredient.objects.get(
                    id=ingredient.get('id')
                ),
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredient_list)

        instance.save()
        return instance

    def validate(self, data):
        if not self.initial_data.get('ingredients'):
            raise ValidationError('Добавьте хотя бы 1 ингредиент!')
        if not self.initial_data.get('tags'):
            raise ValidationError('Добавьте хотя бы 1 тег!')
        if not self.initial_data.get('image'):
            raise ValidationError(
                'Изображение обязательно для добавления рецепта!'
            )
        return data

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise ValidationError('Такого ингредиента нет!')
            if ingredient in ingredients_list:
                raise ValidationError('Ингредиенты не должны повторятся!')
            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError('Теги не должны повторятся!')
        return tags

    def to_representation(self, instance):
        request = self.context.get('request')
        return {
            'id': instance.id,
            'name': instance.name,
            'text': instance.text,
            'image': instance.image.url,
            'cooking_time': instance.cooking_time,
            'is_favorited': False,
            'is_in_shopping_cart': False,
            'author': {
                'id': instance.author.id,
                'username': instance.author.username,
                'first_name': instance.author.first_name,
                'last_name': instance.author.last_name,
                'email': instance.author.email,
                'is_subscribed': False,
                'avatar': instance.author.avatar.url
                if instance.author.avatar else None,
            },
            'tags': TagGetSerializer(
                instance.tags,
                many=True,
                context={'request': request}
            ).data,
            'ingredients': IngredientGetSerializer(
                instance.recipe_ingredients.all(),
                many=True
            ).data,
        }

    class Meta:
        model = Recipe
        fields = (
            'name',
            'text',
            'cooking_time',
            'image',
            'ingredients',
            'tags'
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецепта."""

    ingredients = IngredientGetSerializer(
        many=True,
        source='recipe_ingredients',
    )
    tags = TagGetSerializer(
        many=True
    )
    author = CustomUserGetSerializer(
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeSubscriptionsSerializer(RecipeGetSerializer):
    """Сериализатор получения рецепта в подписках."""

    class Meta(RecipeGetSerializer.Meta):
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в избранные."""

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSubscriptionsSerializer(
            instance.recipe, context={'request': request}
        ).data

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже находится в избранном',
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSubscriptionsSerializer(
            instance.recipe, context={'request': request}
        ).data

    class Meta:
        model = ShoppingCart
        fields = '__all__'
