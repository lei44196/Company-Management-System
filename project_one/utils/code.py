from PIL import Image, ImageFont, ImageDraw
from random import choice, randint
import string


def creat_image_content():
    """生成验证码图片
    
    Returns:
        tuple: (Image对象, 验证码字符串)
    """
    width, height = 110, 40
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')

    try:
        font = ImageFont.truetype('arial.ttf', size=28)
    except IOError:
        font = ImageFont.load_default()

    chars = string.ascii_uppercase + string.digits
    code = ''.join(choice(chars) for _ in range(4))

    x_start = 10
    for i, char in enumerate(code):
        color = (randint(0, 100), randint(0, 100), randint(0, 100))
        y_offset = randint(-3, 3)
        draw.text((x_start + i * 25, 5 + y_offset), char, fill=color, font=font)

    for _ in range(3):
        start = (randint(0, width // 3), randint(0, height))
        end = (randint(width * 2 // 3, width), randint(0, height))
        ctrl1 = (randint(0, width), randint(0, height))
        curve_color = (randint(100, 200), randint(100, 200), randint(100, 200))
        points = []
        for t in range(0, 101, 5):
            t /= 100.0
            x = (1-t)**2 * start[0] + 2*(1-t)*t * ctrl1[0] + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * ctrl1[1] + t**2 * end[1]
            points.append((x, y))
        draw.line(points, fill=curve_color, width=1)

        wave_points = []
        for x in range(0, width, 5):
            y = height // 2 + randint(-8, 8) + 5 * ((x / 10) % 2)
            wave_points.append((x, y))
        draw.line(wave_points, fill=(randint(80, 180), randint(80, 180), randint(80, 180)), width=1)

    num_dots = randint(80, 150)
    for _ in range(num_dots):
        dot_x = randint(0, width - 1)
        dot_y = randint(0, height - 1)
        dot_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        draw.point((dot_x, dot_y), fill=dot_color)

    for _ in range(30):
        x1 = randint(0, width)
        y1 = randint(0, height)
        x2 = x1 + randint(-2, 2)
        y2 = y1 + randint(-2, 2)
        draw.line((x1, y1, x2, y2), fill=(randint(100, 200), randint(100, 200), randint(100, 200)), width=1)

    return img, code


if __name__ == '__main__':
    img, code = creat_image_content()
    img.show()
    img.save('captcha.png')
    print(f"验证码: {code}")