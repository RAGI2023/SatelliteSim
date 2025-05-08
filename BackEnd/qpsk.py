import numpy as np
from signal_input import capture_image

def qpsk_modulate(bit_seq, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    # 确保比特序列长度为偶数
    if len(bit_seq) % 2 != 0:
        bit_seq = np.append(bit_seq, 0)

    t = np.arange(0, symbol_duration, 1/sample_rate)
    modulated_signal = []

    # QPSK映射表
    mapping = {
        (0, 0): np.pi/4,
        (0, 1): 3*np.pi/4,
        (1, 1): 5*np.pi/4,
        (1, 0): 7*np.pi/4
    }

    for i in range(0, len(bit_seq), 2):
        bits = (bit_seq[i], bit_seq[i+1])
        phase = mapping[bits]
        signal = np.cos(2 * np.pi * carrier_freq * t + phase)
        modulated_signal.extend(signal)

    # 优化数据拼接方式
    x = np.linspace(0, len(modulated_signal) / sample_rate, len(modulated_signal))
    y = np.array(modulated_signal)
    data = f"{','.join(map(str, x))}|{','.join(map(str, y))}"

    return data

def qpsk_demodulate(data_str, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    # 解析字符串格式的数据
    x_str, y_str = data_str.split('|')
    y = np.array(list(map(float, y_str.split(','))))

    t = np.arange(0, symbol_duration, 1/sample_rate)
    samples_per_symbol = len(t)
    num_symbols = len(y) // samples_per_symbol

    bit_seq = []

    for i in range(num_symbols):
        start = i * samples_per_symbol
        end = start + samples_per_symbol
        segment = y[start:end]

        # 同步的正交载波
        cosine = np.cos(2 * np.pi * carrier_freq * t)
        sine = np.sin(2 * np.pi * carrier_freq * t)

        I = np.sum(segment * cosine)
        Q = np.sum(segment * sine)

        # 判决四个象限
        if I > 0 and Q > 0:
            bits = (0, 0)
        elif I < 0 and Q > 0:
            bits = (0, 1)
        elif I < 0 and Q < 0:
            bits = (1, 1)
        else:
            bits = (1, 0)

        bit_seq.extend(bits)

    return bit_seq

if __name__ == "__main__":
    frame = capture_image('test_image.jpg')  # 获取图片帧，形状为 (480, 640, 3)
    import cv2
    frame_resized = cv2.resize(frame, (32, 24))  # 将图片缩小到 32x24
    height, width, channels = 32, 24, 3  # 根据压缩后的图片形状

    bit_seq = np.unpackbits(frame_resized.astype(np.uint8).flatten())  # 转换为比特序列
    modulated = qpsk_modulate(bit_seq)  # 进行QPSK调制
    print('调制成功')  # 打印调制结果
    print(len(modulated))  # 打印调制后的数据

    # 解调数据
    demodulated_bits = qpsk_demodulate(modulated, carrier_freq=1000, sample_rate=10000)

    # 将比特序列打包为字节
    byte_data = np.packbits(demodulated_bits)

    # 检查数据大小是否匹配目标形状
    expected_size = height * width * channels
    if len(byte_data) < expected_size:
        # 如果数据不足，填充0
        byte_data = np.pad(byte_data, (0, expected_size - len(byte_data)), mode='constant')
    elif len(byte_data) > expected_size:
        # 如果数据过多，截断多余部分
        byte_data = byte_data[:expected_size]

    # 将字节数据转换为图片
    restored_image = np.frombuffer(byte_data, dtype=np.uint8).reshape((height, width, channels))

    # 保存还原的图片
    cv2.imwrite("restored_image.jpg", restored_image)
    print("图片已还原并保存为 restored_image.jpg")
    frame = capture_image('test_image.jpg')  # 获取图片帧，形状为 (480, 640, 3)
    import cv2
    frame_resized = cv2.resize(frame, (32, 24))  # 将图片缩小到 32x24
    height, width, channels = 32, 24, 3  # 根据压缩后的图片形状

    bit_seq = np.unpackbits(frame_resized.astype(np.uint8).flatten())  # 转换为比特序列
    modulated = qpsk_modulate(bit_seq)  # 进行QPSK调制
    print('调制成功')  # 打印调制结果
    print(len(modulated))  # 打印调制后的数据

    # 解调数据
    demodulated_bits = qpsk_demodulate(modulated, carrier_freq=1000, sample_rate=10000)

    # 将比特序列打包为字节
    byte_data = np.packbits(demodulated_bits)

    # 检查数据大小是否匹配目标形状
    expected_size = height * width * channels
    if len(byte_data) < expected_size:
        # 如果数据不足，填充0
        byte_data = np.pad(byte_data, (0, expected_size - len(byte_data)), mode='constant')
    elif len(byte_data) > expected_size:
        # 如果数据过多，截断多余部分
        byte_data = byte_data[:expected_size]

    # 将字节数据转换为图片
    restored_image = np.frombuffer(byte_data, dtype=np.uint8).reshape((height, width, channels))

    # 保存还原的图片
    cv2.imwrite("restored_image.jpg", restored_image)
    print("图片已还原并保存为 restored_image.jpg")
