"""
Redis缓存和Session测试用例

测试内容：
1. Redis连接测试
2. 缓存基础功能测试（设置、获取、删除）
3. 缓存键名生成测试
4. 缓存装饰器测试
5. 缓存穿透/击穿防护测试
6. Session存储测试
7. 缓存清理测试

运行方式：
python manage.py test project_one.tests.test_redis
或
python manage.py shell < project_one/tests/test_redis.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

import time
import json
from django.test import TestCase, Client
from django.contrib.sessions.backends.cache import SessionStore
from django.conf import settings

from project_one.utils.redis_cache import (
    redis_cache,
    cache_query,
    cache_invalidated,
    get_cache_stats,
    RedisCacheManager
)
from project_one import models


class RedisConnectionTest(TestCase):
    """Redis连接测试"""

    def test_redis_connection(self):
        """测试Redis是否能正常连接"""
        client = redis_cache.client
        if client:
            result = client.ping()
            self.assertTrue(result, "Redis连接失败")
        else:
            self.skipTest("Redis未启用，跳过连接测试")

    def test_redis_cache_enabled(self):
        """测试缓存开关配置"""
        is_enabled = redis_cache.is_enabled()
        print(f"\n缓存状态: {'已启用' if is_enabled else '已禁用'}")


class CacheBasicOperationTest(TestCase):
    """缓存基础操作测试"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key = "test:unit:basic"
        test_value = {"name": "test", "value": 123}

        result = redis_cache.set(test_key, test_value, expire=60)
        self.assertTrue(result, "缓存设置失败")

        cached = redis_cache.get(test_key)
        self.assertEqual(cached, test_value, "缓存获取值不匹配")

        redis_cache.delete(test_key)

    def test_cache_delete(self):
        """测试缓存删除"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key = "test:unit:delete"
        redis_cache.set(test_key, "value", expire=60)

        result = redis_cache.delete(test_key)
        self.assertTrue(result, "缓存删除失败")

        cached = redis_cache.get(test_key)
        self.assertIsNone(cached, "缓存未正确删除")

    def test_cache_expire(self):
        """测试缓存过期"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key = "test:unit:expire"
        redis_cache.set(test_key, "value", expire=2)

        cached1 = redis_cache.get(test_key)
        self.assertEqual(cached1, "value", "缓存未正确设置")

        time.sleep(3)
        cached2 = redis_cache.get(test_key)
        self.assertIsNone(cached2, "缓存过期后不应返回数据")


class CacheKeyGenerationTest(TestCase):
    """缓存键名生成测试"""

    def test_generate_cache_key(self):
        """测试缓存键名生成"""
        key1 = redis_cache.generate_cache_key("app", "model", "filter", name="test", age=20)
        key2 = redis_cache.generate_cache_key("app", "model", "filter", name="test", age=20)
        key3 = redis_cache.generate_cache_key("app", "model", "filter", name="test", age=21)

        self.assertEqual(key1, key2, "相同参数应生成相同键名")
        self.assertNotEqual(key1, key3, "不同参数应生成不同键名")
        self.assertTrue(key1.startswith("app:model:filter:"), "键名格式不正确")

    def test_generate_cache_key_with_long_args(self):
        """测试长参数键名生成（应使用hash）"""
        long_arg = "a" * 200
        key = redis_cache.generate_cache_key("prefix", long_arg)
        self.assertTrue(len(key) < 150, "长参数键名应被hash压缩")


class CachePenetrationProtectionTest(TestCase):
    """缓存穿透防护测试"""

    def test_none_value_protection(self):
        """测试空值防护"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key = "test:unit:none"

        redis_cache.set_with_none_protection(test_key, None, expire=60)
        cached, is_none = redis_cache.get_with_none_check(test_key)

        self.assertTrue(is_none, "空值应被标记")
        self.assertIsNone(cached, "空值返回应为None")

    def test_none_protection_different_from_missing(self):
        """测试空值保护与缺失值的区别"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key1 = "test:unit:none_key1"
        test_key2 = "test:unit:none_key2"

        redis_cache.set_with_none_protection(test_key1, None, expire=60)
        redis_cache.set(test_key2, "value", expire=60)

        cached1, is_none1 = redis_cache.get_with_none_check(test_key1)
        cached2, is_none2 = redis_cache.get_with_none_check(test_key2)

        self.assertTrue(is_none1, "空值应有标记")
        self.assertFalse(is_none2, "正常值不应有标记")
        self.assertIsNone(cached1, "空值返回None")
        self.assertEqual(cached2, "value", "正常值应正常返回")


