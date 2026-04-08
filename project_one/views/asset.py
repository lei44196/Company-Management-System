# 导入MySQLdb的connect函数（虽然导入但未使用）
from MySQLdb import connect
# 导入Django的快捷函数，用于渲染模板和重定向
from django.shortcuts import render, redirect
# 导入Django的forms模块，用于创建表单
from django import forms
# 导入matplotlib的pyplot模块（虽然导入但未使用）
from matplotlib.pyplot import title
# 导入项目的models模块，用于操作数据库
from project_one import models
# 导入Django的RegexValidator，用于验证手机号格式
from django.core.validators import RegexValidator
# 导入Django的ValidationError，用于抛出验证错误
from django.core.exceptions import ValidationError
# 导入自定义的分页工具函数，用于实现分页功能
from project_one.utils.pagination import paginate
# 导入openpyxl库，用于读取Excel文件
import openpyxl
# 导入os模块，用于处理文件路径
import os


# 资产列表视图函数
# 功能：展示所有资产数据，支持分页和搜索
# 流程：1. 获取所有资产数据 2. 使用分页工具处理数据 3. 渲染模板显示数据
# 前端交互：当用户访问资产列表页面时，显示所有资产数据，支持分页和搜索
def asset_list(request):
    # 获取所有资产数据
    # 使用all()方法获取所有记录，因为我们需要展示所有资产
    queryset = models.Assets.objects.all()
    # 使用自定义的paginate函数处理分页和搜索
    # 参数说明：request对象、查询集、每页显示条数、搜索字段
    page_data = paginate(request, queryset, page_size=10, search_fields=['mobile'])
    # 渲染资产列表模板，传递分页后的数据
    return render(request, 'asset/asset_list.html', page_data)


# 资产添加表单类
# 功能：创建添加资产的表单
# 说明：继承自ModelForm，自动生成表单字段，并重写mobile字段添加验证
class AssetForm(forms.ModelForm):
    # 重写mobile字段，添加标签和验证器
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r"^1[3-9]\d{9}", "请输入正确格式的手机号")]
    )

    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Assets
        # 指定表单包含所有字段
        fields = "__all__"

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}

    # 手机号校验方法，用于自定义验证逻辑
    def clean_mobile(self):
        # 获取清理后的手机号数据
        new_mobile = self.cleaned_data['mobile']
        # 检查手机号是否已存在
        # 使用filter()方法筛选相同手机号的记录
        exists = models.Assets.objects.filter(mobile=new_mobile).exists()
        # 如果手机号已存在，抛出验证错误
        if exists:
            raise ValidationError("手机号已经存在")
        # 返回验证通过的手机号
        return new_mobile


# 资产添加视图函数
# 功能：处理添加资产的请求
# 流程：1. GET请求时显示表单 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击"添加资产"按钮时，跳转到该视图，提交表单后保存数据
def asset_add(request):
    # 处理GET请求，显示添加表单
    if request.method == 'GET':
        # 设置页面标题
        title = "添加资产"
        # 创建表单实例
        form = AssetForm()
        # 渲染添加表单模板，传递表单和标题
        return render(request, 'asset/asset_modify.html', {'form': form, "title": title})
    # 处理POST请求，保存表单数据
    form = AssetForm(data=request.POST)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到资产列表页面
        return redirect("/asset/")
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, 'asset/asset_modify.html', {'form': form})


# 资产修改表单类
# 功能：创建修改资产的表单
# 说明：继承自ModelForm，自动生成表单字段，并重写price字段为不可编辑
class AssetModify(forms.ModelForm):
    # 重写price字段，设置为不可编辑
    price = forms.CharField(disabled=True, label="价格")

    # Meta类用于指定表单的元数据
    class Meta:
        # 指定表单对应的模型
        model = models.Assets
        # 指定表单包含所有字段
        fields = "__all__"

    # 初始化方法，用于设置表单字段的属性
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        # 遍历所有字段，为每个字段添加form-control类，使表单样式统一
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}

    # 手机号校验方法，用于自定义验证逻辑
    def clean_mobile(self):
        # 获取清理后的手机号数据
        new_mobile = self.cleaned_data['mobile']
        # 检查手机号是否已存在（排除当前记录）
        # 使用exclude()方法排除当前记录，然后使用filter()方法筛选相同手机号的记录
        exists = models.Assets.objects.exclude(id=self.instance.pk).filter(mobile=new_mobile).exists()
        # 如果手机号已存在，抛出验证错误
        if exists:
            raise ValidationError("手机号已经存在")
        # 返回验证通过的手机号
        return new_mobile


