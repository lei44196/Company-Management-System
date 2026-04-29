from django.shortcuts import render, redirect
from project_one.utils.pagination import paginate
from project_one import models

# 导入Redis缓存装饰器
from project_one.utils.redis_cache import cache_invalidated


def index(request):
    """
    首页视图
    
    提供统计数据、最近任务、最近绩效和部门分布信息
    """
    # 统计数据
    stat_data = {
        'depart_count': models.Department.objects.count(),
        'user_count': models.Userinfo.objects.count(),
        'asset_count': models.Assets.objects.count(),
        'task_count': models.Task.objects.filter(status__lt=2).count(),
    }
    
    # 最近任务（取最近5条）
    recent_tasks = models.Task.objects.order_by('-id')[:5]
    
    # 最近绩效（取最近5条）
    recent_performs = models.Perform.objects.order_by('-id')[:5]
    
    # 部门人员分布统计
    depart_stats = []
    departments = models.Department.objects.all()
    total_users = models.Userinfo.objects.count()
    colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6']
    
    for i, depart in enumerate(departments):
        user_count = models.Userinfo.objects.filter(depart_id=depart.id).count()
        percentage = round((user_count / total_users) * 100) if total_users > 0 else 0
        depart_stats.append({
            'name': depart.title,
            'count': user_count,
            'percentage': percentage,
            'color': colors[i % len(colors)]
        })
    
    return render(request, 'index/index.html', {
        'stat_data': stat_data,
        'recent_tasks': recent_tasks,
        'recent_performs': recent_performs,
        'depart_stats': depart_stats,
    })


def depart_list(request):
    """
    部门列表视图
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 部门列表页面
    """
    queryset = models.Department.objects.all()
    page_data = paginate(request, queryset, page_size=10, search_fields=['title'])
    return render(request, 'depart/depart_list.html', page_data)


def depart_add(request):
    """
    添加部门视图
    
    【注意】写操作，不使用缓存
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 添加部门页面或重定向到部门列表
    """
    if request.method == "GET":
        title = "添加部门"
        return render(request, 'depart/depart_add_modify.html', {'title': title})

    title = request.POST.get('title')
    models.Department.objects.create(title=title)
    return redirect("/depart/")


@cache_invalidated('Department', 'list')
def depart_del(request, nid):
    """
    删除部门视图
    
    【缓存策略】
    - 使用@cache_invalidated装饰器清理相关缓存
    - 清理模式：project_one:Department:list:*
    
    Args:
        request: HTTP请求对象
        nid: 部门ID
    
    Returns:
        HttpResponse: 重定向到部门列表
    """
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/")


@cache_invalidated('Department', 'list')
def depart_modify(request, nid):
    """
    修改部门视图
    
    【缓存策略】
    - 使用@cache_invalidated装饰器清理相关缓存
    - 清理模式：project_one:Department:list:*
    
    Args:
        request: HTTP请求对象
        nid: 部门ID
    
    Returns:
        HttpResponse: 修改部门页面或重定向到部门列表
    """
    if request.method == "GET":
        title = "修改部门"
        name = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart/depart_add_modify.html', {'title': title, 'name': name})

    title = request.POST.get('title')
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/")