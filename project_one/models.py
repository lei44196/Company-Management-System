from django.db import models


# Create your models here.
class Department(models.Model):
    title = models.CharField(verbose_name="部门表", max_length=100)
    def __str__(self):
        return self.title


class Userinfo(models.Model):
    name = models.CharField(verbose_name="部门表", max_length=100)
    age = models.CharField(verbose_name="年龄", max_length=100)
    gender_choice = (
        (1, "男"),
        (2, "女")

    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choice)
    salary = models.DecimalField(verbose_name="收入", max_digits=10,  # 总位数（整数部分+小数部分）
                                 decimal_places=2)
    create_time = models.DateTimeField(verbose_name="入职时间")
    depart = models.ForeignKey(verbose_name="部门",to="Department", to_field="id", on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class Assets(models.Model):
    mobile=models.CharField(verbose_name="手机号码", max_length=11)
    start_code_choice=(
        (1,"已使用"),
        (2,"未使用")
    )
    status=models.IntegerField(verbose_name="使用状态",choices=start_code_choice)
    times=models.CharField(verbose_name="创建时间",max_length=100)
    user=models.ForeignKey(verbose_name="使用者",to="Userinfo", to_field="id", on_delete=models.SET_NULL, null=True, blank=True)
    price=models.CharField(verbose_name="价格", max_length=1000)

class Adminrole(models.Model):
    username=models.CharField(verbose_name="用户名",max_length=32)
    password=models.CharField(verbose_name="密码",max_length=64)
    level_choice = (
        (1, "员工"),
        (2, "领导"),
        (3,"管理员")
    )
    role=models.IntegerField(verbose_name="角色",choices=level_choice)


class Task(models.Model):
    title = models.CharField(verbose_name='任务标题', max_length=100)
    description = models.TextField(verbose_name='任务描述')
    deadline = models.DateField(verbose_name='截止日期')
    status_choice = (
        (0, '待办'),
        (1, '进行中'),
        (2, '已完成')
    )
    status = models.IntegerField(verbose_name='状态', choices=status_choice, default=0)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    assignee = models.ForeignKey(verbose_name='接收员工', to='Adminrole', on_delete=models.CASCADE)
    creator = models.ForeignKey(verbose_name='创建人', to='Adminrole', on_delete=models.CASCADE, related_name='created_tasks')

# 定义一个名为 Perform 的 Django 模型
class Perform(models.Model):
    # 订单号：字符类型，最长32位
    oid = models.CharField(verbose_name="订单号", max_length=32)
    # 来源：字符类型，最长32位（例如：微信、抖音、线下等）
    source = models.CharField(verbose_name="来源", max_length=32)
    # 客户姓名：字符类型，最长32位（此处字段名与内容不匹配，建议修正）
    title = models.CharField(verbose_name="客户姓名", max_length=32)
    # 成交日期：日期类型，无长度限制
    times = models.DateField(verbose_name="成交日期")
    # 成交金额：字符类型，最长32位（此处不建议使用 CharField）
    price = models.CharField(verbose_name="成交金额", max_length=32)
    # 销售人员：字符类型，最长32位
    name = models.CharField(verbose_name="销售人员", max_length=32)
    # 详情：图片类型，用于上传业绩相关图片
    image = models.ImageField(verbose_name="业绩图片", upload_to='perform/')