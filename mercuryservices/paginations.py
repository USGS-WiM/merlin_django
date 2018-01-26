from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = None


class UnlimitedResultsSetPagination(PageNumberPagination):
    page_size = None
