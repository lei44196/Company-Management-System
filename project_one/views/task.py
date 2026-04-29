from django.shortcuts import render, redirect, HttpResponse
from project_one.models import Task, Adminrole
from project_one.utils.pagination import paginate

# 导入Redis缓存装饰器
from project_one.utils.redis_cache import cache_invalidated


def task_list(request):
    """
    任务列表视图
    
    【角色权限】
    - 角色2（领导）、角色3（管理员）：查看所有任务
    - 角色1（员工）：只查看自己的任务
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 任务列表页面
    """
    user_role = request.unicom_role
    user_id = request.unicom_id

    if user_role in [2, 3]:
        queryset = Task.objects.all()
    else:
        queryset = Task.objects.filter(assignee_id=user_id)

    page_data = paginate(request, queryset, page_size=10, search_fields=['title', 'description'])
    return render(request, 'task/task_list.html', page_data)


def task_add(request):
    """
    添加任务视图
    
    【角色权限】
    - 仅角色2（领导）、角色3（管理员）可添加任务
    
    【注意】写操作，不使用缓存
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 添加任务页面或重定向到任务列表
    """
    if request.unicom_role not in [2, 3]:
        return render(request, "permission_denied.html")

    if request.method == 'GET':
        employees = Adminrole.objects.filter(role=1)
        return render(request, 'task/task_add.html', {'employees': employees})

    title = request.POST.get('title')
    description = request.POST.get('description')
    assignee_id = request.POST.get('assignee')
    deadline = request.POST.get('deadline')

    if not title or not description or not assignee_id or not deadline:
        employees = Adminrole.objects.filter(role=1)
        return render(request, 'task/task_add.html', {
            'employees': employees,
            'error': '请填写所有必填项'
        })

    Task.objects.create(
        title=title,
        description=description,
        assignee_id=assignee_id,
        deadline=deadline,
        creator_id=request.unicom_id
    )

    return redirect('/task/')


@cache_invalidated('Task', 'list')
def task_modify(request, nid):
    """
    修改任务视图
    
    【角色权限】
    - 仅角色2（领导）、角色3（管理员）可修改任务
    
    【缓存策略】
    - 使用@cache_invalidated装饰器清理相关缓存
    - 清理模式：project_one:Task:list:*
    
    Args:
        request: HTTP请求对象
        nid: 任务ID
    
    Returns:
        HttpResponse: 修改任务页面或重定向到任务列表
    """
    if request.unicom_role not in [2, 3]:
        return render(request, "permission_denied.html")

    task = Task.objects.filter(id=nid).first()
    if not task:
        return HttpResponse('任务不存在')

    if request.method == 'GET':
        employees = Adminrole.objects.filter(role=1)
        return render(request, 'task/task_modify.html', {
            'task': task,
            'employees': employees
        })

    title = request.POST.get('title')
    description = request.POST.get('description')
    assignee_id = request.POST.get('assignee')
    deadline = request.POST.get('deadline')
    status = request.POST.get('status')

    if not title or not description or not assignee_id or not deadline or status is None:
        employees = Adminrole.objects.filter(role=1)
        return render(request, 'task/task_modify.html', {
            'task': task,
            'employees': employees,
            'error': '请填写所有必填项'
        })

    task.title = title
    task.description = description
    task.assignee_id = assignee_id
    task.deadline = deadline
    task.status = int(status)
    task.save()

    return redirect('/task/')


@cache_invalidated('Task', 'list')
def task_delete(request, nid):
    """
    删除任务视图
    
    【角色权限】
    - 仅角色2（领导）、角色3（管理员）可删除任务
    
    【缓存策略】
    - 使用@cache_invalidated装饰器清理相关缓存
    - 清理模式：project_one:Task:list:*
    
    Args:
        request: HTTP请求对象
        nid: 任务ID
    
    Returns:
        HttpResponse: 重定向到任务列表
    """
    if request.unicom_role not in [2, 3]:
        return render(request, "permission_denied.html")

    Task.objects.filter(id=nid).delete()
    return redirect('/task/')