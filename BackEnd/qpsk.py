import numpy as np

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

    x = np.linspace(0, len(modulated_signal) * 1 / sample_rate, len(modulated_signal))
    y = modulated_signal
    # 将列表转换为字符串形式再进行拼接
    x_str = ','.join(map(str, x.tolist()))
    y_str = ','.join(map(str, y))
    data = x_str + '|' + y_str

    return np.array(data)

def qpsk_demodulate(data_str, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    # 解析字符串格式的数据
    x_str, y_str = data_str.split('|')
    y = np.array(list(map(float, y_str.split(','))))

    t = np.arange(0, symbol_duration, 1/sample_rate)
    samples_per_symbol = len(t)
    num_symbols = len(y) // samples_per_symbol

    # 构造本地载波
    bit_seq = []

    for i in range(num_symbols):
        start = i * samples_per_symbol
        end = start + samples_per_symbol
        segment = y[start:end]

        # 同步的正交载波
        cosine = np.cos(2 * np.pi * carrier_freq * t)
        sine   = np.sin(2 * np.pi * carrier_freq * t)

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
    bits = [0, 0, 1, 0, 1, 1, 0, 1]
    modulated = qpsk_modulate(bits, carrier_freq=1000, sample_rate=10000)
    print("QPSK调制结果（字符串部分）:", modulated[:100], "...")

    demodulated = qpsk_demodulate(modulated, carrier_freq=1000, sample_rate=10000)
    print("原始比特序列:", bits)
    print("解调比特序列:", demodulated)
