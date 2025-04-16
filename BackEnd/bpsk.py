import numpy as np
import matplotlib.pyplot as plt
#bit_seq:比特序列   carrier_freq:载波频率   sample_rate:采样频率    symbol_duration:时间周期
def bpsk_modulate(bit_seq, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    t = np.arange(0, symbol_duration, 1/sample_rate)#一段时间序列
    modulated_signal = []

    for bit in bit_seq:
        phase = 0 if bit == 1 else np.pi  # 1 -> 0 rad, 0 -> pi rad
        signal = np.cos(2 * np.pi * carrier_freq * t + phase)
        modulated_signal.extend(signal)

    x = np.linspace(0, len(modulated_signal) * 1 / sample_rate, len(modulated_signal))
    y = modulated_signal
    data = list(zip(x,y))
    return np.array(data,dtype=np.float64)

def bpsk_demodulate(received_signal, carrier_freq=1000, sample_rate=10000, symbol_duration=0.01):
    samples_per_symbol = int(sample_rate * symbol_duration)
    num_symbols = len(received_signal) // samples_per_symbol
    bit_seq = []

    # 生成本地载波（用于相干解调）
    t = np.arange(0, symbol_duration, 1/sample_rate)
    carrier = np.cos(2 * np.pi * carrier_freq * t)

    for i in range(num_symbols):
        start = i * samples_per_symbol
        end = start + samples_per_symbol
        segment = received_signal[start:end]

        # 相干解调：将接收信号与本地产生的载波相乘并积分（这里使用累加）
        product = segment * carrier
        metric = np.sum(product)

        # 判决：metric > 0 判为 1，否则判为 0
        bit = 1 if metric > 0 else 0
        bit_seq.append(bit)

    return bit_seq

if __name__ == "__main__":
    bits = [0, 1, 1, 0, 1]  # 示例比特流
    result = bpsk_modulate(bits, carrier_freq=1000, sample_rate=10000)

    print("调制信号的形状", result.shape)
    print("部分调试信号展示:\n", result[:10])

    # 解调
    received = result[:, 1]  # 提取调制后的 y 值
    demodulated_bits = bpsk_demodulate(received, carrier_freq=1000, sample_rate=10000)

    print("原始数据：", bits)
    print("调制后的数据：", demodulated_bits)