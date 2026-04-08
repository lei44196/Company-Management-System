# 导入Django的forms模块，用于创建表单
from django import forms
# 导入密码处理工具，用于密码加密
from project_one.utils import pwd_data
# 导入Django的快捷函数，用于渲染模板和重定向
from django.shortcuts import render, redirect
# 导入自定义的分页工具函数，用于实现分页功能
from project_one.utils.pagination import paginate
# 导入项目的models模块，用于操作数据库
from project_one import models
# 导入Django的ValidationError，用于抛出验证错误
from django.core.validators import ValidationError


# 管理员列表视图函数
# 功能：展示所有管理员账号数据，支持分页和搜索
# 流程：1. 获取所有管理员数据 2. 使用分页工具处理数据 3. 渲染模板显示数据
# 前端交互：当用户访问管理员列表页面时，显示所有管理员数据，支持分页和搜索
def admin_list(request):
    # 获取所有管理员数据
    # 使用all()方法获取所有记录，因为我们需要展示所有管理员
    queryset = models.Adminrole.objects.all()
    # 使用自定义的paginate函数处理分页和搜索
    # 参数说明：request对象、查询集、每页显示条数、搜索字段
    page_data = paginate(request, queryset, page_size=5, search_fields=['mobile'])
    # 渲染管理员列表模板，传递分页后的数据
    return render(request, "admin_role/admin_list.html", page_data)


# 管理员添加表单类
# 功能：创建添加管理员的表单
# 说明：继承自ModelForm，自动生成表单字段，添加确认密码字段
class AdminModelForm(forms.ModelForm):
    # 添加确认密码字段
    new_password = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Adminrole
        # 指定表单包含的字段
        fields = ['username', 'password', "new_password", 'role']
        # 设置密码字段的 widget 为密码输入框
        widgets = {
            "password": forms.PasswordInput,
        }

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}

    # 密码校验方法，用于加密密码
    def clean_password(self):
        # 获取密码数据
        pwd = self.cleaned_data.get('password')
        # 使用md5加密密码
        return pwd_data.md5(pwd)

    # 确认密码校验方法，用于验证两次密码是否一致
    def clean_new_password(self):
        # 加密确认密码
        new_pwd = pwd_data.md5(self.cleaned_data.get("new_password"))
        # 获取加密后的密码
        pwd = self.cleaned_data.get('password')
        # 验证两次密码是否一致
        if pwd != new_pwd:
            # 密码不一致，抛出验证错误
            raise ValidationError("两次密码不一致")
        # 返回加密后的确认密码
        return new_pwd


# 管理员添加视图函数
# 功能：处理添加管理员的请求
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击"添加账号"按钮时，跳转到该视图，提交表单后保存数据
def admin_add(request):
    # 设置页面标题
    title = "添加账号"
    # 处理GET请求，显示添加表单
    if request.method == 'GET':
        # 创建表单实例
        form = AdminModelForm()
        # 准备模板数据
        content = {
            "title": title,
            "form": form
        }
        # 渲染添加表单模板，传递标题和表单
        return render(request, "admin_role/admin_add.html", content)

    # 处理POST请求，保存表单数据
    form = AdminModelForm(data=request.POST)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到管理员列表页面
        return redirect('/admin_role/admin_list/')
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, "admin_role/admin_add.html", {"title": title, "form": form})


# 管理员修改表单类
# 功能：创建修改管理员的表单
# 说明：继承自ModelForm，自动生成表单字段，只包含用户名和角色字段
class AdminModifyModelForm(forms.ModelForm):
    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Adminrole
        # 指定表单包含的字段
        fields = ['username', 'role']

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}


# 管理员修改视图函数
# 功能：处理修改管理员的请求
# 流程：1. GET请求时显示表单并填充数据 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击列表页的"修改"按钮时，跳转到该视图，提交表单后更新数据
def admin_modify(request,nid):
    # 设置页面标题
    title="编辑页面"
    # 根据ID获取管理员数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
    title_obj=models.Adminrole.objects.filter(id=nid).first()
    # 处理GET请求，显示修改表单并填充数据
    if request.method == 'GET':
        # 创建表单实例，传递管理员数据
        form = AdminModifyModelForm(instance=title_obj)
        # 准备模板数据
        content = {
            "title": title,
            "form": form
        }
        # 渲染修改表单模板，传递标题和表单
        return render(request,"admin_role/admin_operation.html", content)

    # 处理POST请求，保存表单数据
    form = AdminModifyModelForm(data=request.POST,instance=title_obj)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到管理员列表页面
        return redirect('/admin_role/admin_list/')
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, "admin_role/admin_operation.html", {"title": title, "form": form})


# 管理员密码重置表单类
# 功能：创建重置管理员密码的表单
# 说明：继承自ModelForm，自动生成表单字段，添加确认密码字段
class AdminResetModelForm(forms.ModelForm):
    # 添加确认密码字段
    new_second_password=forms.CharField(label="确认密码", widget=forms.PasswordInput)
    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Adminrole
        # 指定表单包含的字段
        fields = ["password"]
        # 设置密码字段的 widget 为密码输入框
        widgets = {
            "password": forms.PasswordInput,
        }

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}

    # 密码校验方法，用于加密密码
    def clean_password(self):
        # 获取密码数据
        pwd = self.cleaned_data.get('password')
        # 使用md5加密密码
        return pwd_data.md5(pwd)

    # 确认密码校验方法，用于验证两次密码是否一致
    def clean_new_second_password(self):
        # 加密确认密码
        new_second_password = pwd_data.md5(self.cleaned_data.get("new_second_password"))
        # 获取加密后的密码
        pwd = self.cleaned_data.get('password')
        # 验证两次密码是否一致
        if pwd != new_second_password:
            # 密码不一致，抛出验证错误
            raise ValidationError("两次密码不一致")
        # 返回加密后的确认密码
        return new_second_password


# 管理员密码重置视图函数
# 功能：处理重置管理员密码的请求
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击列表页的"重置密码"按钮时，跳转到该视图，提交表单后更新密码
def admin_reset(request,nid):
    # 根据ID获取管理员数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
    title_object=models.Adminrole.objects.filter(id=nid).first()
    # 设置页面标题，包含管理员用户名
    title=f"重置<{title_object.username}>密码"
    # 处理GET请求，显示重置密码表单
    if request.method == 'GET':
        # 创建表单实例，传递管理员数据
        form = AdminResetModelForm(instance=title_object)
        # 渲染重置密码表单模板，传递标题和表单
        return render(request,"admin_role/admin_operation.html", {"title": title, "form": form})
    # 处理POST请求，保存表单数据
    form = AdminResetModelForm(data=request.POST,instance=title_object)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到管理员列表页面
        return redirect('/admin_role/admin_list/')
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, "admin_role/admin_operation.html", {"title": title, "form": form})
