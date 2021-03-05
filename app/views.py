from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from app.filters import ConditionFilter, FilterObj, str_to_time
from app.serializer import SearchUserSerializer
from app.models import User

class SearchUser(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SearchUserSerializer
    filter_backends = (filters.SearchFilter, ConditionFilter)
    search_fields = ('name', 'age', 'relation_user__name', )

    filter_fields = (
        FilterObj(arg_field='name', desc='名称'),
        FilterObj(arg_field='min_created_time', condition='created_time__gte', desc='创建时间范围', data_type='time'),
        FilterObj(arg_field='max_created_time', condition='created_time__lte', desc='创建时间范围', data_type='time'),
    )

class SearchUser2(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SearchUserSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', 'age', 'relation_user__name', )

    def list(self, request, *args, **kwargs):
        query_params = self.request.query_params
        queryset = self.filter_queryset(self.get_queryset())
        name = query_params.get('name')
        min_created_time = query_params.get('min_created_time')
        max_created_time = query_params.get('max_created_time')
        if name:
            queryset = queryset.filter(name=name)
        if min_created_time:
            min_created_time = str_to_time(min_created_time)
            queryset = queryset.filter(created_time__gte=min_created_time)
        if max_created_time:
            max_created_time = str_to_time(max_created_time)
            queryset = queryset.filter(created_time__lte=max_created_time)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)