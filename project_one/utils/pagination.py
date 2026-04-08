# 导入Django的安全字符串处理函数，用于标记HTML为安全的
from django.utils.safestring import mark_safe  # 用于将HTML字符串标记为安全，避免Django自动转义
from django.db.models import Q  # 用于构建复杂的查询条件


def paginate(request, queryset, page_size=10, search_fields=None):
    """分页工具函数
    功能：实现数据的分页显示和搜索功能
    参数：
        request: 请求对象，用于获取GET参数
        queryset: 查询集，需要分页的数据
        page_size: 每页显示的记录数，默认10条
        search_fields: 搜索字段列表，用于构建搜索条件
    返回值：包含分页数据的字典，包括：
        data_list: 当前页的数据列表
        page_html: 分页导航的HTML字符串
        total_count: 总记录数
        page: 当前页码
        page_count: 总页数
        search_value: 搜索关键词
    
    实现步骤：
    1. 获取搜索关键词
    2. 构建搜索条件并筛选数据
    3. 计算总记录数和总页数
    4. 获取并修正页码参数
    5. 计算数据切片范围并获取当前页数据
    6. 生成分页导航HTML
    7. 返回包含分页数据的字典
    
    使用场景：
    - 当需要在前端显示大量数据时，使用此函数进行分页处理
    - 当需要在列表页面添加搜索功能时，使用此函数处理搜索逻辑
    - 适用于项目中的各种列表页面，如员工列表、资产列表、任务列表等
    """
    # 获取搜索关键词，从GET参数中获取'search'字段，默认为空字符串
    search_value = request.GET.get('search', '')
    
    # 构建搜索条件
    if search_value and search_fields:
        q = Q()  # 创建Q对象，用于构建复杂查询
        for field in search_fields:
            # 为每个搜索字段添加包含搜索条件（icontains表示不区分大小写的包含）
            q |= Q(**{f"{field}__icontains": search_value})  # 使用**{key: value}动态构建关键字参数
        # 根据搜索条件筛选数据
        queryset = queryset.filter(q)
    
    # 获取总记录数
    total_count = queryset.count()
    
    # 计算总页数
    page_count, div = divmod(total_count, page_size)  # divmod返回商和余数
    if div:  # 如果有余数，总页数加1
        page_count += 1
    if page_count == 0:  # 避免空数据时分页栏显示0页
        page_count = 1
    
    # 获取页码参数
    try:
        page = int(request.GET.get('page', 1))  # 从GET参数中获取'page'字段，默认值为1
    except ValueError:  # 处理页码不是数字的情况
        page = 1
    
    # 修正页码范围，确保页码在有效范围内
    if page < 1:
        page = 1
    if page > page_count:
        page = page_count
    
    # 计算切片范围，用于从查询集中获取当前页的数据
    start = (page - 1) * page_size  # 起始索引
    end = page * page_size  # 结束索引
    data_list = queryset[start:end]  # 使用切片获取当前页数据
    
    # 生成分页HTML
    page_str_list = []  # 用于存储分页HTML片段
    
    # 首页按钮
    if page > 1:  # 如果当前页不是第一页，显示首页按钮
        first_url = f'?page=1'  # 首页URL
        if search_value:  # 如果有搜索关键词，添加到URL中
            first_url += f'&search={search_value}'
        # 添加首页按钮的HTML
        page_str_list.append(
            f'<li><a href="{first_url}" aria-label="First"><span aria-hidden="true">&laquo;&laquo;</span></a></li>')
    else:  # 如果当前页是第一页，禁用首页按钮
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&laquo;&laquo;</span></li>')
    
    # 上一页按钮
    if page > 1:  # 如果当前页不是第一页，显示上一页按钮
        prev_url = f'?page={page - 1}'  # 上一页URL
        if search_value:  # 如果有搜索关键词，添加到URL中
            prev_url += f'&search={search_value}'
        # 添加上一页按钮的HTML
        page_str_list.append(
            f'<li><a href="{prev_url}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>')
    else:  # 如果当前页是第一页，禁用上一页按钮
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&laquo;</span></li>')
    
    # 页码显示范围（当前页前后各2页）
    start_page = max(1, page - 2)  # 起始页码，最小为1
    end_page = min(page_count, page + 2)  # 结束页码，最大为总页数
    
    # 生成页码按钮
    for num in range(start_page, end_page + 1):
        url = f'?page={num}'  # 页码URL
        if search_value:  # 如果有搜索关键词，添加到URL中
            url += f'&search={search_value}'
        if num == page:  # 如果是当前页，添加active类
            page_str_list.append(f'<li class="active"><a href="{url}">{num}</a></li>')
        else:  # 否则，添加普通页码按钮
            page_str_list.append(f'<li><a href="{url}">{num}</a></li>')
    
    # 下一页按钮
    if page < page_count:  # 如果当前页不是最后一页，显示下一页按钮
        next_url = f'?page={page + 1}'  # 下一页URL
        if search_value:  # 如果有搜索关键词，添加到URL中
            next_url += f'&search={search_value}'
        # 添加下一页按钮的HTML
        page_str_list.append(
            f'<li><a href="{next_url}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>')
    else:  # 如果当前页是最后一页，禁用下一页按钮
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&raquo;</span></li>')
    
    # 尾页按钮
    if page < page_count:  # 如果当前页不是最后一页，显示尾页按钮
        last_url = f'?page={page_count}'  # 尾页URL
        if search_value:  # 如果有搜索关键词，添加到URL中
            last_url += f'&search={search_value}'
        # 添加尾页按钮的HTML
        page_str_list.append(
            f'<li><a href="{last_url}" aria-label="Last"><span aria-hidden="true">&raquo;&raquo;</span></a></li>')
    else:  # 如果当前页是最后一页，禁用尾页按钮
        page_str_list.append('<li class="disabled"><span aria-hidden="true">&raquo;&raquo;</span></li>')
    
    # 将分页HTML片段连接成完整的HTML字符串，并标记为安全
    page_html = mark_safe(''.join(page_str_list))  # mark_safe确保Django不会转义HTML
    
    # 返回结果字典，包含分页相关数据
    return {
        'data_list': data_list,  # 当前页的数据列表
        'page_html': page_html,  # 分页导航的HTML字符串
        'total_count': total_count,  # 总记录数
        'page': page,  # 当前页码
        'page_count': page_count,  # 总页数
        'search_value': search_value  # 搜索关键词
    }