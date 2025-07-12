import base64
import io
from PIL import Image


def base64_to_image(base64_string, output_path=None):
    """
    将Base64编码的图片字符串转换为图片

    参数:
        base64_string: Base64编码的图片字符串，可以是纯Base64编码或data URL格式
        output_path: 输出图片的路径，如果为None则不保存图片

    返回:
        PIL.Image对象
    """
    # 检查字符串是否是data URL格式
    if base64_string.startswith("data:"):
        # 提取Base64编码部分
        header, base64_data = base64_string.split(",", 1)
    else:
        base64_data = base64_string

    # 解码Base64数据
    image_data = base64.b64decode(base64_data)

    # 将解码后的数据转换为图片
    image = Image.open(io.BytesIO(image_data))

    # 如果指定了输出路径，则保存图片
    if output_path:
        image.save(output_path)
        print(f"图片已保存为 {output_path}")

    return image
