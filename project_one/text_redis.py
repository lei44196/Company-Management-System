import redis


# 定义Redis连接函数（可选，封装成函数更规范）
def connect_redis():
    # 建立连接（替换成你的虚拟机IP和密码）
    r = redis.Redis(
        host='192.168.213.129',  # 你的虚拟机IP
        port=6379,

        decode_responses=True  # 返回字符串，不是字节
    )
    return r


# 程序入口：只有直接运行这个文件时，才会执行下面的代码
if __name__ == "__main__":
    # 调用连接函数
    redis_client = connect_redis()

    # 测试Redis操作
    redis_client.set('test_key', 'Hello Redis!')
    result = redis_client.get('test_key')
    print("Redis返回结果：", result)  # 输出：Redis返回结果： Hello Redis!