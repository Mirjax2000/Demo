from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """PageNumberPagination with client-controllable page_size."""

    page_size_query_param = "page_size"
    max_page_size = 200
