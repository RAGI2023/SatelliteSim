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

    return np.array(modulated_signal)