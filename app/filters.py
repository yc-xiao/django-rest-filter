"""
    1.参考rest_framework.filters.SearchFilter用法
    2.重构filter_queryset()方法
    3.ConditionFilter过滤需要搭配FilterObj使用
    Example:
        class SearchUser(viewsets.ModelViewSet):
            filter_backends = (ConditionFilter, )
            filter_fields = (
                FilterObj(arg_field='name', desc='名称'),
                FilterObj(arg_field='min_created_time', condition='created_time__gte', desc='创建时间范围', data_type='time'),
                FilterObj(arg_field='max_created_time', condition='created_time__lte', desc='创建时间范围', data_type='time'),
            )
    PS: FilterObj(arg_field='max_created_time', condition='created_time__lte', desc='创建时间范围', data_type='time')
    PS: 最后转化为 Q(created_time_lte=max_created_time)
"""

from django.core.exceptions import ValidationError
from functools import reduce
from django.db.models import Q

import operator
import time


def str_to_time(value):
    time_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
    for time_format in time_formats:
        try:
            value = time.strptime(value, time_format)
            return value
        except ValueError:
            continue
    return None


class FilterObj(object):
    def __init__(self, arg_field=None, condition=None, value=None, desc=None, func=None,
                 data_type='str', *args, **kw):
        """
            arg_field 定义接口参数名称
            condition 补充对应查询条件
            desc      字段描述，可忽略
            value     参数可设置默认值
            func      通过指定函数处理参数，优先级最高
            data_type 指定字段类型，用于参数类型装换
        """
        self.arg_field = arg_field
        self.condition = condition if condition else arg_field  
        self.desc = desc  
        self.value = value  
        self.func = func    
        self.data_type = data_type  

    def handler_datas(self, values):
        func_name = 'handler_%s_datas' % self.data_type     # 根据类型处理数据
        handler_func = getattr(self, func_name, self.handler_str_datas)
        handler_func = self.func if self.func else handler_func  # 传入的函数优先级最高
        values = handler_func(values)
        values = values if isinstance(values, list) else [values]
        return values or []

    def handler_str_datas(self, values):
        # 处理str类型的数据
        return values.split(',')

    def handler_bool_datas(self, value):
        # 处理bool类型的数据
        if isinstance(value, bool):
            return value
        if value.lower() in ['false', 'False']:
            return False
        if value.lower() in ['true', 'True']:
            return True
        return None

    def handler_time_datas(self, value):
        # 处理时间类型
        return value if str_to_time(value) else None

    def handler_int_datas(self, values):
        # 处理int类型的数据
        new_values = []
        for value in values.split(','):
            try:
                value = int(value)
            except ValueError:
                continue
            new_values.append(value)
        return new_values


class ConditionFilter(object):
    def filter_queryset(self, request, queryset, view):
        query_params = view.request.query_params
        if not hasattr(view, 'filter_fields'):
            return queryset
        for obj in view.filter_fields:
            if request.method == 'GET':
                values = query_params.get(obj.arg_field)
            else:
                values = request.data.get(obj.arg_field)

            values = values if values else obj.value
            if not values:
                continue
            values = obj.handler_datas(values)
            conditions = [Q(**{obj.condition: value}) for value in values if value is not None]
            if conditions:
                try:
                    queryset = queryset.filter(reduce(operator.or_, conditions))
                except ValidationError:
                    return queryset
        return queryset
