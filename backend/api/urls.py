from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserView,
    AvatarUpdateView,
    SubscribeViewSet,
    SubscriptionsViewSet,
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    FavoriteViewsSet,
    ShoppingCartViewSet
)

router = DefaultRouter()
router.register(
    'users',
    UserViewSet,
    basename='users'
)
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

current_user_urlpatterns = [
    path(
        'me/',
        CurrentUserView.as_view(),
        name='current_user'
    ),
    path(
        'me/avatar/',
        AvatarUpdateView.as_view(),
        name='avatar_update'
    ),
    path(
        '<int:user_id>/subscribe/',
        SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='subscribe'
    ),
    path(
        'subscriptions/',
        SubscriptionsViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    )
]

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:recipe_id>/get-link/',
        RecipeViewSet.as_view({'get': 'get_short_link'}),
        name='get_short_link'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewsSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(
            {
                'post': 'create',
                'delete': 'destroy'
            }
        ),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartViewSet.as_view(
            {
                'get': 'download_shopping_cart'
            }
        ),
        name='download_shopping_cart'
    ),
    path('users/', include(current_user_urlpatterns)),
    path('', include(router.urls)),
]
