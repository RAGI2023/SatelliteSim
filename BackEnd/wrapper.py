import time
import struct
import hashlib
import json

# 协议头格式定义
# version(1B), source源地址(16B), dest目的地(16B), 
# timestamp时间戳(8B), data_length数据长度(4B),
# checksum校验和(32B), priority(1B), data_type(1B), seq序列号(4B)
_HEADER_FORMAT = "!B16s16sQI32sBBI"
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)# 计算二进制协议头的总字节数：83字节

# 定义异常类
class ProtocolError(Exception):
    pass

def _checksum(data: bytes, method: str = "sha256") -> bytes:
    """计算校验和，支持sha256和md5"""
    if method == "sha256":
        return hashlib.sha256(data).digest()
    elif method == "md5":
        return hashlib.md5(data).digest().ljust(32, b'\x00')
    else:
        raise ValueError("不支持的校验和算法")


def pack_protocol(
    data: bytes,
    source: str,
    destination: str,
    version: int = 1,
    priority: int = 0,
    data_type: int = 0,
    sequence: int = 0,
    checksum_method: str = "sha256"
) -> bytes:
    """
    封装协议数据包，支持扩展字段和多种校验和算法

    参数:
        data (bytes): 需要封装的数据
        source (str): 源地址（最长16字节）
        destination (str): 目标地址（最长16字节）
        version (int): 协议版本号（默认1）
        priority (int): 优先级（0~255，默认0）
        data_type (int): 数据类型（0~255，默认0），可自定义类型：
        sequence (int): 序列号（默认0）
        checksum_method (str): 校验和算法（"sha256"或"md5"），默认sha256

    返回:
        bytes: 完整协议包
    """
    timestamp = int(time.time())
    data_length = len(data)
    checksum = _checksum(data, checksum_method)
    header = struct.pack(
        _HEADER_FORMAT,
        version,
        source.encode('utf-8')[:16].ljust(16, b'\x00'),
        destination.encode('utf-8')[:16].ljust(16, b'\x00'),
        timestamp,
        data_length,
        checksum,
        priority,
        data_type,
        sequence
    )
    return header + data

def unpack_protocol(
    packet: bytes,
    decode: bool = False,
    checksum_method: str = "sha256"
) -> dict:
    """
    解析协议数据包，支持扩展字段和多种校验和算法

    参数:
        packet (bytes): 完整协议包
        decode (bool): 是否将data字段自动解码为utf-8字符串（默认False）
        checksum_method (str): 校验和算法（"sha256"或"md5"）

    返回:
        dict: 协议头信息及数据内容
        其中 data_type 字段含义参见 pack_protocol 的说明
    """
    if len(packet) < _HEADER_SIZE:
        raise ProtocolError("协议包长度不足")

    header = packet[:_HEADER_SIZE]
    data = packet[_HEADER_SIZE:]

    unpacked = struct.unpack(_HEADER_FORMAT, header)
    version = unpacked[0]
    source = unpacked[1].decode('utf-8').rstrip('\x00')
    destination = unpacked[2].decode('utf-8').rstrip('\x00')# 去除字符串右侧的填充字符 \x00
    timestamp = unpacked[3]
    data_length = unpacked[4]
    checksum = unpacked[5]
    priority = unpacked[6]
    data_type = unpacked[7]
    sequence = unpacked[8]
    if len(data) != data_length:
        raise ProtocolError("数据长度不匹配")
    if _checksum(data, checksum_method) != checksum:
        raise ProtocolError("数据校验和错误")
    result = {
        "version": version,
        "source": source,
        "destination": destination,
        "timestamp": timestamp,
        "data_length": data_length,
        "checksum": checksum.hex(),
        "priority": priority,
        "data_type": data_type,
        "sequence": sequence,
        "data": data.decode('utf-8') if decode else data
    }
    return result

def unpack_protocol_to_json(packet: bytes, checksum_method: str = "sha256") -> str:
    """
    解析协议并返回JSON字符串

    参数:
        packet (bytes): 完整协议包
        checksum_method (str): 校验和算法

    返回:
        str: 协议头及数据内容的JSON字符串
    """
    info = unpack_protocol(packet, decode=True, checksum_method=checksum_method)
    return json.dumps(info, ensure_ascii=False, indent=2)

