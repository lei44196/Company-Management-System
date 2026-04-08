# Django资产与任务管理系统

## 项目概述

Django资产与任务管理系统是一个基于Django框架开发的企业级管理系统，主要用于管理企业的资产、员工、部门、任务和绩效等信息。系统采用B/S架构，前端使用Bootstrap框架构建响应式界面，后端使用Django框架提供RESTful API，数据库使用MySQL存储数据。

### 主要功能模块

- **用户管理**：包括管理员账号管理、员工管理、部门管理等
- **资产管理**：包括资产的添加、修改、删除、列表展示和导入功能
- **任务管理**：包括任务的分配、跟踪和管理，集成了Arcgis地图功能
- **绩效管理**：包括绩效的添加、修改、删除和列表展示，支持图片上传
- **权限控制**：基于角色的权限管理，区分员工、领导和管理员权限
- **验证码系统**：登录时的验证码验证功能，提高系统安全性

### 技术栈

- **前端**：HTML5、CSS3、JavaScript、Bootstrap 5
- **后端**：Python 3.10+、Django 6.0
- **数据库**：MySQL 8.0+
- **其他**：Arcgis JavaScript API（任务管理地图功能）

## 功能特点

### 1. 完整的权限管理系统

- 基于中间件的权限控制，实现了员工、领导和管理员的权限分级
- 员工只能查看数据，不能进行增删改操作
- 领导和管理员具有完整的操作权限
- 未登录用户自动跳转到登录页面
- 权限不足时显示友好的提示信息

### 2. 强大的资产管理功能

- 支持资产的添加、修改、删除和列表展示
- 支持资产的批量导入功能（Excel文件）
- 支持资产数据的搜索和分页
- 资产详情页面支持图片展示

### 3. 任务管理与地图集成

- 支持任务的添加、修改、删除和列表展示
- 集成Arcgis JavaScript API，提供地图可视化功能
- 任务分配支持员工选择和状态跟踪

### 4. 绩效管理系统

- 支持绩效的添加、修改、删除和列表展示
- 支持绩效图片的上传和展示
- 绩效详情页面支持图片链接点击查看

### 5. 安全的登录系统

- 基于session的用户认证
- 登录时的验证码验证功能
- 密码MD5加密存储

### 6. 其他特点

- 响应式设计，适配不同设备
- 统一的页面风格和操作流程
- 详细的代码注释，便于维护和扩展
- 模块化设计，便于功能扩展

## 安装指南

### 1. 环境要求

- Python 3.10+
- MySQL 8.0+
- Django 6.0+
- 其他依赖包（见requirements.txt）

### 2. 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**
   - 修改 `djangoProject/settings.py` 中的数据库配置
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'project_one',  # 数据库名字
           'USER': 'root',
           'PASSWORD': 'root',
           'HOST': '127.0.0.1',  # 那台机器安装了MySQL
           'PORT': 3306,
       }
   }
   ```

5. **数据库迁移**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **创建超级用户**
   ```bash
   python manage.py createsuperuser
   ```

7. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```

8. **访问系统**
   打开浏览器，访问 http://127.0.0.1:8000/login/，使用超级用户账号登录

## 使用说明

### 1. 登录系统

- 访问 http://127.0.0.1:8000/login/
- 输入用户名和密码
- 输入验证码
- 点击登录按钮

### 2. 资产管理

- **资产列表**：访问 http://127.0.0.1:8000/asset/，查看所有资产
- **添加资产**：点击"添加资产"按钮，填写资产信息并保存
- **修改资产**：在资产列表页面点击"修改"按钮，修改资产信息并保存
- **删除资产**：在资产列表页面点击"删除"按钮，确认后删除资产
- **导入资产**：点击"导入资产"按钮，上传Excel文件导入资产数据

### 3. 任务管理

- **任务列表**：访问 http://127.0.0.1:8000/task/，查看所有任务
- **添加任务**：点击"添加任务"按钮，填写任务信息并保存
- **修改任务**：在任务列表页面点击"修改"按钮，修改任务信息并保存
- **删除任务**：在任务列表页面点击"删除"按钮，确认后删除任务
- **地图查看**：在任务详情页面查看任务的地图位置

### 4. 绩效管理

