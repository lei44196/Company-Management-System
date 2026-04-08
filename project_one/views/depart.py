# 导入tkinter的font模块（虽然导入但未使用）
from tkinter.font import names

# 导入Django的快捷函数，用于渲染模板和重定向
from django.shortcuts import render, redirect
# 导入matplotlib的pyplot模块（虽然导入但未使用）
from matplotlib.pyplot import title
# 导入自定义的分页工具函数，用于实现分页功能
from project_one.utils.pagination import paginate
# 导入项目的models模块，用于操作数据库
from project_one import models


# 首页视图函数
# 功能：显示项目首页
# 流程：直接渲染首页模板
# 前端交互：当用户访问项目根路径时，显示首页
def index(request):
    # 渲染首页模板
    return render(request, 'index/index.html')


# 部门列表视图函数
# 功能：展示所有部门数据，支持分页和搜索
# 流程：1. 获取所有部门数据 2. 使用分页工具处理数据 3. 渲染模板显示数据
# 前端交互：当用户访问部门列表页面时，显示所有部门数据，支持分页和搜索
def depart_list(request):
    # 获取所有部门数据
    # 使用all()方法获取所有记录，因为我们需要展示所有部门
    queryset = models.Department.objects.all()
    # 使用自定义的paginate函数处理分页和搜索
    # 参数说明：request对象、查询集、每页显示条数、搜索字段
    page_data = paginate(request, queryset, page_size=10, search_fields=['title'])

    # 渲染部门列表模板，传递分页后的数据
    return render(request, 'depart/depart_list.html', page_data)


# 部门添加视图函数
# 功能：处理添加部门的请求
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 创建部门记录并重定向
# 前端交互：当用户点击"添加部门"按钮时，跳转到该视图，提交表单后保存数据
def depart_add(request):
    # 处理GET请求，显示添加表单
    if request.method == "GET":
        # 设置页面标题
        title="添加部门"
        # 渲染添加表单模板，传递标题
        return render(request, 'depart/depart_add_modify.html', {'title': title})
    # 处理POST请求，保存表单数据
    # 从POST请求中获取部门名称
    title = request.POST.get('title')
    # 创建部门记录
    # 使用create()方法创建新部门记录
    models.Department.objects.create(title=title)
    # 重定向到部门列表页面
    return redirect("/depart/")


# 部门删除视图函数
# 功能：处理删除部门的请求
# 流程：1. 根据ID删除部门数据 2. 重定向到部门列表页面
# 前端交互：当用户点击列表页的"删除"按钮时，前端会发送请求到当前视图，后端接收ID参数后执行删除操作并返回结果
def depart_del(request, nid):
    # 根据ID删除部门数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常
    models.Department.objects.filter(id=nid).delete()
    # 重定向到部门列表页面
    return redirect("/depart/")


# 部门修改视图函数
# 功能：处理修改部门的请求
# 流程：1. GET请求时显示表单并填充数据 2. POST请求时处理表单数据 3. 更新部门记录并重定向
# 前端交互：当用户点击列表页的"修改"按钮时，跳转到该视图，提交表单后更新数据
def depart_modify(request, nid):
    # 处理GET请求，显示修改表单并填充数据
    if request.method == "GET":
        # 设置页面标题
        title = "修改部门"
        # 根据ID获取部门数据
        # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
        name=models.Department.objects.filter(id=nid).first()
        # 渲染修改表单模板，传递标题和部门数据
        return render(request, 'depart/depart_add_modify.html', {'title': title , 'name': name})
    # 处理POST请求，保存表单数据
    # 从POST请求中获取部门名称
    title = request.POST.get('title')
    # 更新部门记录
    # 使用filter()方法筛选记录，然后使用update()方法更新
    models.Department.objects.filter(id=nid).update(title=title)
    # 重定向到部门列表页面
    return redirect("/depart/")

