from django.utils.safestring import mark_safe
from django.db.models import Q


def paginate(request, queryset, page_size=10, search_fields=None):
    """分页工具函数
    
    Args:
        request: 请求对象
        queryset: 查询集
        page_size: 每页记录数，默认10
        search_fields: 搜索字段列表
    
    Returns:
        dict: 包含分页数据的字典
    """
    search_value = request.GET.get('search', '')
    
    if search_value and search_fields:
        q = Q()
        for field in search_fields:
            q |= Q(**{f"{field}__icontains": search_value})
        queryset = queryset.filter(q)
    
    total_count = queryset.count()
    page_count, div = divmod(total_count, page_size)
    if div:
        page_count += 1
    if page_count == 0:
        page_count = 1
    
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    
    if page < 1:
        page = 1
    if page > page_count:
        page = page_count
    
    start = (page - 1) * page_size
    end = page * page_size
    data_list = queryset[start:end]
    
    page_str_list = []
    
    if page > 1:
        first_url = f'?page=1'
        if search_value:
            first_url += f'&search={search_value}'
        page_str_list.append(
            f'<li><a href="{first_url}" aria-label="First"><span aria-hidden="true">&laquo;&laquo;</span></a></li>')
    else:
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&laquo;&laquo;</span></li>')
    
    if page > 1:
        prev_url = f'?page={page - 1}'
        if search_value:
            prev_url += f'&search={search_value}'
        page_str_list.append(
            f'<li><a href="{prev_url}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>')
    else:
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&laquo;</span></li>')
    
    start_page = max(1, page - 2)
    end_page = min(page_count, page + 2)
    
    for num in range(start_page, end_page + 1):
        url = f'?page={num}'
        if search_value:
            url += f'&search={search_value}'
        if num == page:
            page_str_list.append(f'<li class="active"><a href="{url}">{num}</a></li>')
        else:
            page_str_list.append(f'<li><a href="{url}">{num}</a></li>')
    
    if page < page_count:
        next_url = f'?page={page + 1}'
        if search_value:
            next_url += f'&search={search_value}'
        page_str_list.append(
            f'<li><a href="{next_url}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>')
    else:
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&raquo;</span></li>')
    
    if page < page_count:
        last_url = f'?page={page_count}'
        if search_value:
            last_url += f'&search={search_value}'
        page_str_list.append(
            f'<li><a href="{last_url}" aria-label="Last"><span aria-hidden="true">&raquo;&raquo;</span></a></li>')
    else:
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&raquo;&raquo;</span></li>')
    
    page_html = mark_safe(''.join(page_str_list))
    
    return {
        'data_list': data_list,
        'page_html': page_html,
        'total_count': total_count,
        'page': page,
        'page_count': page_count,
        'search_value': search_value
    }