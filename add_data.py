#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import django
import random
import datetime
from faker import Faker

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from project_one.models import Department, Userinfo

# 初始化 Faker
fake = Faker('zh_CN')

def add_departments(count=15):
    """添加部门"""
    departments = []
    department_names = [
        '技术部', '市场部', '销售部', '人力资源部', '财务部',
        '研发部', '产品部', '设计部', '运营部', '客服部',
        '行政部', '法务部', '采购部', '公关部', '战略部'
    ]
    
    for name in department_names[:count]:
        department, created = Department.objects.get_or_create(title=name)
        if created:
            departments.append(department)
            print(f'添加部门: {name}')
    
    return departments

def add_employees(count=200):
    """添加员工"""
    # 获取所有部门
    departments = Department.objects.all()
    if not departments:
        print('请先添加部门')
        return
    
    employees = []
    for i in range(count):
        # 随机选择部门
        depart = random.choice(departments)
        
        # 生成随机数据
        name = fake.name()
        age = str(random.randint(18, 60))
        gender = random.choice([1, 2])
        salary = round(random.uniform(3000, 20000), 2)
        create_time = fake.date_time_between(start_date='-5y', end_date='now')
        
        # 创建员工
        employee = Userinfo(
            name=name,
            age=age,
            gender=gender,
            salary=salary,
            create_time=create_time,
            depart=depart
        )
        employees.append(employee)
        
        # 每10个批量创建一次
        if (i + 1) % 10 == 0:
            Userinfo.objects.bulk_create(employees)
            print(f'已添加 {i + 1} 个员工')
            employees = []
    
    # 处理剩余的员工
    if employees:
        Userinfo.objects.bulk_create(employees)
        print(f'已添加 {len(employees)} 个员工')

if __name__ == '__main__':
    print('开始添加部门...')
    add_departments(15)
    print('部门添加完成')
    
    print('\n开始添加员工...')
    add_employees(200)
    print('员工添加完成')
