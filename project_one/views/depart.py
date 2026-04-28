from django.shortcuts import render, redirect
from project_one.utils.pagination import paginate
from project_one import models


def index(request):
    return render(request, 'index/index.html')


def depart_list(request):
    queryset = models.Department.objects.all()
    page_data = paginate(request, queryset, page_size=10, search_fields=['title'])
    return render(request, 'depart/depart_list.html', page_data)


def depart_add(request):
    if request.method == "GET":
        title = "添加部门"
        return render(request, 'depart/depart_add_modify.html', {'title': title})
    
    title = request.POST.get('title')
    models.Department.objects.create(title=title)
    return redirect("/depart/")


def depart_del(request, nid):
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/")


def depart_modify(request, nid):
    if request.method == "GET":
        title = "修改部门"
        name = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart/depart_add_modify.html', {'title': title, 'name': name})
    
    title = request.POST.get('title')
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/")