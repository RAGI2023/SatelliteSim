import numpy as np
from BackEnd.signal_input import capture_image

def qpsk_modulate(bit_seq, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    # 确保比特序列长度为偶数
    bit_seq = np.asarray(bit_seq)
    if bit_seq.size % 2 != 0:
        bit_seq = np.append(bit_seq, 0)
    num_symbols = bit_seq.size // 2

    t = np.arange(0, symbol_duration, 1 / sample_rate)
    samples_per_symbol = t.size

    # Gray编码QPSK相位映射
    mapping = np.array([
        np.pi / 4,    # 00
        3 * np.pi / 4, # 01
        5 * np.pi / 4, # 11
        7 * np.pi / 4  # 10
    ])
    # 计算每对比特的索引
    idx = (bit_seq[0::2] << 1) | bit_seq[1::2]
    phases = mapping[idx]

    # 生成所有符号的调制信号
    carrier = 2 * np.pi * carrier_freq * t
    signals = np.cos(carrier[None, :] + phases[:, None])
    modulated_signal = signals.reshape(-1)
    return modulated_signal

def qpsk_demodulate(signal, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    # signal为一维ndarray
    t = np.arange(0, symbol_duration, 1 / sample_rate)
    samples_per_symbol = t.size
    num_symbols = signal.size // samples_per_symbol
    signal = signal[:num_symbols * samples_per_symbol].reshape(num_symbols, samples_per_symbol)

    # 生成正交载波
    cosine = np.cos(2 * np.pi * carrier_freq * t)
    sine = np.sin(2 * np.pi * carrier_freq * t)

    I = np.dot(signal, cosine)
    Q = np.dot(signal, sine)

    # 最大似然判决
    phases = np.arctan2(Q, I)
    phases = (phases + 2 * np.pi) % (2 * np.pi)
    ref_phases = np.array([np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4])
    diff = np.abs(phases[:, None] - ref_phases[None, :])
    symbol_indices = np.argmin(diff, axis=1)

    # Gray编码反映射
    bits = np.zeros((num_symbols, 2), dtype=np.uint8)
    bits[symbol_indices == 0] = [0, 0]
    bits[symbol_indices == 1] = [0, 1]
    bits[symbol_indices == 2] = [1, 1]
    bits[symbol_indices == 3] = [1, 0]
    return bits.reshape(-1)

if __name__ == "__main__":
    import cv2
    frame = capture_image('test_image.jpg')  # (480, 640, 3)
    frame_resized = cv2.resize(frame, (640, 480))
    height, width, channels = frame_resized.shape

    bit_seq = np.unpackbits(frame_resized.astype(np.uint8).flatten())
    modulated = qpsk_modulate(bit_seq)
    print('调制成功')
    print('调制信号长度:', len(modulated))
    # =======================做了算法优化：向量化处理===================================
    # 解调
    demodulated_bits = qpsk_demodulate(modulated, carrier_freq=1000, sample_rate=10000)
    demodulated_bits = demodulated_bits[:height * width * channels * 8]  # 截断多余比特
    byte_data = np.packbits(demodulated_bits)

    # 检查数据大小
    expected_size = height * width * channels
    if byte_data.size < expected_size:
        byte_data = np.pad(byte_data, (0, expected_size - byte_data.size), mode='constant')
    elif byte_data.size > expected_size:
        byte_data = byte_data[:expected_size]

    restored_image = byte_data.reshape((height, width, channels))
    cv2.imwrite("restored_image.jpg", restored_image)
    print("图片已还原并保存为 restored_image.jpg")
