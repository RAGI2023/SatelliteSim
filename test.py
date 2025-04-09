import numpy as np

def bpsk_modulate(bit_seq, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    t = np.arange(0, symbol_duration, 1/sample_rate)
    modulated_signal = []

    for bit in bit_seq:
        phase = 0 if bit == 1 else np.pi  # 1 -> 0 rad, 0 -> pi rad
        signal = np.cos(2 * np.pi * carrier_freq * t + phase)
        modulated_signal.extend(signal)

    return np.array(modulated_signal)

def qpsk_modulate(bit_seq, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    # Ensure bit_seq has even length
    if len(bit_seq) % 2 != 0:
        bit_seq = np.append(bit_seq, 0)

    t = np.arange(0, symbol_duration, 1/sample_rate)
    modulated_signal = []

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

    return np.array(modulated_signal)

# 示例调用
if __name__ == "__main__":
    # 模拟前端请求中的比特流
    bitstream = np.random.randint(0, 2, 16)  # 16位比特
    print("原始比特流:", bitstream)

    # BPSK 调制
    bpsk_signal = bpsk_modulate(bitstream)
    print("BPSK 信号生成完毕，长度:", len(bpsk_signal))
    print(type(bpsk_signal))
    # QPSK 调制
    qpsk_signal = qpsk_modulate(bitstream)
    print("QPSK 信号生成完毕，长度:", len(qpsk_signal))
