#四个码源，比bpsk更快，但是不如bpsk稳定
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

    return np.array(modulated_signal)