class CacheMutexLockTest(TestCase):
    """缓存互斥锁测试"""

    def test_acquire_and_release_lock(self):
        """测试获取和释放锁"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key = "test:unit:lock"

        lock_value = redis_cache.acquire_lock(test_key, timeout=10)
        self.assertIsNotNone(lock_value, "应成功获取锁")

        result = redis_cache.release_lock(test_key, lock_value)
        self.assertTrue(result, "应成功释放锁")

    def test_lock_prevents_double_acquire(self):
        """测试锁防止重复获取"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        test_key = "test:unit:double_lock"

        lock1 = redis_cache.acquire_lock(test_key, timeout=10)
        lock2 = redis_cache.acquire_lock(test_key, timeout=10)

        self.assertIsNotNone(lock1, "第一次应获取锁成功")
        self.assertIsNone(lock2, "第二次获取锁应失败")

        redis_cache.release_lock(test_key, lock1)


class CacheDecoratorTest(TestCase):
    """缓存装饰器测试"""

    def test_cache_query_decorator(self):
        """测试查询缓存装饰器"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        call_count = [0]

        @cache_query('TestModel', key_prefix='test', expire=60)
        def expensive_operation():
            call_count[0] += 1
            return {"result": "data", "count": call_count[0]}

        result1 = expensive_operation()
        result2 = expensive_operation()

        self.assertEqual(call_count[0], 1, "第二次调用应使用缓存")
        self.assertEqual(result1, result2, "两次调用结果应相同")

        redis_cache.delete_pattern("project_one:TestModel:test:*")

    def test_cache_invalidated_decorator(self):
        """测试缓存失效装饰器"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        call_count = [0]

        @cache_query('TestModel2', key_prefix='test', expire=60)
        def cached_function():
            call_count[0] += 1
            return {"count": call_count[0]}

        @cache_invalidated('TestModel2', 'test')
        def update_operation():
            return "updated"

        cached_function()
        self.assertEqual(call_count[0], 1)

        update_operation()

        result = cached_function()
        self.assertEqual(call_count[0], 2, "缓存失效后应重新计算")
        self.assertEqual(result["count"], 2, "结果应反映新的计数值")


class SessionStorageTest(TestCase):
    """Session存储测试"""

    def test_session_create_and_read(self):
        """测试Session创建和读取"""
        session = SessionStore()

        session['user_id'] = 123
        session['username'] = 'testuser'
        session.save()

        session_key = session.session_key
        self.assertIsNotNone(session_key, "Session Key不应为空")

        session2 = SessionStore(session_key=session_key)
        self.assertEqual(session2['user_id'], 123, "Session数据应正确读取")
        self.assertEqual(session2['username'], 'testuser', "Session数据应正确读取")

    def test_session_update_and_delete(self):
        """测试Session更新和删除"""
        session = SessionStore()

        session['test'] = 'value'
        session.save()

        session['test'] = 'new_value'
        session.save()

        session2 = SessionStore(session_key=session.session_key)
        self.assertEqual(session2['test'], 'new_value', "Session更新应成功")

        del session2['test']
        session2.save()

        session3 = SessionStore(session_key=session.session_key)
        self.assertIsNone(session3.get('test'), "Session删除应成功")

    def test_session_expiry(self):
        """测试Session过期"""
        session = SessionStore()
        session.set_expiry(2)

        session['data'] = 'test'
        session.save()

        time.sleep(3)

        expired_session = SessionStore(session_key=session.session_key)
        self.assertIsNone(expired_session.get('data'), "过期Session不应返回数据")


class ViewCacheIntegrationTest(TestCase):
    """视图缓存集成测试"""

    def setUp(self):
        self.client = Client()

    def test_user_list_cache(self):
        """测试用户列表缓存"""
        if not redis_cache.is_enabled():
            self.skipTest("缓存未启用")

        Department = models.Department
        if not Department.objects.exists():
            Department.objects.create(title="测试部门")

        response1 = self.client.get('/user/')
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get('/user/')
        self.assertEqual(response2.status_code, 200)

    def test_session_in_view(self):
        """测试视图中的Session使用"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()

        response2 = self.client.get('/')
        self.assertEqual(response2.status_code, 200)


class CacheStatsTest(TestCase):
    """缓存统计测试"""

    def test_get_cache_stats(self):
        """测试获取缓存统计信息"""
        stats = get_cache_stats()
        self.assertIn('status', stats)
        print(f"\n缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Redis缓存和Session测试")
    print("=" * 60)

    test_classes = [
        RedisConnectionTest,
        CacheBasicOperationTest,
        CacheKeyGenerationTest,
        CachePenetrationProtectionTest,
        CacheMutexLockTest,
        CacheDecoratorTest,
        SessionStorageTest,
        ViewCacheIntegrationTest,
        CacheStatsTest,
    ]

    total = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n{'-' * 60}")
        print(f"测试类: {test_class.__name__}")
        print(f"{'-' * 60}")

        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]

        for method_name in methods:
            total += 1
            method = getattr(instance, method_name)
            try:
                print(f"\n>>> {method_name}...")
                method()
                print(f"    结果: PASS")
                passed += 1
            except Exception as e:
                print(f"    结果: FAIL - {e}")
                failed += 1

    print(f"\n{'=' * 60}")
    print(f"测试总结: 总计 {total} 个测试, 通过 {passed}, 失败 {failed}")
    print(f"{'=' * 60}\n")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
