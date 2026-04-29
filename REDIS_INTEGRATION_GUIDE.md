"""
Redis集成配置说明文档
=====================

本项目已成功集成Redis，实现了：
1. 查询操作缓存优化
2. Redis替代默认Session存储

## 一、依赖安装

```bash
pip install django-redis redis
```

## 二、settings.py配置说明

### 2.1 Redis基础配置

```python
REDIS_HOST = '192.168.213.129'      # Redis服务器地址
REDIS_PORT = 6379                   # Redis端口
REDIS_DB = 1                        # Redis数据库编号
REDIS_PASSWORD = None                # Redis密码（如果有）
REDIS_MAX_CONNECTIONS = 50           # 最大连接数
```

### 2.2 缓存配置

```python
# 缓存总开关（设为False可禁用所有缓存）
REDIS_CACHE_ENABLED = True

# 缓存前缀（用于区分不同项目的缓存）
REDIS_CACHE_PREFIX = 'project_one'

# 默认缓存过期时间（秒）
REDIS_CACHE_TTL = 300
```

### 2.3 Session配置

```python
# 使用Redis存储Session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Session过期时间（秒），默认24小时
SESSION_COOKIE_AGE = 86400

# 关闭浏览器时删除Session
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 每次请求都保存Session
SESSION_SAVE_EVERY_REQUEST = True
```

## 三、使用方式

### 3.1 查询缓存

为视图函数添加 `@cache_query` 装饰器即可启用缓存：

```python
from project_one.utils.redis_cache import cache_query, cache_invalidated

@cache_query('Userinfo', key_prefix='list', expire=300)
def user_list(request):
    # 首次调用会执行数据库查询，结果存入Redis
    # 后续调用（300秒内）直接从Redis返回缓存结果
    queryset = models.Userinfo.objects.all()
    page_data = paginate(request, queryset, page_size=10, search_fields=['name'])
    return render(request, "user/user_list.html", page_data)
```

**装饰器参数：**
- `model_name`: 模型名称，用于生成缓存键
- `key_prefix`: 缓存键前缀，默认使用函数名
- `expire`: 缓存过期时间（秒），默认使用配置值
- `unless_func`: 条件函数，返回True时跳过缓存

### 3.2 缓存失效

在执行删除/更新操作后，使用 `@cache_invalidated` 装饰器自动清理缓存：

```python
@cache_invalidated('Userinfo', 'list')
def user_del(request, nid):
    # 删除用户后，自动清理Userinfo相关的list缓存
    models.Userinfo.objects.filter(id=nid).delete()
    return redirect("/user/")

@cache_invalidated('Userinfo', 'list')
def user_modify(request, nid):
    # 修改用户后，自动清理Userinfo相关的list缓存
    obj = models.Userinfo.objects.filter(id=nid).first()
    form = UserModelForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
    return redirect("/user/")
```

### 3.3 Session使用

Session的创建、读取、更新、删除完全兼容Django原生API，无需修改任何业务代码：

```python
# 创建/更新Session
request.session['user_id'] = 123
request.session['username'] = 'test'

# 读取Session
user_id = request.session.get('user_id')

# 删除Session数据
del request.session['user_id']

# Session过期
request.session.set_expiry(0)  # 浏览器关闭时过期
request.session.set_expiry(3600)  # 1小时后过期
```

## 四、性能优化点

### 4.1 查询缓存优化
- **减少数据库压力**: 频繁查询的数据（如列表页）从Redis返回，数据库压力大幅降低
- **提升响应速度**: Redis内存访问比MySQL快10-100倍
- **支持搜索**: 缓存包含搜索条件，不同搜索条件独立缓存

### 4.2 Session优化
- **分布式共享**: 多台服务器共享Session，适合集群部署
- **高性能**: 比数据库Session快数百倍
- **自动清理**: Redis自动处理过期Session

### 4.3 连接池优化
```python
'CONNECTION_POOL_KWARGS': {
    'max_connections': 50,
    'retry_on_timeout': True,
}
```
- **复用连接**: 减少连接创建销毁开销
- **并发控制**: 限制最大连接数，防止资源耗尽

## 五、注意事项

### 5.1 Redis连接异常处理
```python
try:
    redis_cache.set(key, value, expire=300)
except redis.RedisError as e:
    logger.error(f"Redis操作失败: {e}")
    # 降级处理：继续使用数据库
```
当Redis不可用时，系统会自动降级，不影响业务运行。

### 5.2 缓存数据一致性
- **写操作时清理缓存**: 所有更新/删除操作都应使用 `@cache_invalidated`
- **缓存过期时间**: 根据数据更新频率设置合适的过期时间
- **不建议使用**: 对实时性要求极高的数据

### 5.3 缓存键命名规范
```
格式: {前缀}:{应用名}:{模型名}:{键名}
示例: project_one:Userinfo:list

对于带参数的查询:
project_one:Userinfo:list:name=zhangsan
```

### 5.4 内存管理
- **设置合理的过期时间**: 避免大量数据永久驻留Redis
- **监控内存使用**: 使用 `redis_cache.client.info()` 查看内存使用
- **及时清理**: 删除/更新操作时清理相关缓存

### 5.5 安全注意事项
- **Redis密码**: 生产环境务必设置Redis密码
- **SESSION_COOKIE_HTTPONLY**: 防止XSS攻击窃取Session
- **SESSION_COOKIE_SECURE**: 生产环境设为True，仅HTTPS传输

## 六、测试验证

### 6.1 启动项目
```bash
python manage.py runserver 0.0.0.0:8000
```

### 6.2 运行测试用例
```bash
python project_one/tests/test_redis.py
```

### 6.3 手动验证
1. 访问 http://localhost:8000/user/ 查看用户列表
2. 登录后检查浏览器Cookie中是否有sessionid
3. 在Redis中查看数据：
   ```bash
   redis-cli -h 192.168.213.129 -p 6379
   KEYS project_one:*    # 查看所有缓存键
   GET session:xxx       # 查看Session数据
   ```

## 七、配置开关

### 7.1 禁用缓存
```python
# settings.py
REDIS_CACHE_ENABLED = False
```
禁用后所有查询直接访问数据库，缓存装饰器自动失效。

### 7.2 修改缓存过期时间
```python
# 全局默认
REDIS_CACHE_TTL = 300  # 5分钟

# 单个视图指定
@cache_query('Userinfo', key_prefix='list', expire=60)
def user_list(request):
    ...
```

## 八、故障排查

### 8.1 Redis连接失败
- 检查Redis服务是否启动: `redis-cli ping`
- 检查网络连通性: `telnet 192.168.213.129 6379`
- 检查防火墙设置

### 8.2 缓存未生效
- 确认 `REDIS_CACHE_ENABLED = True`
- 检查装饰器是否正确添加
- 查看日志中的缓存命中/未命中信息

### 8.3 Session丢失
- 确认使用同一个Redis数据库（默认DB 1）
- 检查浏览器Cookie是否被禁用
- 确认SESSION_CACHE_ALIAS配置正确
"""