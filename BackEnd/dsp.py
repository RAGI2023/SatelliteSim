import binascii

def crc32(data):
    """
    计算数据的 CRC32 校验
    :param data: 输入数据（字符串或字节流）
    :return: CRC32 校验值
    """
    return binascii.crc32(data.encode()) & 0xffffffff  # 使用 binascii 的 crc32 方法

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
    
