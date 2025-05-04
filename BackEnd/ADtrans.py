import numpy as np
from pydub import AudioSegment

def extract_audio_segment(mp3_path, start_ms=0, duration_ms=1000, target_sample_rate=8000):
    """
    从MP3文件中截取一段音频，重采样后转换为数字样本（模拟AD过程）

    :param mp3_path: MP3文件路径
    :param start_ms: 起始时间（毫秒）
    :param duration_ms: 持续时间（毫秒）
    :param target_sample_rate: 要重采样为的采样率（Hz）
    :return: (样本数组, 实际采样率)
    """
    # 加载音频（原始采样率可能是 44100）
    audio = AudioSegment.from_mp3(mp3_path)

    # 重采样（修改为目标采样率，例如 16000 Hz）
    audio = audio.set_frame_rate(target_sample_rate)

    # 截取指定时间段
    segment = audio[start_ms:start_ms + duration_ms]

    # 转为数组
    samples = segment.get_array_of_samples()
    arr = np.array(samples).astype(np.float32)

    # 合并双声道为单声道
    if segment.channels == 2:
        arr = arr.reshape((-1, 2)).mean(axis=1)

    return arr, segment.frame_rate