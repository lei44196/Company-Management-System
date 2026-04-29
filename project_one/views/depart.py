from django.shortcuts import render, redirect
from project_one.utils.pagination import paginate
from project_one import models

# 导入Redis缓存装饰器
from project_one.utils.redis_cache import cache_invalidated


def index(request):
    """首页视图"""
    return render(request, 'index/index.html')


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