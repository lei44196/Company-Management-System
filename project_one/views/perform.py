# 导入Django的快捷函数，用于渲染模板和重定向
from django.shortcuts import render, redirect
# 导入Django的forms模块，用于创建表单
from django import forms
# 导入项目的models模块，用于操作数据库
from project_one import models
# 导入自定义的分页工具函数，用于实现分页功能
from project_one.utils.pagination import paginate
# 导入datetime模块，用于处理日期时间
from datetime import datetime


# 绩效列表视图函数
# 功能：展示所有绩效数据，支持分页和搜索
# 流程：1. 获取所有绩效数据 2. 使用分页工具处理数据 3. 渲染模板显示数据
def perform_list(request):
    # 获取所有绩效数据
    # 使用all()方法获取所有记录，因为我们需要展示所有绩效
    queryset = models.Perform.objects.all()
    # 使用自定义的paginate函数处理分页和搜索
    # 参数说明：request对象、查询集、每页显示条数、搜索字段
    page_data = paginate(request, queryset, page_size=10, search_fields=['oid', 'title', 'name'])
    # 渲染绩效列表模板，传递分页后的数据
    return render(request, 'perform/perform_list.html', page_data)


# 绩效添加表单类
# 功能：创建添加绩效的表单
# 说明：继承自ModelForm，自动生成表单字段
class PerformForm(forms.ModelForm):
    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Perform
        # 指定表单包含的字段
        fields = ['oid', 'source', 'title', 'times', 'price', 'name', 'image']

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}


# 绩效添加视图函数
# 功能：处理添加绩效的请求
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击"添加绩效"按钮时，跳转到该视图，提交表单后保存数据

def perform_add(request):
    # 处理GET请求，显示添加表单
    if request.method == 'GET':
        # 设置页面标题
        title = "添加绩效"
        # 创建表单实例
        form = PerformForm()
        # 获取当前日期，用于在表单中显示
        current_date = datetime.now().strftime('%Y-%m-%d')
        # 渲染添加表单模板，传递表单和标题
        return render(request, 'perform/perform_add.html', {'form': form, "title": title, 'current_date': current_date})
    # 处理POST请求，保存表单数据
    # 处理POST请求时，自动设置当前时间为成交日期
    # 使用request.POST.copy()创建副本，避免直接修改原始POST数据
    post_data = request.POST.copy()
    # 设置成交日期为当前日期
    post_data['times'] = datetime.now().date()
    # 创建表单实例，传递POST数据和文件数据
    form = PerformForm(data=post_data, files=request.FILES)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到绩效列表页面
        return redirect("/perform/")
    # 表单验证失败，重新渲染表单并显示错误信息
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render(request, 'perform/perform_add.html', {'form': form, 'current_date': current_date})


# 绩效修改表单类
# 功能：创建修改绩效的表单
# 说明：继承自ModelForm，自动生成表单字段，并重写times字段为不可编辑
class PerformModify(forms.ModelForm):
    # 重写times字段，设置为不可编辑
    times = forms.DateField(disabled=True, label="成交日期")
    
    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Perform
        # 指定表单包含的字段
        fields = ['oid', 'source', 'title', 'times', 'price', 'name', 'image']

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}
    
    # 表单验证方法，用于自定义验证逻辑
    def clean(self):
        # 调用父类的验证方法，获取清理后的数据
        cleaned_data = super().clean()
        # 忽略 times 字段的必填校验，因为该字段已设置为不可编辑
        if 'times' in cleaned_data:
            del cleaned_data['times']
        # 返回清理后的数据
        return cleaned_data


# 绩效修改视图函数
# 功能：处理修改绩效的请求
# 流程：1. GET请求时显示表单并填充数据 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击列表页的"修改"按钮时，跳转到该视图，提交表单后更新数据

def perform_modify(request, nid):
    # 设置页面标题
    title = "修改绩效"
    # 根据ID获取绩效数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
    data_list = models.Perform.objects.filter(id=nid).first()
    # 处理GET请求，显示修改表单并填充数据
    if request.method == 'GET':
        # 创建表单实例，传递绩效数据
        form = PerformModify(instance=data_list)
        # 准备模板数据
        content = {
            "title": title,
            "form": form,
            "current_date": data_list.times.strftime('%Y-%m-%d')

        }
        # 渲染修改表单模板，传递表单和标题
        return render(request, 'perform/perform_add.html', content)
    # 处理POST请求，保存表单数据
    # 处理POST请求时，确保 times 字段不会因为被禁用而导致验证失败
    form = PerformModify(data=request.POST, files=request.FILES, instance=data_list)
    # 验证表单数据
    if form.is_valid():
        # 保存时保留原来的 times 值
        # 使用commit=False创建实例但不保存到数据库
        instance = form.save(commit=False)
        # 设置times字段为原始值，因为表单中该字段被禁用
        instance.times = data_list.times
        # 保存实例到数据库
        instance.save()
        # 重定向到绩效列表页面
        return redirect("/perform/")
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, 'perform/perform_add.html', {'form': form, "title": title, "current_date": data_list.times.strftime('%Y-%m-%d')})


# 绩效删除视图函数
# 功能：处理删除绩效的请求
# 流程：1. 根据ID删除绩效数据 2. 重定向到绩效列表页面
# 前端交互：当用户点击列表页的"删除"按钮时，前端会发送请求到当前视图，后端接收ID参数后执行删除操作并返回结果

def perform_delete(request, nid):
    # 根据ID删除绩效数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常
    models.Perform.objects.filter(id=nid).delete()
    # 重定向到绩效列表页面
    return redirect("/perform/")
