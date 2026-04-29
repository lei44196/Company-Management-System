"""
Redis缓存工具模块

【修改目的和背景】
为了提升Django项目的性能，通过Redis实现查询缓存和Session存储功能：
1. 查询缓存：减少高频数据库查询，提升响应速度
2. Session存储：替代默认数据库Session，支持分布式部署

【实现思路】
- 使用单例模式管理Redis连接，避免重复创建连接
- 提供装饰器简化缓存逻辑的使用
- 实现缓存穿透和击穿防护机制
- 支持缓存开关配置，便于调试和维护

【关键特性】
- 缓存过期策略（默认300秒，可自定义）
- 缓存穿透防护（空值缓存）
- 缓存击穿防护（分布式互斥锁）
- 自动缓存失效（更新/删除时清理缓存）
- 全局缓存开关（REDIS_CACHE_ENABLED）
"""

import json
import hashlib
import time
import logging
from functools import wraps
from typing import Any, Callable, Optional, Union

import redis
from django.conf import settings
from django.core.cache import cache

# 配置日志记录器，记录缓存操作信息
logger = logging.getLogger(__name__)


class RedisCacheManager:
    """
    Redis缓存管理器（单例模式）
    
    负责管理Redis连接、缓存操作、锁机制等核心功能
    确保整个应用中只有一个Redis客户端实例，避免资源浪费
    """

    _instance = None  # 单例实例
    _redis_client = None  # Redis客户端连接

    def __new__(cls):
        """
        单例模式实现：确保只创建一个实例
        
        Returns:
            RedisCacheManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化方法：延迟初始化Redis连接"""
        if self._redis_client is None:
            self._init_redis_client()

    def _init_redis_client(self):
        """
        初始化Redis客户端连接
        
        从settings.py读取配置参数，建立与Redis服务器的连接
        支持配置：REDIS_HOST、REDIS_PORT、REDIS_DB、REDIS_PASSWORD等
        
        Raises:
            redis.ConnectionError: 连接失败时记录错误日志
        """
        try:
            # 从Django配置中读取Redis连接参数
            self._redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', '192.168.213.129'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                decode_responses=True,  # 自动将字节转为字符串
                password=getattr(settings, 'REDIS_PASSWORD', None),
                socket_timeout=5,        # 套接字超时时间（秒）
                socket_connect_timeout=5, # 连接超时时间（秒）
                retry_on_timeout=True,   # 超时后重试
                max_connections=getattr(settings, 'REDIS_MAX_CONNECTIONS', 50)
            )
            # 测试连接是否正常
            self._redis_client.ping()
            logger.info("✅ Redis连接成功")
        except redis.ConnectionError as e:
            logger.error(f"❌ Redis连接失败: {e}")
            self._redis_client = None

    @property
    def client(self) -> Optional[redis.Redis]:
        """
        获取Redis客户端实例
        
        Returns:
            redis.Redis: Redis客户端对象，连接失败时返回None
        """
        return self._redis_client

    def is_enabled(self) -> bool:
        """
        检查缓存功能是否启用
        
        判断条件：
        1. settings中REDIS_CACHE_ENABLED为True
        2. Redis客户端连接成功
        
        Returns:
            bool: True表示缓存可用，False表示不可用
        """
        return getattr(settings, 'REDIS_CACHE_ENABLED', False) and self._redis_client is not None

    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        生成唯一且可读的缓存键名
        
        【键名格式】
        当参数较短时：prefix:arg1:arg2:key1=value1:key2=value2
        当参数较长时（>100字符）：prefix:md5_hash
        
        【设计目的】
        - 唯一性：确保不同参数生成不同键名
        - 可读性：短参数保持原始格式，便于调试
        - 安全性：长参数使用hash避免键名过长
        
        Args:
            prefix: 键名前缀，用于区分不同类型的缓存
            *args: 位置参数，参与键名生成
            **kwargs: 关键字参数，参与键名生成（自动排序）
        
        Returns:
            str: 生成的缓存键名
        
        Examples:
            generate_cache_key("project_one", "Userinfo", "list", name="zhangsan")
            => "project_one:Userinfo:list:name=zhangsan"
        """
        # 将位置参数转为字符串列表
        key_parts = [str(arg) for arg in args]
        # 将关键字参数转为"key=value"格式并按key排序
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

        # 拼接所有部分
        raw_key = ":".join(key_parts) if key_parts else ""

        # 长键名使用MD5哈希压缩
        if len(raw_key) > 100:
            hash_key = hashlib.md5(raw_key.encode()).hexdigest()
            cache_key = f"{prefix}:{hash_key}"
        else:
            cache_key = f"{prefix}:{raw_key}"

        return cache_key

    def get(self, key: str) -> Optional[Any]:
        """
        从Redis获取缓存数据
        
        Args:
            key: 缓存键名
        
        Returns:
            Any: 缓存的值（已反序列化），不存在或出错时返回None
        
        【异常处理】
        - RedisError: Redis操作异常
        - JSONDecodeError: 数据反序列化失败
        """
        if not self.is_enabled():
            return None

        try:
            value = self._redis_client.get(key)
            if value:
                # 将JSON字符串反序列化为Python对象
                return json.loads(value)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ 缓存获取失败 key={key}: {e}")

        return None

    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        设置缓存数据
        
        Args:
            key: 缓存键名
            value: 要缓存的数据（会被序列化为JSON）
            expire: 过期时间（秒），默认为settings中的REDIS_CACHE_TTL（300秒）
        
        Returns:
            bool: True表示设置成功，False表示失败
        
        【序列化处理】
        - 使用json.dumps序列化，支持中文（ensure_ascii=False）
        - 使用default=str处理无法直接序列化的对象（如datetime）
        
        【注意事项】
        - 缓存值大小建议不超过1MB
        - 复杂对象建议只缓存必要字段而非完整对象
        """
        if not self.is_enabled():
            return False

        # 使用配置的默认过期时间
        if expire is None:
            expire = getattr(settings, 'REDIS_CACHE_TTL', 300)

        try:
            # 序列化数据为JSON字符串
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            # 使用SET EX命令设置缓存（自动过期）
            self._redis_client.setex(key, expire, serialized)
            return True
        except (redis.RedisError, TypeError) as e:
            logger.warning(f"⚠️ 缓存设置失败 key={key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除指定缓存
        
        Args:
            key: 要删除的缓存键名
        
        Returns:
            bool: True表示删除成功，False表示失败或缓存未启用
        """
        if not self.is_enabled():
            return False

        try:
            self._redis_client.delete(key)
            return True
        except redis.RedisError as e:
            logger.warning(f"⚠️ 缓存删除失败 key={key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        根据模式批量删除缓存
        
        【使用场景】
        当更新/删除数据后，需要清理所有相关缓存时使用
        
        Args:
            pattern: 键名匹配模式，支持通配符*和?
                     示例："project_one:Userinfo:*"
        
        Returns:
            int: 删除的缓存键数量
        
        【注意事项】
        - KEYS命令在大数据量时可能阻塞Redis，建议在非高峰时段使用
        - 生产环境可考虑使用SCAN命令替代（本实现为简化版本）
        """
        if not self.is_enabled():
            return 0

        try:
            # 查找所有匹配模式的键
            keys = self._redis_client.keys(pattern)
            if keys:
                # 批量删除
                return self._redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.warning(f"⚠️ 批量缓存删除失败 pattern={pattern}: {e}")
            return 0

    def acquire_lock(self, key: str, timeout: int = 10) -> Optional[str]:
        """
        获取分布式锁（防止缓存击穿）
        
        【缓存击穿场景】
        当某个热门缓存失效时，大量请求同时访问数据库，导致数据库压力骤增
        
        【解决方案】
        使用Redis的SET NX命令实现分布式锁：
        - 只有第一个请求能获取锁
        - 其他请求直接返回或等待
        - 锁自动超时释放，避免死锁
        
        Args:
            key: 锁的键名（通常与缓存键名相同）
            timeout: 锁的超时时间（秒），默认10秒
        
        Returns:
            str: 锁的唯一标识符（用于释放锁），获取失败返回None
        """
        if not self.is_enabled():
            return None

        # 锁的键名前缀，与普通缓存区分
        lock_key = f"lock:{key}"
        # 锁的唯一值（时间戳+对象ID），确保只有持有者能释放锁
        lock_value = f"{time.time()}:{id(self)}"

        try:
            # SET NX: 只有键不存在时才设置成功
            # SET EX: 设置过期时间，自动释放锁
            if self._redis_client.set(lock_key, lock_value, nx=True, ex=timeout):
                return lock_value
        except redis.RedisError as e:
            logger.warning(f"⚠️ 获取锁失败 key={key}: {e}")

        return None

    def release_lock(self, key: str, lock_value: str) -> bool:
        """
        释放分布式锁
        
        【安全释放】
        只有锁的持有者（lock_value匹配）才能释放锁，防止误删其他请求的锁
        
        Args:
            key: 锁的键名
            lock_value: 获取锁时返回的唯一标识符
        
        Returns:
            bool: True表示释放成功，False表示失败或锁已过期
        """
        if not self.is_enabled():
            return False

        lock_key = f"lock:{key}"

        try:
            # 获取当前锁的值
            current_value = self._redis_client.get(lock_key)
            # 只有值匹配时才删除锁
            if current_value == lock_value:
                self._redis_client.delete(lock_key)
                return True
        except redis.RedisError as e:
            logger.warning(f"⚠️ 释放锁失败 key={key}: {e}")

        return False

    def set_with_none_protection(self, key: str, value: Any, expire: int = 60) -> bool:
        """
        设置缓存（带空值防护）
        
        【缓存穿透场景】
        攻击者故意查询不存在的数据，导致每次请求都访问数据库
        
        【解决方案】
        即使查询结果为空，也缓存一个空值标记，防止重复查询
        
        Args:
            key: 缓存键名
            value: 要缓存的数据
            expire: 空值缓存的过期时间（秒），默认60秒（比正常缓存时间短）
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        if value is None:
            # 空值存储为特殊标记
            return self.set(key, {"__none_value": True}, expire)
        return self.set(key, value, expire)

    def get_with_none_check(self, key: str) -> tuple:
        """
        获取缓存（带空值检查）
        
        配合set_with_none_protection使用，区分真正的空值和缓存缺失
        
        Args:
            key: 缓存键名
        
        Returns:
            tuple: (实际值, 是否是空值标记)
                   - 如果是空值标记：(None, True)
                   - 如果是正常数据：(数据, False)
                   - 如果缓存不存在：(None, False)
        """
        value = self.get(key)
        # 判断是否为空值标记
        if value and isinstance(value, dict) and value.get("__none_value"):
            return None, True
        return value, False


# 创建全局Redis缓存管理器实例
redis_cache = RedisCacheManager()


def cache_query(model_name: str, key_prefix: str = None, expire: int = None, unless_func: Callable = None):
    """
    查询缓存装饰器
    
    【功能说明】
    自动为函数添加缓存逻辑：
    1. 检查缓存是否命中
    2. 命中则直接返回缓存数据
    3. 未命中则执行函数并缓存结果
    4. 支持缓存穿透和击穿防护
    
    【使用示例】
        @cache_query('Userinfo', key_prefix='list', expire=300)
        def get_user_data():
            return {'data': list(Userinfo.objects.all().values())}
    
    Args:
        model_name: 模型名称，用于生成缓存键（如'Userinfo'）
        key_prefix: 缓存键前缀，默认使用函数名
        expire: 缓存过期时间（秒），默认使用settings中的REDIS_CACHE_TTL
        unless_func: 条件函数，返回True时跳过缓存（用于特殊场景）
    
    【缓存键格式】
    {REDIS_CACHE_PREFIX}:{model_name}:{key_prefix}:{args}:{kwargs}
    
    【注意事项】
    - 被装饰函数的返回值必须是可JSON序列化的字典类型
    - 对于有参数的函数，不同参数会生成不同的缓存键
    - 视图函数（返回HttpResponse）不应使用此装饰器，会导致错误
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查缓存是否启用
            if not redis_cache.is_enabled():
                return func(*args, **kwargs)

            # 检查是否需要跳过缓存
            if unless_func and unless_func(*args, **kwargs):
                return func(*args, **kwargs)

            # 生成缓存键名
            prefix = key_prefix or func.__name__
            cache_key = redis_cache.generate_cache_key(
                f"{getattr(settings, 'REDIS_CACHE_PREFIX', 'django')}:{model_name}:{prefix}",
                *args,
                **kwargs
            )

            # 尝试从缓存获取数据（带空值检查）
            cached_value, is_none = redis_cache.get_with_none_check(cache_key)
            if cached_value is not None:
                logger.debug(f"📥 缓存命中: {cache_key}")
                # 只返回字典类型的缓存数据
                if isinstance(cached_value, dict):
                    return cached_value
                else:
                    # 缓存数据类型不正确，跳过缓存重新执行
                    logger.warning(f"⚠️ 缓存数据类型错误，跳过缓存: {cache_key}")

            # 获取分布式锁（防止缓存击穿）
            lock_value = redis_cache.acquire_lock(cache_key)
            if lock_value is None:
                # 获取锁失败，直接执行函数（降级处理）
                return func(*args, **kwargs)

            try:
                # 获取锁成功，执行函数获取数据
                result = func(*args, **kwargs)
                
                # 只缓存字典类型的数据
                # 视图函数返回的HttpResponse对象不应该被缓存
                if isinstance(result, dict):
                    ttl = expire or getattr(settings, 'REDIS_CACHE_TTL', 300)
                    redis_cache.set_with_none_protection(cache_key, result, ttl)
                    logger.debug(f"📤 缓存设置: {cache_key}")
                
                return result
            finally:
                # 无论成功与否，都释放锁
                redis_cache.release_lock(cache_key, lock_value)

        return wrapper
    return decorator


def cache_invalidated(model_name: str, key_prefix: str = None):
    """
    缓存失效装饰器
    
    【功能说明】
    在执行更新/删除操作后自动清理相关缓存，确保数据一致性
    
    【使用示例】
        @cache_invalidated('Userinfo', 'list')
        def user_del(request, nid):
            Userinfo.objects.filter(id=nid).delete()
            return redirect('/user/')
    
    Args:
        model_name: 模型名称，用于匹配缓存键
        key_prefix: 缓存键前缀，默认使用函数名
    
    【清理逻辑】
    删除所有匹配模式 "{REDIS_CACHE_PREFIX}:{model_name}:{key_prefix}:*" 的缓存
    
    【注意事项】
    - 建议在所有修改数据的操作上使用此装饰器
    - 如果有多个缓存键前缀，需要分别调用或使用通配符
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存匹配模式
            prefix = key_prefix or func.__name__
            pattern = f"{getattr(settings, 'REDIS_CACHE_PREFIX', 'django')}:{model_name}:{prefix}:*"

            # 先执行原函数（删除/更新操作）
            result = func(*args, **kwargs)

            # 清理相关缓存
            deleted = redis_cache.delete_pattern(pattern)
            if deleted > 0:
                logger.info(f"🗑️ 缓存清理: {pattern}, 删除 {deleted} 条")

            return result

        return wrapper
    return decorator


class QueryCacheMixin:
    """
    模型缓存混合类
    
    【功能说明】
    为Django模型添加自动缓存失效功能：
    - 当模型实例保存时自动清理相关缓存
    - 当模型实例删除时自动清理相关缓存
    
    【使用方式】
        class Userinfo(QueryCacheMixin, models.Model):
            model_name = 'Userinfo'  # 可选，默认使用类名
            ...
    
    【注意事项】
    - 需要将此Mixin放在models.Model之前
    - 如果模型名与类名不同，需要设置model_name属性
    """

    model_name = None  # 自定义模型名称（可选）

    def save(self, *args, **kwargs):
        """重写save方法：保存后清理缓存"""
        result = super().save(*args, **kwargs)
        self._invalidate_cache()
        return result

    def delete(self, *args, **kwargs):
        """重写delete方法：删除前清理缓存"""
        self._invalidate_cache()
        return super().delete(*args, **kwargs)

    def _invalidate_cache(self):
        """清理当前模型相关的所有缓存"""
        if not redis_cache.is_enabled():
            return

        # 使用自定义模型名或类名
        model_name = self.model_name or self.__class__.__name__
        pattern = f"{getattr(settings, 'REDIS_CACHE_PREFIX', 'django')}:{model_name}:*"
        deleted = redis_cache.delete_pattern(pattern)
        logger.info(f"🗑️ 模型 {model_name} 缓存已清理，删除 {deleted} 条")


def get_cache_stats() -> dict:
    """
    获取Redis缓存统计信息
    
    【统计内容】
    - status: 连接状态（connected/disabled/error）
    - used_memory: 使用内存大小（人类可读格式）
    - connected_clients: 当前连接数
    - total_commands_processed: 处理的命令总数
    - keyspace_hits: 缓存命中次数
    - keyspace_misses: 缓存未命中次数
    
    Returns:
        dict: 统计信息字典
    """
    if not redis_cache.is_enabled():
        return {"status": "disabled", "message": "缓存功能未启用"}

    try:
        # 获取Redis服务器信息
        info = redis_cache.client.info()
        return {
            "status": "connected",
            "used_memory": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": f"{info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1) * 100):.1f}%"
        }
    except redis.RedisError as e:
        return {"status": "error", "message": str(e)}