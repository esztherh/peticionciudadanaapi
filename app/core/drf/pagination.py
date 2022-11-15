from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.urls import replace_query_param


class PaginationPeticionCiudadana(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.get_previous_link(),
            'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            'count': self.page.paginator.count,
            'current_page': int(self.get_page_number(self.request, self.page.paginator)),
            'page_size': self.get_page_size(self.request),
            'url': replace_query_param(self.request.build_absolute_uri(), self.page_query_param, "number"),
            'results': data
        })
