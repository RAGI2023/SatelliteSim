import math

def a2d(
    analog_value: float,#唯一必选参数
    v_ref: float = 3.3,
    resolution: int = 12,
    bipolar: bool = False,
    noise: float = 0.0
) -> int:
    """
    模拟量转数字量（ADC转换）
    :param analog_value: 输入模拟电压值（单位V）
    :param v_ref: 参考电压（单位V）
    :param resolution: ADC分辨率（位数），如12位
    :param bipolar: 是否为双极性输入（True: -v_ref~+v_ref, False: 0~v_ref）
    :param noise: 添加的高斯噪声标准差（单位V），默认0
    :return: 数字量（int）
    """
    max_digital = (1 << resolution) - 1 #最大分辨率（数字信号能模拟产生的最大值）
    # 添加噪音
    if noise > 0.0:
        import random
        analog_value += random.gauss(0, noise)
    # 双极性输入
    if bipolar:
        analog_value = max(-v_ref, min(analog_value, v_ref))
        digital = int(round(((analog_value + v_ref) / (2 * v_ref)) * max_digital))
    else:
        analog_value = max(0.0, min(analog_value, v_ref))
        digital = int(round((analog_value / v_ref) * max_digital))
    return digital

def d2a(
    digital_value: int,
    v_ref: float = 3.3,
    resolution: int = 12,
    bipolar: bool = False
) -> float:
    """
    数字量转模拟量（DAC转换）
    :param digital_value: 输入数字量
    :param v_ref: 参考电压（单位V）
    :param resolution: DAC分辨率（位数），如12位
    :param bipolar: 是否为双极性输出（True: -v_ref~+v_ref, False: 0~v_ref）
    :return: 输出模拟电压值（单位V）
    """
    max_digital = (1 << resolution) - 1
    digital_value = max(0, min(digital_value, max_digital))
    if bipolar:
        analog = ((digital_value / max_digital) * 2 - 1) * v_ref
    else:
        analog = (digital_value / max_digital) * v_ref
    return analog

def adc_info(resolution: int = 12, v_ref: float = 3.3, bipolar: bool = False) -> dict:
    """
    获取ADC参数信息
    :param resolution: 分辨率
    :param v_ref: 参考电压
    :param bipolar: 是否双极性
    :return: 信息字典
    """
    max_digital = (1 << resolution) - 1
    if bipolar:
        min_v, max_v = -v_ref, v_ref
    else:
        min_v, max_v = 0.0, v_ref
    lsb = (max_v - min_v) / max_digital
    return {
        "resolution": resolution,
        "v_ref": v_ref,
        "bipolar": bipolar,
        "digital_range": (0, max_digital),
        "analog_range": (min_v, max_v),
        "lsb": lsb # 最小有效位：数字量变化一个单位所代表的最小模拟电压变化量
    }

def auto_adc(analog_value: float, **kwargs) -> int:
    """
    自动选择参数的ADC转换（简化接口）
    :param analog_value: 输入模拟电压
    :param kwargs: 其他参数
    :return: 数字量
    """
    return a2d(analog_value, **kwargs)

def auto_dac(digital_value: int, **kwargs) -> float:
    """
    自动选择参数的DAC转换（简化接口）
    :param digital_value: 输入数字量
    :param kwargs: 其他参数
    :return: 模拟电压
    """
    return d2a(digital_value, **kwargs)

def a2d_array(
    analog_values,
    v_ref: float = 3.3,
    resolution: int = 12,
    bipolar: bool = False,
    noise: float = 0.0
):
    """
    批量模拟量转数字量（支持列表、元组、numpy数组）
    :param analog_values: 输入模拟电压序列
    :return: 数字量序列（与输入类型一致）
    """
    try:
        import numpy as np
        arr = np.asarray(analog_values)
        vec_adc = np.vectorize(lambda v: a2d(v, v_ref, resolution, bipolar, noise))
        return vec_adc(arr)
    except ImportError:
        # 不依赖numpy时，支持列表/元组
        return type(analog_values)(a2d(v, v_ref, resolution, bipolar, noise) for v in analog_values)

def d2a_array(
    digital_values,
    v_ref: float = 3.3,
    resolution: int = 12,
    bipolar: bool = False
):
    """
    批量数字量转模拟量（支持列表、元组、numpy数组）
    :param digital_values: 输入数字量序列
    :return: 模拟电压序列（与输入类型一致）
    """
    try:
        import numpy as np
        arr = np.asarray(digital_values)
        vec_dac = np.vectorize(lambda d: d2a(d, v_ref, resolution, bipolar))
        return vec_dac(arr)
    except ImportError:
        return type(digital_values)(d2a(d, v_ref, resolution, bipolar) for d in digital_values)

import time

# ----------------------多写的----------------------------------------
def continuous_sampling(
    analog_source_func,
    duration: float,
    interval: float = 0.01,
    v_ref: float = 3.3,
    resolution: int = 12,
    bipolar: bool = False,
    noise: float = 0.0
):
    """
    连续采样一段时间，将模拟信号转为数字信号
    :param analog_source_func: 返回当前模拟电压的函数
    :param duration: 采样总时长（秒）
    :param interval: 采样间隔（秒）
    :return: 数字量列表
    """
    samples = []
    t0 = time.time()
    while time.time() - t0 < duration:
        analog_value = analog_source_func()
        digital = a2d(analog_value, v_ref, resolution, bipolar, noise)
        samples.append(digital)
        time.sleep(interval)# 好新颖的思路，不用定义时间序列了
    return samples

# 示例
if __name__ == "__main__":
    v = 1.65  # 输入模拟电压
    adc = a2d(v)
    print(f"模拟电压 {v}V 转换为数字量: {adc}")

    dac = d2a(adc)
    print(f"数字量 {adc} 转换回模拟电压: {dac:.4f}V")

    # 双极性、带噪声
    v2 = -1.0
    adc2 = a2d(v2, v_ref=2.5, resolution=16, bipolar=True, noise=0.01)
    print(f"双极性模拟电压 {v2}V 转换为数字量: {adc2}")

    dac2 = d2a(adc2, v_ref=2.5, resolution=16, bipolar=True)
    print(f"数字量 {adc2} 转换回双极性模拟电压: {dac2:.4f}V")

    # 查询ADC参数
    info = adc_info(16, 2.5, bipolar=True)
    print("ADC参数信息:", info)

    # 批量采样测试
    analog_list = [0.1, 0.5, 1.0, 2.0, 3.0]
    digital_list = a2d_array(analog_list)
    print("批量模拟量转数字量:", digital_list)
    recovered_analog = d2a_array(digital_list)
    print("批量数字量转模拟量:", recovered_analog)

    # 连续采样测试
    import math
    def sine_wave_gen(freq=1.0, amp=1.0, offset=1.65):
        start = time.time()
        return lambda: amp * math.sin(2 * math.pi * freq * (time.time() - start)) + offset

    print("开始连续采样（采集正弦波1秒，每0.05秒采样一次）...")
    analog_func = sine_wave_gen(freq=2, amp=1.0, offset=1.65)
    sampled_digits = continuous_sampling(analog_func, duration=1.0, interval=0.05)
    print("连续采样数字量:", sampled_digits)
    print("连续采样还原模拟量:", d2a_array(sampled_digits))
