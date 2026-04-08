# 导入hashlib模块，用于实现MD5加密功能
import hashlib  # 提供了多种哈希算法，包括MD5


# 密钥，用于MD5加密的盐值
# 盐值的作用是增加密码的安全性，即使相同的密码生成的哈希值也会不同
SECRET_KEY = 'django-insecure-wat!x=&@1t0u-))nfxt)fs*_jfkv(18kbr3u%d#b5(=+*y^7i-'

def md5(data):
    """MD5加密函数
    功能：对输入的数据进行MD5加密，返回加密后的哈希值
    参数：
        data: 要加密的数据，通常是用户密码
    返回值：
        加密后的MD5哈希值（32位十六进制字符串）
    
    实现步骤：
    1. 创建MD5对象，并使用密钥作为盐值
    2. 更新MD5对象，添加要加密的数据
    3. 返回加密后的哈希值
    
    使用场景：
    - 当用户注册或修改密码时，对密码进行加密后存储到数据库
    - 当用户登录时，对输入的密码进行加密后与数据库中存储的哈希值进行比较
    - 确保密码在数据库中以加密形式存储，提高安全性
    """
    # 创建MD5对象，并使用SECRET_KEY作为盐值
    # 盐值的作用是增加密码的安全性，防止彩虹表攻击
    obj_md5 = hashlib.md5(SECRET_KEY.encode("utf-8"))
    
    # 更新MD5对象，添加要加密的数据
    # encode("utf-8")将字符串转换为字节串，因为MD5处理的是字节串
    obj_md5.update(data.encode("utf-8"))
    
    # 返回加密后的哈希值，使用hexdigest()方法获取十六进制格式的哈希值
    return obj_md5.hexdigest()