# 资产修改视图函数
# 功能：处理修改资产的请求
# 流程：1. GET请求时显示表单并填充数据 2. POST请求时处理表单数据 3. 验证通过后保存数据并重定向
# 前端交互：当用户点击列表页的"修改"按钮时，跳转到该视图，提交表单后更新数据
def asset_modify(request, nid):
    # 设置页面标题
    title = "修改数据"
    # 根据ID获取资产数据
    # 使用filter()而不用get()是因为filter()返回查询集，即使没有找到数据也不会抛出异常，然后用first()获取第一个结果
    data_list = models.Assets.objects.filter(id=nid).first()
    # 处理GET请求，显示修改表单并填充数据
    if request.method == 'GET':
        # 创建表单实例，传递资产数据
        form = AssetModify(instance=data_list)
        # 准备模板数据
        content = {
            "title": title,
            "form": form,

        }
        # 渲染修改表单模板，传递表单和标题
        return render(request, 'asset/asset_modify.html', content)
    # 处理POST请求，保存表单数据
    form = AssetModify(data=request.POST, instance=data_list)
    # 验证表单数据
    if form.is_valid():
        # 保存表单数据到数据库
        form.save()
        # 重定向到资产列表页面
        return redirect("/asset/")
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, 'asset/asset_modify.html', {'form': form, "title": title})


# 导入资产表单类
# 功能：创建导入资产的表单，用于上传Excel文件
class AssetImportForm(forms.Form):
    # 文件上传字段，限制只能上传Excel文件
    file = forms.FileField(
        label="Excel文件",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )


# 导入资产视图函数
# 功能：处理导入资产的请求，包括显示上传表单和处理文件上传
# 流程：1. GET请求时显示上传表单 2. POST请求时处理文件上传 3. 读取Excel文件数据 4. 保存数据到数据库 5. 重定向到资产列表页面
# 前端交互：当用户点击"导入资产"按钮时，跳转到该视图，上传Excel文件后导入数据

def asset_import(request):
    # 处理GET请求，显示上传表单
    if request.method == 'GET':
        # 创建表单实例
        form = AssetImportForm()
        # 渲染导入表单模板，传递表单
        return render(request, 'asset/asset_import.html', {'form': form})
    
    # 处理POST请求，处理文件上传
    form = AssetImportForm(request.POST, request.FILES)
    # 验证表单数据
    if form.is_valid():
        # 获取上传的文件
        file = request.FILES['file']
        
        # 检查文件扩展名，确保是Excel文件
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.xlsx', '.xls']:
            # 文件格式不正确，重新渲染表单并显示错误信息
            form.add_error('file', '请上传.xlsx或.xls格式的Excel文件')
            return render(request, 'asset/asset_import.html', {'form': form})
        
        try:
            # 加载Excel文件
            wb = openpyxl.load_workbook(file)
            # 获取第一个工作表
            ws = wb.active
            
            # 遍历Excel中的每一行数据（从第二行开始，第一行是标题）
            for row in ws.iter_rows(min_row=1, values_only=True):
                # 检查行数据是否为空
                if not row or not row[0]:
                    continue
                
                # 从Excel行数据中获取字段值
                # 根据Excel图片中的列名与数据库字段对应
                # 列A: mobile (手机号)
                # 列B: status (使用状态，1=已使用，2=未使用)
                # 列C: times (购买时间)
                # 列D: price (价格)
                # 列E: user_id (使用人ID)
                mobile = str(row[0]) if row[0] else ''
                status = int(row[1]) if row[1] else 2  # 默认未使用
                times = str(row[2]) if row[2] else ''
                price = str(row[3]) if row[3] else ''
                user_id = int(row[4]) if row[4] else None
                
                # 检查手机号是否已存在
                if mobile:
                    exists = models.Assets.objects.filter(mobile=mobile).exists()
                    if not exists:
                        # 验证user_id是否在Userinfo表中存在
                        if user_id:
                            user_exists = models.Userinfo.objects.filter(id=user_id).exists()
                            if not user_exists:
                                user_id = None  # 如果user_id不存在，设置为None
                        
                        # 创建新的资产记录
                        asset = models.Assets(
                            mobile=mobile,
                            status=status,
                            times=times,
                            price=price,
                            user_id=user_id
                        )
                        asset.save()
            
            # 导入完成后重定向到资产列表页面
            return redirect("/asset/")
            
        except Exception as e:
            # 处理导入过程中的错误
            form.add_error('file', f'导入失败：{str(e)}')
            return render(request, 'asset/asset_import.html', {'form': form})
    
    # 表单验证失败，重新渲染表单并显示错误信息
    return render(request, 'asset/asset_import.html', {'form': form})
