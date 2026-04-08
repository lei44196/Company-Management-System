"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from project_one.views import depart, user, asset, admin_role, login, task,ajax_demo,perform
from django.conf.urls.static import serve
from django.conf import settings



urlpatterns = [
    re_path(r"^media/(?P<path>.*)$",serve,{"document_root":settings.MEDIA_ROOT}),
    path('', depart.index, name='index'),

    path('depart/', depart.depart_list, name='depart_list'),
    path('depart/add/', depart.depart_add, name='depart_add'),
    path('depart/<int:nid>/del/', depart.depart_del, name='depart_del'),
    path('depart/<int:nid>/modify/', depart.depart_modify, name='depart_modify'),

    #__________员工表视图___________
    path('user/', user.user_list, name='user_list'),
    path('user/add/', user.user_add, name='user_add'),
    path('user/<int:nid>/del/', user.user_del, name='user_del'),
    path('user/add/modelform/', user.user_add_modelform, name='user_add_modelform'),
    path('user/<int:nid>/modify/', user.user_modify, name='user_modify'),

    #——————————————资产管理——————————
    path('asset/', asset.asset_list, name='asset_list'),
    path('asset/add/', asset.asset_add, name='asset_add'),
    path('asset/daoru/', asset.asset_import, name='asset_import'),
    path('asset/<int:nid>/modify/',asset.asset_modify, name='asset_modify'),
    #——————————————资产管理——————————
    path('admin_role/admin_list/', admin_role.admin_list, name='admin_list'),
    path('admin_role/admin_add/', admin_role.admin_add, name='admin_add'),
    path('admin_role/<int:nid>/admin_modify/', admin_role.admin_modify, name='admin_modify'),
    path('admin_role/<int:nid>/reset/', admin_role.admin_reset, name='admin_reset'),
    #####################登入登出
    path('login/', login.login, name='login'),
    path('logout/', login.logout, name='logout'),
    path('get_captcha/', login.get_captcha, name='get_captcha'),
    
    # 任务管理
    path('task/', task.task_list, name='task_list'),
    path('task/add/', task.task_add, name='task_add'),
    path('task/<int:nid>/modify/', task.task_modify, name='task_modify'),
    path('task/<int:nid>/delete/', task.task_delete, name='task_delete'),


    #ajax演示
    # path('ajax/', ajax_demo.ajax),
    ######绩效管理

    path('perform/', perform.perform_list, name='perform_list'),
    path('perform/add/', perform.perform_add, name='perform_add'),
    path('perform/<int:nid>/modify/', perform.perform_modify, name='perform_modify'),
    path('perform/<int:nid>/delete/', perform.perform_delete, name='perform_delete'),

]
