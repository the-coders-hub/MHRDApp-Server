from rest_framework.pagination import CursorPagination


class DefaultPaginationClass(CursorPagination):

    page_size = 20
