# 导入Django的快捷函数，用于渲染模板和重定向
from django.shortcuts import render, redirect
# 导入Django的MiddlewareMixin，用于创建中间件类
from django.utils.deprecation import MiddlewareMixin

class AuthMiddleware(MiddlewareMixin):
    """权限控制中间件
    功能：验证用户登录状态并进行权限控制
    作用：在请求处理前检查用户是否登录，以及是否有足够的权限执行操作
    """
    
    def process_request(self, request):
        """处理请求的方法
        功能：在请求到达视图函数前进行处理
        参数：request - Django请求对象，包含请求的所有信息
        返回值：None（继续处理请求）、HttpResponse（直接返回响应）或redirect（重定向）
        """
        
        # 定义无需验证的路径列表，包括登录、登出和验证码获取
        # 这些路径即使未登录也可以访问
        if request.path_info in ["/login/","/logout/", "/get_captcha/"]:
            # 直接返回，不进行后续验证
            return
        
        # 从session中获取用户信息
        # session是Django中用于存储用户状态的机制
        info_dict = request.session.get('info')
        
        # 检查用户是否已登录（session中是否有用户信息）
        if info_dict:
            # 将用户信息存储到请求对象中，方便后续视图函数使用
            # 这样在视图函数中就可以通过request.unicom_id等属性直接获取用户信息
            request.unicom_id = info_dict['id']
            request.unicom_username = info_dict['username']
            request.unicom_role = info_dict['role']
            
            # 权限控制：员工（role=1）只能访问列表页面，不能进行增删改操作
            # 这里的role=1表示普通员工，role=2表示领导，role=3表示管理员
            if info_dict['role'] == 1:
                # 定义需要权限的路径模式列表
                # 这些路径只有领导和管理员可以访问
                restricted_paths = [
                    '/depart/add/', '/depart/\d+/del/', '/depart/\d+/modify/',  # 部门管理的增删改操作
                    '/user/add/', '/user/\d+/del/', '/user/add/modelform/', '/user/\d+/modify/',  # 员工管理的增删改操作
                    '/asset/add/', '/asset/\d+/modify/',  # 资产管理的增删改操作
                    '/admin_role/admin_add/', '/admin_role/\d+/admin_modify/', '/admin_role/\d+/reset/'  # 管理员管理的操作
                ]
                
                # 导入正则表达式模块，用于匹配路径模式
                import re
                
                # 遍历所有需要权限的路径模式
                for path_pattern in restricted_paths:
                    # 使用正则表达式匹配当前请求路径
                    if re.match(path_pattern, request.path_info):
                        # 如果匹配成功，说明员工尝试访问需要权限的路径
                        # 渲染权限不足页面并返回
                        return render(request, "permission_denied.html")
            
            # 用户已登录且有权限，继续处理请求
            return
        
        # 用户未登录，重定向到登录页面
        # 这样未登录的用户将被强制跳转到登录页面
        return redirect("/login/")
