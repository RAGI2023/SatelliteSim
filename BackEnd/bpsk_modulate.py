import numpy as np
#bit_seq:比特序列   carrier_freq:载波频率   sample_rate:采样频率    symbol_duration:时间周期
def bpsk_modulate(bit_seq, carrier_freq=100, sample_rate=1000, symbol_duration=0.01):
    t = np.arange(0, symbol_duration, 1/sample_rate)#一段时间序列
    modulated_signal = []

    for bit in bit_seq:
        phase = 0 if bit == 1 else np.pi  # 1 -> 0 rad, 0 -> pi rad
        signal = np.cos(2 * np.pi * carrier_freq * t + phase)
        modulated_signal.extend(signal)

    return np.array(modulated_signal)

if __name__ == "__main__":
    # 模拟前端请求中的比特流
    bitstream = np.random.randint(0, 2, 16)  # 16位比特
    print("原始比特流:", bitstream)

    # BPSK 调制
    bpsk_signal = bpsk_modulate(bitstream)
    print("BPSK 信号生成完毕，长度:", len(bpsk_signal))
    print("BPSK 信号数据类型:", bpsk_signal.dtype)
    for i in range(16):
        print(bpsk_signal[i],sep=' ')
