import random
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from faker import Faker
from project_one.models import Adminrole

# 初始化faker
fake = Faker('zh_CN')

# 生成100个员工数据
def add_employees(count=100):
    for i in range(count):
        username = fake.name()
        # 生成随机密码，这里使用简单的密码"123456"
        password = "123456"
        # 员工角色为1
        role = 1
        
        # 创建员工
        Adminrole.objects.create(
            username=username,
            password=password,
            role=role
        )
        print(f"已创建员工: {username}")

if __name__ == "__main__":
    add_employees(100)
    print("\n100个员工数据已添加完成！")
