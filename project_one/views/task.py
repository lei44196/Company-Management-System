# 导入Django的快捷函数，用于渲染模板、重定向和返回HTTP响应
from django.shortcuts import render, redirect, HttpResponse
# 导入Task和Adminrole模型，用于操作任务和用户数据
from project_one.models import Task, Adminrole
# 导入自定义的分页工具函数，用于实现分页功能
from project_one.utils.pagination import paginate


# 任务列表视图函数
# 功能：展示任务数据，支持分页和搜索，根据用户角色显示不同的任务
# 流程：1. 获取用户角色和ID 2. 根据角色筛选任务 3. 使用分页工具处理数据 4. 渲染模板显示数据
# 前端交互：当用户访问任务列表页面时，根据用户角色显示相应的任务列表
def task_list(request):
    """任务列表视图"""
    # 获取当前用户角色，从中间件中设置
    user_role = request.unicom_role
    # 获取当前用户ID，从中间件中设置
    user_id = request.unicom_id
    
    # 根据角色过滤任务
    # 领导和管理员可以看到所有任务
    if user_role in [2, 3]:  # 2是领导，3是管理员
        # 使用all()方法获取所有任务记录
        queryset = Task.objects.all()
    # 普通员工只能看到分配给自己的任务
    else:  # 1是员工
        # 使用filter()方法筛选分配给当前用户的任务
        # 使用filter()而不用get()是因为可能有多个任务分配给同一用户
        queryset = Task.objects.filter(assignee_id=user_id)
    
    # 使用自定义的paginate函数处理分页和搜索
    # 参数说明：request对象、查询集、每页显示条数、搜索字段
    page_data = paginate(request, queryset, page_size=10, search_fields=['title', 'description'])
    
    # 渲染任务列表模板，传递分页后的数据
    return render(request, 'task/task_list.html', page_data)


# 任务添加视图函数
# 功能：处理添加任务的请求，只有领导和管理员可以添加任务
# 流程：1. 检查权限 2. GET请求时显示表单 3. POST请求时处理表单数据 4. 验证通过后保存数据并重定向
# 前端交互：当用户点击"添加任务"按钮时，跳转到该视图，提交表单后保存数据
def task_add(request):
    """添加任务视图"""
    # 检查权限，只有领导和管理员可以添加任务
    if request.unicom_role not in [2, 3]:
        # 权限不足，返回权限拒绝页面
        return render(request, "permission_denied.html")
    
    # 处理GET请求，显示添加表单
    if request.method == 'GET':
        # 获取所有员工列表，用于下拉选择
        # 使用filter()方法筛选角色为1的用户（员工）
        employees = Adminrole.objects.filter(role=1)
        # 渲染添加表单模板，传递员工列表
        return render(request, 'task/task_add.html', {'employees': employees})
    
    # 处理POST请求，保存表单数据
    # 从POST请求中获取表单数据
    title = request.POST.get('title')  # 任务标题
    description = request.POST.get('description')  # 任务描述
    assignee_id = request.POST.get('assignee')  # 接收任务的员工ID
    deadline = request.POST.get('deadline')  # 截止日期
    
    # 验证必填项
    if not title or not description or not assignee_id or not deadline:
        # 验证失败，重新渲染表单并显示错误信息
        employees = Adminrole.objects.filter(role=1)
        return render(request, 'task/task_add.html', {
            'employees': employees,
            'error': '请填写所有必填项'
        })
    
    # 创建任务
    # 使用create()方法创建新任务记录
    Task.objects.create(
        title=title,  # 任务标题
        description=description,  # 任务描述
        assignee_id=assignee_id,  # 接收任务的员工
        deadline=deadline,  # 截止日期
        creator_id=request.unicom_id  # 创建任务的用户
    )
    
    # 重定向到任务列表页面
    return redirect('/task/')


# 任务修改视图函数
# 功能：处理修改任务的请求，只有领导和管理员可以修改任务
# 流程：1. 检查权限 2. 获取任务对象 3. GET请求时显示表单 4. POST请求时处理表单数据 5. 验证通过后更新数据并重定向
# 前端交互：当用户点击列表页的"修改"按钮时，跳转到该视图，提交表单后更新数据
def task_modify(request, nid):
    """修改任务视图"""
    # 检查权限，只有领导和管理员可以修改任务
    if request.unicom_role not in [2, 3]:
        # 权限不足，返回权限拒绝页面
        return render(request, "permission_denied.html")
    
    # 获取任务对象
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
    task = Task.objects.filter(id=nid).first()
    # 如果任务不存在，返回错误信息
    if not task:
        return HttpResponse('任务不存在')
    
    # 处理GET请求，显示修改表单
    if request.method == 'GET':
        # 获取所有员工列表，用于下拉选择
        employees = Adminrole.objects.filter(role=1)
        # 渲染修改表单模板，传递任务数据和员工列表
        return render(request, 'task/task_modify.html', {
            'task': task,
            'employees': employees
        })
    
    # 处理POST请求，保存表单数据
    # 从POST请求中获取表单数据
    title = request.POST.get('title')  # 任务标题
    description = request.POST.get('description')  # 任务描述
    assignee_id = request.POST.get('assignee')  # 接收任务的员工ID
    deadline = request.POST.get('deadline')  # 截止日期
    status = request.POST.get('status')  # 任务状态
    
    # 验证必填项
    if not title or not description or not assignee_id or not deadline or status is None:
        # 验证失败，重新渲染表单并显示错误信息
        employees = Adminrole.objects.filter(role=1)
        return render(request, 'task/task_modify.html', {
            'task': task,
            'employees': employees,
            'error': '请填写所有必填项'
        })
    
    # 更新任务
    # 直接修改任务对象的属性
    task.title = title  # 更新任务标题
    task.description = description  # 更新任务描述
    task.assignee_id = assignee_id  # 更新接收任务的员工
    task.deadline = deadline  # 更新截止日期
    task.status = int(status)  # 更新任务状态，转换为整数类型
    # 保存更新后的任务对象
    task.save()
    
    # 重定向到任务列表页面
    return redirect('/task/')


# 任务删除视图函数
# 功能：处理删除任务的请求，只有领导和管理员可以删除任务
# 流程：1. 检查权限 2. 根据ID删除任务数据 3. 重定向到任务列表页面
# 前端交互：当用户点击列表页的"删除"按钮时，前端会发送请求到当前视图，后端接收ID参数后执行删除操作并返回结果
def task_delete(request, nid):
    """删除任务视图"""
    # 检查权限，只有领导和管理员可以删除任务
    if request.unicom_role not in [2, 3]:
        # 权限不足，返回权限拒绝页面
        return render(request, "permission_denied.html")
    
    # 删除任务
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常
    Task.objects.filter(id=nid).delete()
    
    # 重定向到任务列表页面
    return redirect('/task/')
