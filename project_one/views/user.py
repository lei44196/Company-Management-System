# 导入tkinter的font模块（虽然导入但未使用）
from tkinter.font import names

# 导入MySQLdb的connect函数（虽然导入但未使用）
from MySQLdb import connect
# 导入Django的快捷函数，用于渲染模板和重定向
from django.shortcuts import render, redirect
# 导入matplotlib的pyplot模块（虽然导入但未使用）
from matplotlib.pyplot import title

# 导入项目的models模块，用于操作数据库
from project_one import models
# 导入Django的forms模块，用于创建表单
from django import forms
# 导入自定义的分页工具函数，用于实现分页功能
from project_one.utils.pagination import paginate


# 员工列表视图函数
# 功能：展示所有员工数据，支持分页和搜索
# 流程：1. 获取所有员工数据 2. 使用分页工具处理数据 3. 渲染模板显示数据
# 前端交互：当用户访问员工列表页面时，显示所有员工数据，支持分页和搜索
def user_list(request):
    # 获取所有员工数据
    # 使用all()方法获取所有记录，因为我们需要展示所有员工
    queryset = models.Userinfo.objects.all()
    # 使用自定义的paginate函数处理分页和搜索
    # 参数说明：request对象、查询集、每页显示条数、搜索字段
    page_data = paginate(request, queryset, page_size=10, search_fields=['name'])
    # 渲染员工列表模板，传递分页后的数据
    return render(request, "user/user_list.html", page_data)


# 员工添加视图函数（传统方式）
# 功能：处理添加员工的请求
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 创建员工记录并重定向
# 前端交互：当用户点击"添加员工"按钮时，跳转到该视图，提交表单后保存数据
def user_add(request):
    # 处理GET请求，显示添加表单
    if request.method == "GET":
        # 准备模板数据，包括性别选项和部门列表
        content = {
            "gender_choice": models.Userinfo.gender_choice,  # 性别选项
            "depart_list": models.Department.objects.all()  # 部门列表
        }
        # 渲染添加表单模板，传递数据
        return render(request, "user/user_add.html", content)
    # 处理POST请求，保存表单数据
    # 从POST请求中获取表单数据
    name = request.POST.get("name")  # 姓名
    age = request.POST.get("age")  # 年龄
    salary = request.POST.get("asset")  # 收入（注意：这里字段名是asset，但实际是salary）
    gender = request.POST.get("gender")  # 性别
    dtime = request.POST.get("dtime")  # 入职时间
    depart = request.POST.get("depart")  # 部门ID
    # 创建员工记录
    # 使用create()方法创建新员工记录
    models.Userinfo.objects.create(name=name, age=age, gender=gender, salary=salary, create_time=dtime,
                                   depart_id=depart)
    # 重定向到员工列表页面
    return redirect("/user/")


# 员工删除视图函数
# 功能：处理删除员工的请求
# 流程：1. 根据ID删除员工数据 2. 重定向到员工列表页面
# 前端交互：当用户点击列表页的"删除"按钮时，前端会发送请求到当前视图，后端接收ID参数后执行删除操作并返回结果
def user_del(request, nid):
    # 根据ID删除员工数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常
    models.Userinfo.objects.filter(id=nid).delete()
    # 重定向到员工列表页面
    return redirect("/user/")


# 员工表单类（使用ModelForm）
# 功能：创建员工的表单
# 说明：继承自ModelForm，自动生成表单字段，并重写name字段添加验证
class UserModelForm(forms.ModelForm):
    # 重写name字段，添加最小长度验证
    name = forms.CharField(min_length=2, label="姓名")
    # 额外添加字段
    class Meta:
        # 获取数据表中的字段
        model = models.Userinfo
        # 指定表单包含所有字段
        fields = "__all__"

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}


# 添加员工视图函数（使用ModelForm）
# 功能：处理添加员工的请求，使用ModelForm简化表单处理
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击"添加员工2"按钮时，跳转到该视图，提交表单后保存数据
def user_add_modelform(request):
    # 处理GET请求，显示添加表单
    if request.method == "GET":
        # 创建表单实例
        form = UserModelForm()
        # 渲染添加表单模板，传递表单
        return render(request, "user/user_modelform.html", {"form": form})
    # 接受表单提交的数据
    form = UserModelForm(request.POST)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到员工列表页面
        return redirect("/user/")
    # 数据不完整，重新渲染表单并显示错误信息
    return render(request, "user/user_modelform.html", {"form": form})


# 员工修改视图函数
# 功能：处理修改员工的请求
# 流程：1. GET请求时显示表单并填充数据 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击列表页的"修改"按钮时，跳转到该视图，提交表单后更新数据
def user_modify(request, nid):
    # 根据ID获取员工数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
    obj = models.Userinfo.objects.filter(id=nid).first()
    # 处理GET请求，显示修改表单并填充数据
    if request.method == "GET":
        # 创建表单实例，传递员工数据
        form = UserModelForm(instance=obj)
        # 准备模板数据
        content = {"form": form}

        # 渲染修改表单模板，传递表单
        return render(request,"user/user_modelform.html", content)
    # 处理POST请求，保存表单数据
    form = UserModelForm(request.POST, instance=obj)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到员工列表页面
        return redirect("/user/")
        # 数据不完整，重新渲染表单并显示错误信息
    return render(request, "user/user_modelform.html", {"form": form})
