# 导入PIL库的相关模块，用于图像处理
from PIL import Image, ImageFont, ImageDraw  # Image用于创建图像，ImageFont用于设置字体，ImageDraw用于绘制内容
from random import choice, randint  # choice用于随机选择字符，randint用于生成随机整数
import string  # 提供字符串常量，如大写字母和数字


def creat_image_content():
    """生成验证码图片的函数
    功能：生成一张包含4位随机字符、干扰曲线和干扰点的验证码图片
    返回值：(Image对象, 验证码字符串) - 用于在前端显示图片和在后端验证用户输入
    
    实现步骤：
    1. 创建白色背景的画布
    2. 尝试加载字体，失败则使用默认字体
    3. 生成4位随机验证码（包含大写字母和数字）
    4. 在画布上绘制验证码字符，每个字符随机位置微调
    5. 添加干扰曲线，增加识别难度
    6. 添加干扰点，进一步增加识别难度
    7. 返回生成的图片和验证码字符串
    
    使用场景：
    - 当用户登录时，前端页面会调用此函数获取图片验证码
    - 验证码图片显示在登录表单中，用户需要输入正确的验证码才能登录
    - 防止自动化程序恶意登录系统
    """
    # 画布尺寸设置为110x40像素，适合显示4位验证码
    width, height = 110, 40
    # 创建白色背景画布，mode='RGB'表示使用RGB颜色模式
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    # 创建绘图对象，用于在画布上绘制内容
    draw = ImageDraw.Draw(img, mode='RGB')

    # 尝试加载arial.ttf字体，若失败则使用默认字体
    # 这样做的原因是确保在不同环境下都能正常显示字体
    try:
        font = ImageFont.truetype('arial.ttf', size=28)  # 设置字体大小为28
    except IOError:
        font = ImageFont.load_default()  # 使用默认字体

    # 生成随机验证码（4位，包含大写字母和数字）
    # string.ascii_uppercase获取所有大写字母，string.digits获取所有数字
    chars = string.ascii_uppercase + string.digits
    # 使用列表推导式和join方法生成4位随机验证码
    code = ''.join(choice(chars) for _ in range(4))

    # 逐个绘制字符，随机位置微调（增加识别难度）
    x_start = 10  # 起始X坐标
    for i, char in enumerate(code):
        # 随机颜色：深色系（0-100），避免与干扰项混淆
        color = (randint(0, 100), randint(0, 100), randint(0, 100))
        # 每个字符的Y轴随机偏移(-3到3像素)，增加识别难度
        y_offset = randint(-3, 3)
        # 在画布上绘制字符，位置为(x_start + i * 25, 5 + y_offset)
        draw.text((x_start + i * 25, 5 + y_offset), char, fill=color, font=font)

    # ---- 添加干扰曲线 ----
    for _ in range(3):  # 绘制3条曲线
        # 随机起始点和结束点
        start = (randint(0, width // 3), randint(0, height))
        end = (randint(width * 2 // 3, width), randint(0, height))
        # 控制点（使曲线更随机）
        ctrl1 = (randint(0, width), randint(0, height))
        ctrl2 = (randint(0, width), randint(0, height))
        # 曲线颜色（浅灰或彩色，使用较亮颜色）
        curve_color = (randint(100, 200), randint(100, 200), randint(100, 200))
        # 绘制贝塞尔曲线（使用line配合point列表简化）
        points = []
        for t in range(0, 101, 5):  # 按步长5采样点
            # 二次贝塞尔曲线公式 B(t) = (1-t)^2*P0 + 2(1-t)t*P1 + t^2*P2
            t /= 100.0
            x = (1-t)**2 * start[0] + 2*(1-t)*t * ctrl1[0] + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * ctrl1[1] + t**2 * end[1]
            points.append((x, y))
        draw.line(points, fill=curve_color, width=1)

        # 再添加一条简单的正弦波样式的曲线（另一种干扰）
        wave_points = []
        for x in range(0, width, 5):
            y = height // 2 + randint(-8, 8) + 5 * ((x / 10) % 2)  # 简易锯齿/波形
            wave_points.append((x, y))
        draw.line(wave_points, fill=(randint(80, 180), randint(80, 180), randint(80, 180)), width=1)

    # ---- 添加干扰点 ----
    num_dots = randint(80, 150)  # 随机点数（80-150个）
    for _ in range(num_dots):
        dot_x = randint(0, width - 1)
        dot_y = randint(0, height - 1)
        dot_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        draw.point((dot_x, dot_y), fill=dot_color)

    # 可选：在边缘添加一些随机像素线（增加噪点感）
    for _ in range(30):
        x1 = randint(0, width)
        y1 = randint(0, height)
        x2 = x1 + randint(-2, 2)
        y2 = y1 + randint(-2, 2)
        draw.line((x1, y1, x2, y2), fill=(randint(100, 200), randint(100, 200), randint(100, 200)), width=1)

    # 返回生成的图片对象和验证码字符串
    return img, code

# 示例调用（若直接运行此脚本，会显示并保存图片）
if __name__ == '__main__':
    img, code = creat_image_content()
    img.show()  # 显示图片
    img.save('captcha.png')  # 保存到文件
    print(f"验证码: {code}")  # 打印验证码