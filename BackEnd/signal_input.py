"""
信号采集模块
支持音频、图片、视频的采集
依赖：sounddevice, scipy, opencv-python, matplotlib
     PortAudio
"""

import numpy as np

def record_audio(filename:str = 'default.wav'
                 , duration=5, samplerate=16000, channels=1):
    """
    通过麦克风采集音频并保存为WAV文件。
    :param filename: 保存的文件名
    :param duration: 采集时长（秒）
    :param samplerate: 采样率
    :param channels: 声道数
    :return: 采集到的音频数据（numpy数组）
    """
    import sounddevice as sd
    from scipy.io.wavfile import write

    print(f"开始录音")
    # 使用sd的rec方法进行录制
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
    # 阻塞程序，等待录音完成
    sd.wait()
    write(filename, samplerate, audio)
    print(f"录音完成，已保存为 {filename}")
    return audio

def capture_image(filename:str = "default.jpg"
                  , camera_index=0):
    """
    通过摄像头采集一张图片并保存。
    :param filename: 保存的文件名
    :param camera_index: 摄像头编号（默认0）
    :return: 采集到的图片（numpy数组）
    """
    import cv2

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("无法打开摄像头")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("无法采集图片")
    cv2.imwrite(filename, frame)
    print(f"图片已保存为 {filename}")
    return frame

def record_video(filename:str = "output.avi"
                 , duration=5, camera_index=0, fps=20, resolution=(640, 480)):
    """
    通过摄像头采集视频并保存。
    :param filename: 保存的文件名
    :param duration: 采集时长（秒）
    :param camera_index: 摄像头编号（默认0）
    :param fps: 帧率
    :param resolution: 分辨率 (宽, 高)
    :return: 保存的视频文件路径
    """
    import cv2
    import time

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("无法打开摄像头")
    # 设置视频编码格式
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    out = cv2.VideoWriter(filename, fourcc, fps, resolution)

    print(f"开始录像，时长{duration}秒...")
    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    cap.release()
    out.release()
    print(f"录像完成，已保存为 {filename}")
    return filename

def read_audio_file(filename:str):
    """
    从本地文件读取音频数据
    :param filename: 音频文件路径
    :return: (采样率, 音频数据)
    """
    from scipy.io.wavfile import read
    samplerate, data = read(filename)
    print(f"读取音频文件 {filename}，采样率: {samplerate}, 形状: {data.shape}")
    return samplerate, data

def read_image_file(filename:str):
    """
    从本地文件读取图片数据
    :param filename: 图片文件路径
    :return: 图片数据（numpy数组）
    """
    import cv2
    img = cv2.imread(filename)
    if img is None:
        raise RuntimeError(f"无法读取图片文件 {filename}")
    print(f"读取图片文件 {filename}，形状: {img.shape}")
    return img

def read_video_file(filename:str):
    """
    从本地文件读取视频数据（逐帧返回）
    :param filename: 视频文件路径
    :return: 帧生成器
    """
    import cv2
    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件 {filename}")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

def plot_audio_waveform(audio, samplerate):
    """
    实时显示音频波形
    :param audio: 音频数据（numpy数组）
    :param samplerate: 采样率
    """
    import matplotlib.pyplot as plt
    import numpy as np
    t = np.arange(audio.shape[0]) / samplerate
    plt.figure()
    plt.plot(t, audio)
    plt.title("Audio Waveform")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

def plot_audio_spectrum(audio, samplerate):
    """
    实时显示音频频谱
    :param audio: 音频数据（numpy数组）
    :param samplerate: 采样率
    """
    import matplotlib.pyplot as plt
    from scipy.fft import fft, fftfreq
    N = audio.shape[0]
    yf = fft(audio[:, 0] if audio.ndim > 1 else audio)
    xf = fftfreq(N, 1 / samplerate)
    plt.figure()
    plt.plot(xf[:N // 2], np.abs(yf[:N // 2]))
    plt.title("Audio Spectrum")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Magnitude")
    plt.show()

if __name__ == "__main__":
        # # 采集音频
    audio_data = record_audio(filename="test_audio.wav", duration=3)
        # 采集图片
    image_data = capture_image(filename="test_image.jpg")
        # 采集视频
    video_file = record_video(filename="test_video.avi", duration=5)

# def generate_sine_wave(frequency=440, duration=2, samplerate=16000, amplitude=0.5):
#     """
#     生成正弦波音频信号
#     :param frequency: 频率Hz
#     :param duration: 时长秒
#     :param samplerate: 采样率
#     :param amplitude: 振幅
#     :return: numpy数组
#     """
#     t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
#     audio = amplitude * np.sin(2 * np.pi * frequency * t)
#     print(f"生成正弦波: {frequency}Hz, {duration}s, 采样率{samplerate}")
#     return (audio * 32767).astype(np.int16)

# def record_audio_segmented(filename_prefix="segment", segment_duration=2, total_duration=10, samplerate=16000, channels=1):
#     """
#     分段采集音频并保存为多个WAV文件
#     :param filename_prefix: 文件名前缀
#     :param segment_duration: 每段时长（秒）
#     :param total_duration: 总采集时长（秒）
#     :param samplerate: 采样率
#     :param channels: 声道数
#     :return: 文件名列表
#     """
#     import sounddevice as sd
#     from scipy.io.wavfile import write
#     file_list = []
#     num_segments = int(np.ceil(total_duration / segment_duration))
#     print(f"分段录音，总时长{total_duration}s，每段{segment_duration}s，共{num_segments}段")
#     for i in range(num_segments):
#         print(f"录制第{i+1}段...")
#         audio = sd.rec(int(segment_duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
#         sd.wait()
#         fname = f"{filename_prefix}_{i+1}.wav"
#         write(fname, samplerate, audio)
#         file_list.append(fname)
#     print("分段录音完成")
#     return file_list

# def record_audio_callback(duration=5, samplerate=16000, channels=1, callback=None):
#     """
#     采集音频并通过回调实时处理
#     :param duration: 采集时长（秒）
#     :param samplerate: 采样率
#     :param channels: 声道数
#     :param callback: 回调函数，参数为音频块
#     """
#     import sounddevice as sd
#
#     blocksize = 1024
#     num_blocks = int(duration * samplerate / blocksize)
#     print(f"开始回调录音，时长{duration}s，blocksize={blocksize}")
#     def audio_callback(indata, frames, time, status):
#         if callback:
#             callback(indata.copy())
#     with sd.InputStream(samplerate=samplerate, channels=channels, blocksize=blocksize, callback=audio_callback):
#         sd.sleep(int(duration * 1000))
#     print("回调录音完成")


    # # 读取音频并显示波形和频谱
    # sr, data = read_audio_file("test_audio.wav")
    # plot_audio_waveform(data, sr)
    # plot_audio_spectrum(data, sr)


    # # 生成正弦波并保存
    # sine = generate_sine_wave(frequency=1000, duration=2, samplerate=sr)
    # from scipy.io.wavfile import write
    # write("sine_1k.wav", sr, sine)
    #
    # # 分段采集音频
    # record_audio_segmented(filename_prefix="seg", segment_duration=1, total_duration=3)
    #
    # # 回调采集音频（示例：打印每块最大值）
    # def print_max(audio_block):
    #     print("音频块最大值:", np.max(audio_block))
    # record_audio_callback(duration=2, callback=print_max)
