# 导入Django核心模块
from django.shortcuts import render, redirect  # render用于渲染模板，redirect用于重定向
from django import forms  # 用于创建表单类
from project_one import models  # 导入项目的模型，用于数据库操作
from project_one.utils import pwd_data  # 导入密码加密工具，用于密码哈希处理
from project_one.utils import code  # 导入验证码生成工具
from io import BytesIO  # 用于在内存中操作图片数据
from django.http import HttpResponse  # 用于返回HTTP响应，特别是验证码图片


class LoginForm(forms.Form):
    """登录表单类
    功能：定义登录表单的字段和验证规则
    字段：用户名、密码、验证码
    """
    # 用户名字段，使用文本输入框，添加Bootstrap样式
    username = forms.CharField(
        label="用户名",  # 表单标签
        widget=forms.TextInput(attrs={'class': 'form-control'})  # 表单控件，添加CSS类
    )
    # 密码字段，使用密码输入框，添加Bootstrap样式
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})  # 密码输入框，会隐藏输入内容
    )
    # 验证码字段，使用文本输入框，添加Bootstrap样式和占位符
    captcha = forms.CharField(
        label="验证码",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入验证码'}),
        required=True  # 此字段为必填项
    )

    def clean_password(self):
        """密码字段的自定义验证方法
        功能：对密码进行MD5加密处理
        返回：加密后的密码字符串
        """
        pwd = self.cleaned_data.get('password')  # 获取表单提交的密码
        if pwd:
            return pwd_data.md5(pwd)  # 对密码进行MD5加密
        return pwd  # 如果密码为空，返回None（表单required=True时一般不会执行到这里）


def login(request):
    """登录视图函数
    功能：处理用户登录请求，包括GET请求显示登录表单和POST请求处理登录验证
    实现流程：
    1. 处理GET请求：创建表单实例并渲染登录页面
    2. 处理POST请求：
       a. 验证表单数据
       b. 验证验证码
       c. 验证用户名和密码
       d. 登录成功后保存session并跳转到首页
    前端交互：
    - 用户访问登录页面时，触发GET请求，显示登录表单
    - 用户填写表单并点击登录按钮时，触发POST请求，提交表单数据进行验证
    """
    if request.method == 'GET':
        # 创建登录表单实例
        form = LoginForm()
        # 渲染登录页面，传递表单实例
        return render(request, "login/login.html", {'form': form})

    # 处理POST请求
    form = LoginForm(request.POST)  # 用POST数据创建表单实例
    if form.is_valid():
        # 验证验证码
        captcha = form.cleaned_data.get('captcha')  # 获取表单提交的验证码
        session_captcha = request.session.get('captcha_code')  # 获取session中存储的验证码
        if not session_captcha or captcha.upper() != session_captcha:  # 验证码不匹配
            form.add_error("captcha", "验证码错误")  # 添加验证码错误信息
            return render(request, "login/login.html", {'form': form})  # 重新渲染登录页面
        
        # 移除验证码字段，因为数据库中没有这个字段
        clean_data = form.cleaned_data
        del clean_data['captcha']
        
        # 验证用户名和密码（cleaned_data中的password已经是md5哈希值）
        admin_object = models.Adminrole.objects.filter(**clean_data).first()  # 根据表单数据查询用户
        if not admin_object:  # 用户不存在或密码错误
            form.add_error("password", "用户名或者密码错误")  # 添加密码错误信息
            return render(request, "login/login.html", {'form': form})  # 重新渲染登录页面

        # 登录成功，保存session
        request.session['info'] = {
            "id": admin_object.id,
            "username": admin_object.username,
            "password": admin_object.password,  # 不推荐存密码，但保留原逻辑
            "role": admin_object.role  # 保存用户角色信息，用于权限控制
        }
        request.session.set_expiry(60 * 60 * 24 * 7)  # 设置session过期时间为一周
        return redirect('/')  # 登录成功后重定向到首页

    # 表单验证失败（如字段为空）
    return render(request, "login/login.html", {'form': form})

def logout(request):
    """登出视图函数
    功能：清除用户session并跳转到登录页面
    前端交互：
    - 用户点击登出按钮时，触发此视图，清除session并返回登录页面
    """
    request.session.clear()  # 清除所有session数据
    return redirect('/login/')  # 重定向到登录页面

def get_captcha(request):
    """生成验证码图片的视图函数
    功能：生成验证码图片并返回给前端
    实现流程：
    1. 生成验证码图片和验证码字符串
    2. 将验证码字符串保存到session
    3. 将图片数据保存到内存缓冲区
    4. 返回图片数据给前端
    前端交互：
    - 登录页面加载时，会请求此视图获取验证码图片
    - 用户点击验证码图片刷新时，会再次请求此视图获取新的验证码
    """
    img, captcha_code = code.creat_image_content()  # 生成验证码图片和验证码字符串
    request.session['captcha_code'] = captcha_code  # 将验证码字符串保存到session
    request.session.set_expiry(60 * 5)  # 设置验证码过期时间为5分钟

    # 将图片保存到内存缓冲区
    buffer = BytesIO()
    img.save(buffer, format='PNG')  # 将图片以PNG格式保存到缓冲区
    img_data = buffer.getvalue()  # 获取缓冲区中的图片数据

    # 返回图片数据，告知浏览器这是PNG图片
    return HttpResponse(img_data, content_type='image/png')