from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Настройка для пагинатора."""

    page_size_query_param = 'limit'
