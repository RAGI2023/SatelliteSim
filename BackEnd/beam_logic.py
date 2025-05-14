# BackEnd/beam_logic.py
import random
import numpy as np
from typing import List, Tuple

class BeamDataManager:
    @staticmethod
    def generate_realistic_users(num_users: int) -> List[Tuple[float, float]]:
        """生成基于中国主要城市人口分布的用户位置"""
        # 定义主要城市中心（纬度, 经度）及权重（模拟人口密度）
        city_centers = [
            (31.23, 121.47, 0.3),   # 上海（长三角核心，权重30%）
            (39.90, 116.40, 0.25),  # 北京（京津冀核心，25%）
            (23.13, 113.26, 0.2),   # 广州（珠三角核心，20%）
            (30.57, 104.07, 0.15),  # 成都（成渝经济圈，15%）
            (22.54, 114.05, 0.1)    # 深圳（粤港澳大湾区，10%）
        ]
        
        users = []
        for _ in range(num_users):
            # 按权重随机选择城市
            city = random.choices(city_centers, weights=[c[2] for c in city_centers])[0]
            lat_center, lon_center, _ = city
            
            # 高斯分布生成用户位置（模拟城市内人口聚集）
            lat = np.random.normal(lat_center, 0.3)  # 纬度标准差0.3°（约33km）
            lon = np.random.normal(lon_center, 0.4)  # 经度标准差0.4°（约44km）
            users.append((round(lat, 6), round(lon, 6)))
        return users

    @staticmethod
    def get_optimized_beam_centers() -> List[Tuple[float, float]]:
        base_centers = [
            (31.23, 121.47),   # 上海
            (39.90, 116.40),   # 北京
            (23.13, 113.26),   # 广州
            (30.57, 104.07),   # 成都
            (22.54, 114.05),   # 深圳
            (36.07, 120.33),   # 青岛
            (28.12, 112.59),   # 长沙
            # 太偏了改一改
            # (31.23, 121.47),  # 上海
            # (39.90, 116.40),  # 北京
            # (23.13, 113.26),  # 广州
            (34.27, 108.95),   # 西安
            (43.82, 87.62),    # 乌鲁木齐
            (25.04, 102.71)    # 昆明
        ]
        # 为每个中心添加±0.1°随机偏移（约10km）
        randomized_centers = []
        for (lat, lon) in base_centers:
            lat += random.uniform(-0.1, 0.1)
            lon += random.uniform(-0.1, 0.1)
            randomized_centers.append((round(lat, 6), round(lon, 6)))
        return randomized_centers