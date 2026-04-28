from django.shortcuts import render, redirect, HttpResponse
from project_one.models import Task, Adminrole
from project_one.utils.pagination import paginate


def task_list(request):
    user_role = request.unicom_role
    user_id = request.unicom_id
    
    if user_role in [2, 3]:
        queryset = Task.objects.all()
    else:
        queryset = Task.objects.filter(assignee_id=user_id)
    
    page_data = paginate(request, queryset, page_size=10, search_fields=['title', 'description'])
    return render(request, 'task/task_list.html', page_data)


def task_add(request):
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


def task_modify(request, nid):
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


def task_delete(request, nid):
    if request.unicom_role not in [2, 3]:
        return render(request, "permission_denied.html")
    
    Task.objects.filter(id=nid).delete()
    return redirect('/task/')