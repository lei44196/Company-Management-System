from django.shortcuts import render, redirect
from project_one import models
from django import forms
from project_one.utils.pagination import paginate

# 导入Redis缓存装饰器
from project_one.utils.redis_cache import cache_invalidated


def user_list(request):
    """
    用户列表视图
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 用户列表页面
    """
    queryset = models.Userinfo.objects.all()
    page_data = paginate(request, queryset, page_size=10, search_fields=['name'])
    return render(request, "user/user_list.html", page_data)


def user_add(request):
    """
    添加用户视图
    
    【注意】此函数不使用缓存，因为是写操作
    新增用户后，会通过其他机制触发缓存失效（如模型的QueryCacheMixin）
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 添加用户页面或重定向到用户列表
    """
    if request.method == "GET":
        content = {
            "gender_choice": models.Userinfo.gender_choice,
            "depart_list": models.Department.objects.all()
        }
        return render(request, "user/user_add.html", content)

    name = request.POST.get("name")
    age = request.POST.get("age")
    salary = request.POST.get("asset")
    gender = request.POST.get("gender")
    dtime = request.POST.get("dtime")
    depart = request.POST.get("depart")

    models.Userinfo.objects.create(name=name, age=age, gender=gender, salary=salary, create_time=dtime,
                                  depart_id=depart)
    return redirect("/user/")


# 【缓存失效装饰器使用说明】
# @cache_invalidated 参数说明：
#   model_name: 模型名称，用于匹配要删除的缓存键（必需）
#   key_prefix: 缓存键前缀，默认使用函数名（可选）
#
# 清理逻辑：删除所有匹配模式 "{REDIS_CACHE_PREFIX}:{model_name}:{key_prefix}:*" 的缓存

@cache_invalidated('Userinfo', 'list')
def user_del(request, nid):
    """
    删除用户视图
    
    【缓存策略】
    - 使用@cache_invalidated装饰器在删除后清理相关缓存
    - 清理模式：project_one:Userinfo:list:*
    - 确保删除后用户列表能获取最新数据
    
    Args:
        request: HTTP请求对象
        nid: 用户ID
    
    Returns:
        HttpResponse: 重定向到用户列表
    """
    models.Userinfo.objects.filter(id=nid).delete()
    return redirect("/user/")


class UserModelForm(forms.ModelForm):
    """
    用户模型表单
    
    用于用户添加和修改操作的表单验证
    """
    name = forms.CharField(min_length=2, label="姓名")

    class Meta:
        model = models.Userinfo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}


def user_add_modelform(request):
    """
    使用ModelForm添加用户视图
    
    Args:
        request: HTTP请求对象
    
    Returns:
        HttpResponse: 添加用户页面或重定向到用户列表
    """
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user/user_modelform.html", {"form": form})

    form = UserModelForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("/user/")
    return render(request, "user/user_modelform.html", {"form": form})


@cache_invalidated('Userinfo', 'list')
def user_modify(request, nid):
    """
    修改用户视图
    
    【缓存策略】
    - 使用@cache_invalidated装饰器在修改后清理相关缓存
    - 清理模式：project_one:Userinfo:list:*
    - 确保修改后用户列表能获取最新数据
    
    Args:
        request: HTTP请求对象
        nid: 用户ID
    
    Returns:
        HttpResponse: 修改用户页面或重定向到用户列表
    """
    obj = models.Userinfo.objects.filter(id=nid).first()
    if request.method == "GET":
        form = UserModelForm(instance=obj)
        return render(request, "user/user_modelform.html", {"form": form})

    form = UserModelForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/user/")
    return render(request, "user/user_modelform.html", {"form": form})