- **绩效列表**：访问 http://127.0.0.1:8000/perform/，查看所有绩效
- **添加绩效**：点击"添加绩效"按钮，填写绩效信息并上传图片
- **修改绩效**：在绩效列表页面点击"修改"按钮，修改绩效信息并保存
- **删除绩效**：在绩效列表页面点击"删除"按钮，确认后删除绩效
- **查看图片**：在绩效列表页面点击图片链接，在新窗口查看图片

### 5. 员工管理

- **员工列表**：访问 http://127.0.0.1:8000/user/，查看所有员工
- **添加员工**：点击"添加员工"按钮，填写员工信息并保存
- **修改员工**：在员工列表页面点击"修改"按钮，修改员工信息并保存
- **删除员工**：在员工列表页面点击"删除"按钮，确认后删除员工

### 6. 部门管理

- **部门列表**：访问 http://127.0.0.1:8000/depart/，查看所有部门
- **添加部门**：点击"添加部门"按钮，填写部门信息并保存
- **修改部门**：在部门列表页面点击"修改"按钮，修改部门信息并保存
- **删除部门**：在部门列表页面点击"删除"按钮，确认后删除部门

### 7. 管理员管理

- **管理员列表**：访问 http://127.0.0.1:8000/admin_role/，查看所有管理员
- **添加管理员**：点击"添加账号"按钮，填写管理员信息并保存
- **修改管理员**：在管理员列表页面点击"修改"按钮，修改管理员信息并保存
- **重置密码**：在管理员列表页面点击"重置密码"按钮，重置管理员密码

## 目录结构

```
djangoProject/                  # 项目根目录
├── djangoProject/              # 项目配置目录
│   ├── __init__.py
│   ├── settings.py             # 项目设置
│   ├── urls.py                 # 项目路由
│   └── wsgi.py                 # WSGI配置
├── project_one/                # 应用目录
│   ├── __init__.py
│   ├── admin.py                # 后台管理
│   ├── apps.py                 # 应用配置
│   ├── middle/                 # 中间件目录
│   │   └── middle.py           # 权限控制中间件
│   ├── migrations/             # 数据库迁移文件
│   ├── models.py               # 数据模型
│   ├── static/                 # 静态文件
│   │   ├── css/                # CSS文件
│   │   └── js/                 # JavaScript文件
│   ├── templates/              # 模板文件
│   │   ├── asset/              # 资产相关模板
│   │   ├── depart/             # 部门相关模板
│   │   ├── index/              # 基础模板
│   │   ├── login/              # 登录相关模板
│   │   ├── perform/            # 绩效相关模板
│   │   ├── task/               # 任务相关模板
│   │   ├── user/               # 员工相关模板
│   │   └── permission_denied.html  # 权限不足页面
│   ├── utils/                  # 工具函数
│   │   ├── code.py             # 验证码生成
│   │   ├── pagination.py       # 分页工具
│   │   └── pwd_data.py         # 密码加密
│   ├── views/                  # 视图函数
│   │   ├── admin_role.py       # 管理员管理
│   │   ├── asset.py            # 资产管理
│   │   ├── depart.py           # 部门管理
│   │   ├── login.py            # 登录管理
│   │   ├── perform.py          # 绩效管理
│   │   ├── task.py             # 任务管理
│   │   └── user.py             # 员工管理
│   └── urls.py                 # 应用路由
├── manage.py                   # 项目管理脚本
├── README.md                   # 项目文档
└── requirements.txt            # 依赖包列表
```

## 贡献指南

### 1. 代码规范

- 遵循PEP 8代码风格指南
- 为所有函数和类添加详细的文档字符串
- 使用有意义的变量和函数名
- 保持代码简洁明了

### 2. 提交规范

- 提交信息应清晰描述修改内容
- 遵循以下提交信息格式：
  ```
  [类型] 简短描述

  详细描述（可选）
  ```
- 类型包括：feat（新功能）、fix（修复）、docs（文档）、style（样式）、refactor（重构）、test（测试）、chore（构建/依赖）

### 3. 分支管理

- `master` 分支：稳定版本，用于生产环境
- `develop` 分支：开发版本，用于集成新功能
- 功能分支：从develop分支创建，用于开发特定功能
- 修复分支：从master分支创建，用于修复生产环境bug

### 4. 提交流程

1. Fork项目仓库
2. 创建功能分支
3. 实现功能或修复bug
4. 编写测试
5. 提交代码
6. 创建Pull Request

## 许可证信息

本项目采用MIT许可证，详见LICENSE文件。

### MIT许可证

```
MIT License

Copyright (c) 2026 Django资产与任务管理系统

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
