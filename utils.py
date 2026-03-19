import ddddocr
import hashlib
import base64
from io import BytesIO
from PIL import Image
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad

def md5_encrypt(text: str) -> str:
    """
    MD5加密
    :param text: 待加密字符串
    :return: 加密后字符串
    """
    md5 = hashlib.md5()
    # 将字符串转换为字节类型并更新到 MD5 对象中
    md5.update(text.encode('utf-8'))
    encrypted_text = md5.hexdigest()
    return encrypted_text


def des_ecb_encrypt(data: bytes, key: bytes) -> str:
    """
    DES ECB加密
    :param data: 待加密字节串
    :param key: 密钥字节串
    :return: 加密后hex编码的字符串
    """
    cipher = DES.new(key, DES.MODE_ECB)
    padded_data = pad(data, DES.block_size)
    encrypted_data = cipher.encrypt(padded_data).hex()
    return encrypted_data


def base64_to_image(base64_str: str) -> bytes:
    """
    将base64字符串转换为图像字节串
    :param base64_str: base64字符串
    :return:
    """
    image_data = base64.b64decode(base64_str.split(',')[1])

    image = Image.open(BytesIO(image_data))
    image = image.convert('L')

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def img_to_code(img: bytes) -> str:
    """
    使用ddddocr识别图片验证码
    :param img:
    :return:
    """
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr.set_ranges(6)
    code = ocr.classification(img)
    return code