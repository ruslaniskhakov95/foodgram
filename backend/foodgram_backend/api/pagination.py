from rest_framework import pagination


class RecipeLimitOffset(pagination.LimitOffsetPagination):
    default_limit = 2
    limit_query_param = 'recipe_limit'
    offset_query_param = 'recipe_offset'
    max_limit = 100