def extract_header(packet: bytes) -> dict:
    """
    仅提取协议头信息，不校验数据内容

    参数:
        packet (bytes): 完整协议包

    返回:
        dict: 协议头信息
    """
    if len(packet) < _HEADER_SIZE:
        raise ProtocolError("协议包长度不足")

    header = packet[:_HEADER_SIZE]
    unpacked = struct.unpack(_HEADER_FORMAT, header)
    return {
        "version": unpacked[0],
        "source": unpacked[1].decode('utf-8').rstrip('\x00'),
        "destination": unpacked[2].decode('utf-8').rstrip('\x00'),
        "timestamp": unpacked[3],
        "data_length": unpacked[4],
        "checksum": unpacked[5].hex(),
        "priority": unpacked[6],
        "data_type": unpacked[7],
        "sequence": unpacked[8]
    }

def extract_data(packet: bytes) -> bytes:
    """
    仅提取数据部分

    参数:
        packet (bytes): 完整协议包

    返回:
        bytes: 数据内容
    """
    if len(packet) < _HEADER_SIZE:
        raise ProtocolError("协议包长度不足")
    return packet[_HEADER_SIZE:]

if __name__ == "__main__":
    # 待发送的数据
    data = "卫星遥测数据".encode("utf-8")
    source = "TerminalA"
    destination = "TerminalB"

    # 封装协议包
    packet = pack_protocol(
        data,
        source,
        destination,
        # version=1,
        # priority=5,
        # data_type=2,
        # sequence=1001,
        # checksum_method="sha256"
    )

    # 2. 解析数据包（终端B）
    try:
        info = unpack_protocol(packet, decode=True)
        print("协议头及数据内容：")
        print(info)
    except ProtocolError as e:
        print("协议解析失败：", e)

    # 5. 以JSON格式输出解析结果
    json_str = unpack_protocol_to_json(packet)
    print("JSON格式输出：\n", json_str)

    # 3. 仅提取协议头
    header = extract_header(packet)
    print("协议头信息：", header)

    # 4. 仅提取数据部分
    data_bytes = extract_data(packet)
    print("原始数据内容：", data_bytes.decode("utf-8"))


# API使用说明
"""
API接口说明：

1. pack_protocol(data, source, destination, version=1, priority=0, data_type=0, sequence=0, checksum_method="sha256")
   - 功能：封装数据为协议包，支持优先级、数据类型、序列号、校验和算法选择。
   - data_type: int，数据类型，可选值及含义：

2. unpack_protocol(packet, decode=False, checksum_method="sha256")
   - 功能：解析协议包，返回协议头和数据内容，支持校验和算法选择。
   - 返回：dict，包含所有字段，data_type 字段含义同上

3. extract_header(packet)
   - 功能：仅提取协议头信息，不校验数据内容。
   - ���回：dict

4. extract_data(packet)
   - 功能：仅提取数据部分。
   - 返回：bytes

5. unpack_protocol_to_json(packet, checksum_method="sha256")
   - 功能：解析协议包并返回JSON字符串，便于接口或日志输出。
   - 返回：str

异常：
- ProtocolError：协议格式或校验错误时抛出

示例：
>>> pkt = pack_protocol(b'hello', 'A', 'B', priority=2, data_type=1, sequence=123)
>>> info = unpack_protocol(pkt, decode=True)
>>> print(info)
>>> print(unpack_protocol_to_json(pkt))
"""


"""
使用说明：

本模块提供协议数据包的封装与解析，支持协议头自动添加源地址、目标地址、时间戳、优先级、数据类型、序列号、校验和等信息。
适用于终端A（封装）与终端B（解析）之间的数据通信。

主要API：
- pack_protocol(data, source, destination, ...)
    封装数据为协议包（bytes），自动添加协议头。
- unpack_protocol(packet, decode=False, ...)
    解析协议包，返回协议头和数据内容（dict）。
- extract_header(packet)
    仅提取协议头信息（dict）。
- extract_data(packet)
    仅提取数据部分（bytes）。
- unpack_protocol_to_json(packet, ...)
    解析协议包并返回JSON字符串，便于接口或日志输出。

异常：
- ProtocolError：协议格式或校验错误时抛出
"""