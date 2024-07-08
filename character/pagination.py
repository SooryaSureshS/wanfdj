from rest_framework import pagination


class CharacterPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'
