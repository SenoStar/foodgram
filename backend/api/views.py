from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from recipes.models import (
    User,
    Tag,
    Recipe,
    Ingredient,
    Favorite,
    ShoppingCart
)
from .serializers import (
    CustomUserGetSerializer,
    AvatarUpdateSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
    TagGetSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)


class CurrentUserView(generics.RetrieveAPIView):
    """Получение и обновление информации о текущем пользователе."""

    serializer_class = CustomUserGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AvatarUpdateView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Обновление аватара текущего пользователя."""

    http_method_names = ['put', 'delete']
    serializer_class = AvatarUpdateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request):

        user = request.user
        serializer = self.get_serializer(
            user,
            data=request.data
        )

        if serializer.is_valid():
            user.avatar.delete()
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request):

        user = request.user
        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ModelViewSet):
    """Добавление подписки."""

    permission_classes = (IsAdminAuthorOrReadOnly,)

    def create(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = SubscribeSerializer(
            data={
                'user': request.user.id,
                'author': author.id
            },
            context={
                'request': request
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user.following.filter(author=author)

        if not follower:
            return Response(
                {
                    'error': 'Нет подписки на этого пользователя'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """Список подписок."""

    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """Тег."""

    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagGetSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    """Ингридиент."""

    http_method_names = ['get']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепт."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def get_short_link(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        short_link = f'foodgram-my-best-food.run.place/recipes/{recipe.id}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class FavoriteViewsSet(viewsets.ModelViewSet):
    """Избранный рецепт."""

    http_method_names = ['post', 'delete']
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {
                    'errors': 'Рецепт уже находится в избранном.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite = Favorite.objects.create(user=user, recipe=recipe)
        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe)

        if not favorite.exists():
            return Response(
                {
                    'errors': 'Рецепт не находится в избранном.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Cписок покупок."""

    http_method_names = ['post', 'delete', 'get']
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {
                    'errors': 'Рецепт уже находится в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item = ShoppingCart.objects.create(
            user=user,
            recipe=recipe
        )
        serializer = self.get_serializer(shopping_cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user
        shopping_cart_item = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )

        if not shopping_cart_item.exists():
            return Response(
                {
                    'errors': 'Рецепт не находится в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        ingredients = {}

        for item in shopping_cart_items:
            for ingredient in item.recipe.recipe_ingredients.all():
                name = ingredient.ingredient.name
                amount = ingredient.amount
                measurement_unit = ingredient.ingredient.measurement_unit
                if name in ingredients:
                    ingredients[name][0] += amount
                else:
                    ingredients[name] = [amount, measurement_unit]

        shopping_list = 'Список покупок: '
        for name in ingredients.keys():
            shopping_list += (
                f'{name}: '
                f'{ingredients[name][0]} '
                f'{ingredients[name][1]}.\n'
            )

        response = Response(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{user}_shopping_list.txt"'
        )
        return response
