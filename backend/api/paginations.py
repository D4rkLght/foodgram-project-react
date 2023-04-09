from rest_framework import pagination
from rest_framework.response import Response


class Paginator(pagination.PageNumberPagination):
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return Response(data)
