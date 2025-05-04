import binascii
import numpy as np

def crc32(data):
    """
    支持 str、bytes、numpy.ndarray 的通用 CRC32 校验函数
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, np.ndarray):
        data = data.tobytes()
    elif not isinstance(data, bytes):
        raise TypeError(f"Unsupported data type: {type(data)}. Must be str, bytes, or numpy.ndarray.")
    
    return binascii.crc32(data) & 0xffffffff

def parity_check(data, check_type="even"):
    """
    对数据进行奇偶校验
    :param data: 二进制数据列表，例如 [1, 0, 1, 1]
    :param check_type: "even" 或 "odd"，偶校验或奇校验
    :return: 校验位
    """
    # 计算数据中 1 的个数
    ones_count = sum(data)
    
    if check_type == "even":
        # 偶校验：总数应该是偶数
        return 0 if ones_count % 2 == 0 else 1
    elif check_type == "odd":
        # 奇校验：总数应该是奇数
        return 1 if ones_count % 2 == 0 else 0
    else:
        raise ValueError("校验类型应为 'even' 或 'odd'")
    
def parity_check_auto(data, check_type="even"):
    if isinstance(data, str):
        bitlist = [int(b) for c in data.encode('utf-8') for b in format(c, '08b')]
    elif isinstance(data, (bytes, bytearray)):
        bitlist = [int(b) for byte in data for b in format(byte, '08b')]
    elif isinstance(data, np.ndarray):
        bitlist = [int(b) for byte in data.tobytes() for b in format(byte, '08b')]
    elif isinstance(data, list) and all(x in (0, 1) for x in data):
        bitlist = data
    else:
        raise TypeError("Unsupported data type for parity check")

    return parity_check(bitlist, check_type)