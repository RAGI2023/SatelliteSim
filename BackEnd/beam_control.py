import numpy as np
import random
from typing import List, Dict, Tuple, Optional

# ===================== 波束信息 =====================
class Beam:
    def __init__(self, beam_id: int, center: Tuple[float, float], radius: float, max_users: int, freq: float,
                 azimuth: float = 0.0, beamwidth: float = 60.0):
        self.beam_id = beam_id
        self.center = center
        self.radius = radius
        self.max_users = max_users
        self.freq = freq
        self.users = set()
        self.power = 1.0
        self.azimuth = azimuth % 360
        self.beamwidth = max(0, min(beamwidth, 360))
        self.active = True

    def is_within(self, user_pos: Tuple[float, float]) -> bool:
        if not self.active:
            return False
        lat1, lon1 = np.radians(self.center)
        lat2, lon2 = np.radians(user_pos)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        earth_radius = 6371
        distance = earth_radius * c
        if distance > self.radius:
            return False

        y = np.sin(np.radians(user_pos[1] - self.center[1])) * np.cos(np.radians(user_pos[0]))
        x = np.cos(np.radians(self.center[0])) * np.sin(np.radians(user_pos[0])) - \
            np.sin(np.radians(self.center[0])) * np.cos(np.radians(user_pos[0])) * \
            np.cos(np.radians(user_pos[1] - self.center[1]))
        user_azimuth = np.degrees(np.arctan2(y, x)) % 360

        lower = self.azimuth - self.beamwidth / 2
        upper = self.azimuth + self.beamwidth / 2
        if lower < 0:
            return user_azimuth >= (lower + 360) or user_azimuth <= upper
        elif upper > 360:
            return user_azimuth >= lower or user_azimuth <= (upper - 360)
        else:
            return lower <= user_azimuth <= upper

    def set_azimuth(self, azimuth: float):
        self.azimuth = azimuth % 360

    def set_beamwidth(self, beamwidth: float):
        self.beamwidth = max(0, min(beamwidth, 360))

    def set_active(self, active: bool):
        self.active = active

    def can_accept(self):
        return len(self.users) < self.max_users

    def add_user(self, user_id):
        if self.can_accept():
            self.users.add(user_id)
            return True
        return False

    def remove_user(self, user_id):
        self.users.discard(user_id)

    def set_power(self, power: float):
        self.power = power

    def set_center(self, center: Tuple[float, float]):
        self.center = center


class User:
    def __init__(self, user_id: int, pos: Tuple[float, float]):
        self.user_id = user_id
        self.pos = pos
        self.connected_beam: Optional[int] = None


class BeamControlSystem:
    def __init__(self, n_beams: int, beam_radius: float, max_users_per_beam: int,
                 freq_list: List[float], initial_centers: Optional[List[Tuple[float, float]]] = None):
        self.beams: Dict[int, Beam] = {}
        self.users: Dict[int, User] = {}
        self.time = 0

        centers = initial_centers if initial_centers else [
            (random.uniform(-60, 60), random.uniform(-180, 180))
            for _ in range(n_beams // 6)
        ]

        for site_idx, site_center in enumerate(centers):
            for beam_in_site in range(6):
                beam_id = site_idx * 6 + beam_in_site
                freq = freq_list[beam_id % len(freq_list)]
                azimuth = beam_in_site * 60
                self.beams[beam_id] = Beam(
                    beam_id, site_center, beam_radius, max_users_per_beam,
                    freq, azimuth, 60.0
                )

    def assign_users_to_beams(self):
        for beam in self.beams.values():
            beam.users.clear()
        for user in self.users.values():
            candidates = [b for b in self.beams.values() if b.active and b.is_within(user.pos) and b.can_accept()]
            if candidates:
                best = min(candidates, key=lambda b: (len(b.users), -b.power))
                best.add_user(user.user_id)
                user.connected_beam = best.beam_id
            else:
                user.connected_beam = None

    def add_user(self, user_id: int, pos: Tuple[float, float]):
        self.users[user_id] = User(user_id, pos)

    def remove_user(self, user_id: int):
        if user_id in self.users:
            beam_id = self.users[user_id].connected_beam
            if beam_id is not None and beam_id in self.beams:
                self.beams[beam_id].remove_user(user_id)
            del self.users[user_id]

    def set_beam_power(self, beam_id: int, power: float):
        if beam_id in self.beams:
            self.beams[beam_id].set_power(power)
            self.assign_users_to_beams()

    def set_beam_center(self, beam_id: int, center: Tuple[float, float]):
        if beam_id in self.beams:
            self.beams[beam_id].set_center(center)

    def set_beam_azimuth(self, beam_id: int, azimuth: float):
        if beam_id in self.beams:
            self.beams[beam_id].set_azimuth(azimuth)
            self.assign_users_to_beams()

    def set_beam_beamwidth(self, beam_id: int, beamwidth: float):
        if beam_id in self.beams:
            self.beams[beam_id].set_beamwidth(beamwidth)
            self.assign_users_to_beams()

    def set_beam_active(self, beam_id: int, active: bool):
        if beam_id in self.beams:
            self.beams[beam_id].set_active(active)
            self.assign_users_to_beams()

    def frequency_reuse(self):
        conflicts = []
        freq_map: Dict[float, List[Beam]] = {}
        for b in self.beams.values():
            if b.active:
                freq_map.setdefault(b.freq, []).append(b)

        for freq, beams in freq_map.items():
            for i in range(len(beams)):
                for j in range(i + 1, len(beams)):
                    bi, bj = beams[i], beams[j]
                    if self._distance(bi.center, bj.center) < bi.radius + bj.radius and \
                            self._azimuth_overlap(bi.azimuth, bi.beamwidth, bj.azimuth, bj.beamwidth):
                        conflicts.append((bi.beam_id, bj.beam_id, freq, round(self._distance(bi.center, bj.center), 2)))
        return conflicts

    def _azimuth_overlap(self, az1, bw1, az2, bw2):
        def range_overlap(l1, u1, l2, u2):
            l1 %= 360
            u1 %= 360
            l2 %= 360
            u2 %= 360
            if l1 > u1:
                u1 += 360
            if l2 > u2:
                u2 += 360
            return max(l1, l2) <= min(u1, u2)

        return range_overlap(az1 - bw1/2, az1 + bw1/2, az2 - bw2/2, az2 + bw2/2)

    def _distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        lat1, lon1 = np.radians(pos1)
        lat2, lon2 = np.radians(pos2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return 6371 * c

    def auto_power_control(self):
        max_users = max((len(b.users) for b in self.beams.values()), default=1)
        for b in self.beams.values():
            b.set_power(1.0 + 2.0 * len(b.users) / max_users if max_users else 1.0)

    def get_beam_status(self):
        return [
            {
                "beam_id": b.beam_id,
                "center": b.center,
                "radius": b.radius,
                "freq": b.freq,
                "power": b.power,
                "user_count": len(b.users),
                "users": list(b.users),
                "azimuth": b.azimuth,
                "beamwidth": b.beamwidth,
                "active": b.active
            } for b in self.beams.values()
        ]

    def get_user_status(self):
        return [
            {
                "user_id": u.user_id,
                "pos": u.pos,
                "connected_beam": u.connected_beam
            } for u in self.users.values()
        ]

    def simulate_step(self, user_move_func=None):
        if user_move_func:
            for user in self.users.values():
                user.pos = user_move_func(user.pos)
        self.assign_users_to_beams()
        self.time += 1

# import numpy as np
# import random
# from typing import List, Dict, Tuple, Optional
#
# # ===================== 波束信息 =====================
# class Beam:
#     def __init__(self, beam_id: int, center: Tuple[float, float], radius: float, max_users: int, freq: float,
#                  azimuth: float = 0.0, beamwidth: float = 60.0):  # 新增方向参数
#         self.beam_id = beam_id
#         self.center = center  # (纬度, 经度)
#         self.radius = radius  # 覆盖半径（km）
#         self.max_users = max_users
#         self.freq = freq
#         self.users = set()
#         self.power = 1.0
#         self.azimuth = azimuth  # 方位角（0-360度，正北为0，顺时针增加）
#         self.beamwidth = beamwidth  # 波束宽度（覆盖角度，如60度）
#         self.active = True  # 新增：波束是否开启
#
#     def is_within(self, user_pos: Tuple[float, float]) -> bool:
#         if not self.active:
#             return False
#         # 1. 计算用户到波束中心的距离（原有逻辑）
#         lat1, lon1 = np.radians(self.center)
#         lat2, lon2 = np.radians(user_pos)
#         dlat = lat2 - lat1
#         dlon = lon2 - lon1
#         a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
#         c = 2 * np.arcsin(np.sqrt(a))
#         earth_radius = 6371  # km
#         distance = earth_radius * c
#         if distance > self.radius:
#             return False
#
#         # 2. 计算用户相对于波束中心的方位角（新增逻辑）
#         # 公式来源：https://www.movable-type.co.uk/scripts/latlong.html
#         dlon_rad = np.radians(lon2 - lon1)
#         y = np.sin(dlon_rad) * np.cos(np.radians(lat2))
#         x = np.cos(np.radians(lat1)) * np.sin(np.radians(lat2)) - np.sin(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(dlon_rad)
#         user_azimuth = np.degrees(np.arctan2(y, x)) % 360  # 转换为0-360度
#
#         # 3. 判断用户是否在波束的方向范围内（azimuth ± beamwidth/2）
#         lower = self.azimuth - self.beamwidth / 2
#         upper = self.azimuth + self.beamwidth / 2
#         if lower < 0:
#             return user_azimuth >= lower + 360 or user_azimuth <= upper
#         elif upper > 360:
#             return user_azimuth >= lower or user_azimuth <= upper - 360
#         else:
#             return lower <= user_azimuth <= upper
#
#     def set_azimuth(self, azimuth: float):
#         """设置波束方位角"""
#         self.azimuth = azimuth % 360
#
#     def set_beamwidth(self, beamwidth: float):
#         """设置波束宽度"""
#         self.beamwidth = max(0, min(beamwidth, 360))  # 限制在0-360度
#
#     def set_active(self, active: bool):
#         self.active = active
#
#     def can_accept(self):
#         return len(self.users) < self.max_users
#
#     def add_user(self, user_id):
#         if self.can_accept():
#             self.users.add(user_id)
#             return True
#         return False
#
#     def remove_user(self, user_id):
#         self.users.discard(user_id)
#
#     def set_power(self, power: float):
#         self.power = power
#
#     def set_center(self, center: Tuple[float, float]):
#         self.center = center
#
# # ===================== 用户 =====================
# class User:
#     def __init__(self, user_id: int, pos: Tuple[float, float]):
#         self.user_id = user_id
#         self.pos = pos
#         self.connected_beam: Optional[int] = None
#
# # ===================== 波束控制系统 =====================
# class BeamControlSystem:
#     def __init__(self, n_beams: int, beam_radius: float, max_users_per_beam: int,
#                  freq_list: List[float], initial_centers: Optional[List[Tuple[float, float]]] = None):
#         self.beams: Dict[int, Beam] = {}
#         self.users: Dict[int, User] = {}
#         self.n_beams = n_beams  # 总波束数（10站点×6波束=60）
#         self.time = 0
#
#         # 获取优化的站点中心（10个）
#         centers = initial_centers if initial_centers is not None else [
#             (random.uniform(-60, 60), random.uniform(-180, 180))
#             for _ in range(n_beams // 6)  # 每个站点对应6个波束，总站点数=总波束数/6
#         ]
#
#         # 为每个站点生成6个60度波束（覆盖360度）
#         for site_idx, site_center in enumerate(centers):
#             for beam_in_site in range(6):  # 每个站点生成6个波束
#                 beam_id = site_idx * 6 + beam_in_site  # 总波束ID（0-59）
#                 freq = freq_list[beam_id % len(freq_list)]  # 频率循环分配
#                 # 方位角：每个波束间隔60度（360/6）
#                 azimuth = beam_in_site * 60
#                 self.beams[beam_id] = Beam(
#                     beam_id=beam_id,
#                     center=site_center,  # 共享站点中心
#                     radius=beam_radius,
#                     max_users=max_users_per_beam,
#                     freq=freq,
#                     azimuth=azimuth,  # 0°, 60°, 120°...300°
#                     beamwidth=60.0  # 波束宽度固定60度
#                 )
#
#     def set_beam_active(self, beam_id: int, active: bool):
#         """开启或关闭波束"""
#         if beam_id in self.beams:
#             self.beams[beam_id].set_active(active)
#             self.assign_users_to_beams()
#
#     def set_beam_azimuth(self, beam_id: int, azimuth: float):
#         """设置波束角度"""
#         if beam_id in self.beams:
#             self.beams[beam_id].set_azimuth(azimuth)
#             self.assign_users_to_beams()
#
#     def set_beam_beamwidth(self, beam_id: int, beamwidth: float):
#         """设置波束宽度"""
#         if beam_id in self.beams:
#             self.beams[beam_id].set_beamwidth(beamwidth)
#             self.assign_users_to_beams()
#
#
#     def add_user(self, user_id: int, pos: Tuple[float, float]):
#         self.users[user_id] = User(user_id, pos)
#
#     def remove_user(self, user_id: int):
#         if user_id in self.users:
#             beam_id = self.users[user_id].connected_beam
#             if beam_id is not None and beam_id in self.beams:
#                 self.beams[beam_id].remove_user(user_id)
#             del self.users[user_id]
#
#     def assign_users_to_beams(self):
#         # 先清空所有beam的用户集合
#         for beam in self.beams.values():
#             beam.users.clear()
#         # 重新分配
#         for user in self.users.values():
#             candidate_beams = [b for b in self.beams.values() if b.active and b.is_within(user.pos) and b.can_accept()]
#             if candidate_beams:
#                 # 优先用户少的，其次功率高的
#                 best_beam = min(candidate_beams, key=lambda b: (len(b.users), -b.power))
#                 best_beam.add_user(user.user_id)
#                 user.connected_beam = best_beam.beam_id
#             else:
#                 user.connected_beam = None
#
#     def dynamic_beam_switch(self, user_id: int, new_pos: Tuple[float, float]):
#         if user_id not in self.users:
#             return
#         self.users[user_id].pos = new_pos
#         self.assign_users_to_beams()
#
#     def set_beam_power(self, beam_id: int, power: float):
#         if beam_id in self.beams:
#             self.beams[beam_id].set_power(power)
#             # 设置功率后自动重新分配用户
#             self.assign_users_to_beams()
#
#     def set_beam_center(self, beam_id: int, center: Tuple[float, float]):
#         if beam_id in self.beams:
#             self.beams[beam_id].set_center(center)
#
#     def set_beam_azimuth(self, beam_id: int, azimuth: float):
#         if beam_id in self.beams:
#             self.beams[beam_id].set_azimuth(azimuth)
#             self.assign_users_to_beams()
#
#     def set_beam_beamwidth(self, beam_id: int, beamwidth: float):
#         if beam_id in self.beams:
#             self.beams[beam_id].set_beamwidth(beamwidth)
#             self.assign_users_to_beams()
#
#     def set_beam_active(self, beam_id: int, active: bool):
#         if beam_id in self.beams:
#             self.beams[beam_id].set_active(active)
#             self.assign_users_to_beams()
#
#     def frequency_reuse(self):
#         freq_beam_map = {}
#         for beam in self.beams.values():
#             freq_beam_map.setdefault(beam.freq, []).append(beam)
#         conflicts = []
#         for freq, beams in freq_beam_map.items():
#             beams = [b for b in beams if b.active]  # 只考虑开启的波束
#             for i in range(len(beams)):
#                 for j in range(i + 1, len(beams)):
#                     # 1. 计算两波束中心距离
#                     dist = self._distance(beams[i].center, beams[j].center)
#
#                     # 2. 计算两波束的方向范围（新增逻辑）
#                     # 波束i的方向范围：[azimuth_i - beamwidth_i/2, azimuth_i + beamwidth_i/2]
#                     # 波束j的方向范围：[azimuth_j - beamwidth_j/2, azimuth_j + beamwidth_j/2]
#                     beam_i = beams[i]
#                     beam_j = beams[j]
#                     lower_i = beam_i.azimuth - beam_i.beamwidth / 2
#                     upper_i = beam_i.azimuth + beam_i.beamwidth / 2
#                     lower_j = beam_j.azimuth - beam_j.beamwidth / 2
#                     upper_j = beam_j.azimuth + beam_j.beamwidth / 2
#
#                     # 3. 判断方向范围是否重叠（考虑环形360度）
#                     dir_overlap = False
#                     # 处理波束i的方向范围跨0度的情况（如 lower_i=-30°, upper_i=30°）
#                     if lower_i < 0:
#                         # 波束i的范围：[lower_i+360, 360] ∪ [0, upper_i]
#                         # 波束j的范围：[lower_j, upper_j]（假设不跨0度）
#                         dir_overlap = (upper_i >= lower_j) or (lower_i + 360 <= upper_j)
#                     elif upper_i > 360:
#                         # 波束i的范围：[lower_i, 360] ∪ [0, upper_i-360]
#                         dir_overlap = (lower_i <= upper_j) or (upper_i - 360 >= lower_j)
#                     else:
#                         # 普通情况：波束i的范围在 [lower_i, upper_i]
#                         dir_overlap = not (upper_i < lower_j or upper_j < lower_i)
#
#                     # 4. 冲突条件：距离过近 且 方向重叠（修正后）
#                     if dist < beam_i.radius + beam_j.radius and dir_overlap:
#                         conflicts.append((beam_i.beam_id, beam_j.beam_id, freq, round(dist, 2)))
#         return conflicts
#
#     def get_beam_status(self):
#         return [{
#             "beam_id": b.beam_id,
#             "center": b.center,
#             "radius": b.radius,
#             "freq": b.freq,
#             "power": b.power,
#             "user_count": len(b.users),
#             "users": list(b.users),
#             "azimuth": b.azimuth,  # 新增方位角字段
#             "beamwidth": b.beamwidth,  # 新增波束宽度字段
#             "active": b.active  # 新增
#         } for b in self.beams.values()]
#
#     def get_user_status(self):
#         return [{
#             "user_id": u.user_id,
#             "pos": u.pos,
#             "connected_beam": u.connected_beam
#         } for u in self.users.values()]
#
#     def auto_power_control(self):
#         max_users = max((len(b.users) for b in self.beams.values()), default=1)
#         for b in self.beams.values():
#             b.set_power(1.0 + 2.0 * len(b.users) / max_users if max_users else 1.0)
#
#     def interference_check(self):
#         freq_beam_map = {}
#         for b in self.beams.values():
#             freq_beam_map.setdefault(b.freq, []).append(b)
#         interference = []
#         for freq, beams in freq_beam_map.items():
#             for i in range(len(beams)):
#                 for j in range(i+1, len(beams)):
#                     dist = self._distance(beams[i].center, beams[j].center)
#                     if dist < beams[i].radius + beams[j].radius:
#                         interference.append((beams[i].beam_id, beams[j].beam_id, freq))
#         return interference
#
#     @staticmethod
#     def _distance(pos1, pos2):
#         lat1, lon1 = np.radians(pos1)
#         lat2, lon2 = np.radians(pos2)
#         dlat = lat2 - lat1
#         dlon = lon2 - lon1
#         a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
#         c = 2 * np.arcsin(np.sqrt(a))
#         earth_radius = 6371
#         return earth_radius * c
#
#     def simulate_step(self, user_move_func=None):
#         if user_move_func:
#             for user in self.users.values():
#                 new_pos = user_move_func(user.pos)
#                 user.pos = new_pos
#         self.assign_users_to_beams()
#         self.time += 1
#
#     def visualize(self):
#         return {
#             "beams": self.get_beam_status(),
#             "users": self.get_user_status(),
#             "time": self.time
#         }
#
#
# # FrontEnd/beam/beam_qt_ui.py
# import sys
# from PyQt5 import uic
# from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
# from PyQt5.QtGui import QDoubleValidator
# from BackEnd.beam_control import BeamControlSystem
# from BackEnd.beam_logic import BeamDataManager
#
# class BeamControlUI(QWidget):
#     def __init__(self):
#         super().__init__()
#         # 加载UI文件
#         uic.loadUi("FrontEnd/beam/beam_control.ui", self)
#         self.init_backend()
#         self.init_validators()
#         self.init_connections()
#         self.refresh_tables()
#
#     def init_backend(self):
#         optimized_centers = BeamDataManager.get_optimized_beam_centers()
#         self.bcs = BeamControlSystem(
#             n_beams=10,
#             beam_radius=300,
#             max_users_per_beam=50,
#             freq_list=[800, 1800, 2600],
#             initial_centers=optimized_centers
#         )
#         realistic_users = BeamDataManager.generate_realistic_users(500)
#         for uid, (lat, lon) in enumerate(realistic_users, start=1000):
#             self.bcs.add_user(uid, (lat, lon))
#         self.bcs.assign_users_to_beams()
#
#     def init_validators(self):
#         # 限制经纬度输入范围
#         self.lat.setValidator(QDoubleValidator(18.0, 53.0, 6))
#         self.lon.setValidator(QDoubleValidator(73.0, 135.0, 6))
#
#     def init_connections(self):
#         self.radius_btn.clicked.connect(self.update_beam_radius)
#         self.reset_center_btn.clicked.connect(self.reset_beam_centers)
#         self.add_btn.clicked.connect(self.add_user)
#         self.remove_btn.clicked.connect(self.remove_user)
#         self.move_btn.clicked.connect(self.move_user)
#
#     def update_beam_radius(self):
#         self.bcs.set_beam_power(self.beam_id, self.power_slider.value())
#
#     def reset_beam_centers(self):
#         self.bcs.set_beam_center(self.beam_id, self.center_slider.value())
#
# # BackEnd/beam_logic.py
# class BeamDataManager:
#     @staticmethod
#     def get_optimized_beam_centers() -> List[Tuple[float, float]]:
#         base_centers = [
#             (31.23, 121.47),   # 上海（基础位置）
#             (23.13, 113.26),   # 广州
#             (39.90, 116.40),   # 北京
#             (30.57, 104.07),   # 成都
#             (22.54, 114.05),   # 深圳
#             (36.07, 120.33),   # 青岛
#             (28.12, 112.59),   # 长沙
#             (34.27, 108.95),   # 西安
#             (43.82, 87.62),    # 乌鲁木齐
#             (25.04, 102.71)    # 昆明
#         ]
#         # 为每个中心添加±0.1°随机偏移（约10km）
#         randomized_centers = []
#         for (lat, lon) in base_centers:
#             lat += random.uniform(-0.1, 0.1)  # 纬度随机偏移
#             lon += random.uniform(-0.1, 0.1)  # 经度随机偏移
#             randomized_centers.append((round(lat, 6), round(lon, 6)))
#         return randomized_centers
#
#
#
# def check_reuse(self):
#     conflicts = self.bcs.frequency_reuse()
#     if not conflicts:
#         QMessageBox.information(self, "频率复用", "当前无频率复用冲突")
#     else:
#         msg = "检测到以下频率复用冲突（距离小于覆盖半径和）:\n"
#         for a, b, f, d in conflicts:
#             msg += f"Beam {a} 与 Beam {b}（频率 {f}MHz）距离 {d:.1f}km\n"
#         QMessageBox.warning(self, "冲突警告", msg)
#
#     # 方案2：多个定向波束组合覆盖360度（更灵活）
#     # 若希望每个中心通过**多个定向波束组合**实现360度覆盖（例如6个60度波束间隔60度），需调整波束数量和初始方位角：
#     beams_per_center = 6  # 每个中心的波束数量
#     total_beams = beams_per_center * len(centers)  # 总波束数
#     self.n_beams = total_beams  # 更新总波束数
#
#     for center_idx, (lat, lon) in enumerate(centers):
#         for beam_in_center in range(beams_per_center):
#             beam_id = center_idx * beams_per_center + beam_in_center
#             freq = freq_list[beam_id % len(freq_list)]
#             # 每个波束的方位角间隔：360 / beams_per_center
#             azimuth = (360 / beams_per_center) * beam_in_center
#             self.beams[beam_id] = Beam(
#                 beam_id=beam_id,
#                 center=(lat, lon),  # 同一中心的波束共享位置
#                 radius=beam_radius,
#                 max_users=max_users_per_beam,
#                 freq=freq,
#                 azimuth=azimuth,  # 按间隔分配方位角
#                 beamwidth=60.0  # 每个波束覆盖60度
#             )
#     # 在 init_ui 方法中添加以下代码
#
#     # 波束控制区
#     beam_control_group = QGroupBox("波束控制")
#     beam_control_layout = QVBoxLayout()
#
#     # 波束ID输入
#     beam_id_layout = QHBoxLayout()
#     beam_id_layout.addWidget(QLabel("Beam ID:"))
#     self.beam_id_input = QSpinBox()
#     self.beam_id_input.setRange(0, 59)  # 假设总波束数为60
#     beam_id_layout.addWidget(self.beam_id_input)
#     beam_control_layout.addLayout(beam_id_layout)
#
#     # 开关控制
#     beam_active_layout = QHBoxLayout()
#     self.beam_active_checkbox = QCheckBox("开启/关闭")
#     toggle_active_btn = QPushButton("应用")
#     toggle_active_btn.clicked.connect(self.toggle_beam_active)
#     beam_active_layout.addWidget(self.beam_active_checkbox)
#     beam_active_layout.addWidget(toggle_active_btn)
#     beam_control_layout.addLayout(beam_active_layout)
#
#     # 角度和宽度设置
#     beam_params_layout = QHBoxLayout()
#     beam_params_layout.addWidget(QLabel("角度(°):"))
#     self.azimuth_input = QLineEdit()
#     self.azimuth_input.setValidator(QDoubleValidator(0.0, 360.0, 1))
#     beam_params_layout.addWidget(self.azimuth_input)
#     beam_params_layout.addWidget(QLabel("宽度(°):"))
#     self.beamwidth_input = QLineEdit()
#     self.beamwidth_input.setValidator(QDoubleValidator(0.0, 360.0, 1))
#     beam_params_layout.addWidget(self.beamwidth_input)
#     set_params_btn = QPushButton("设置参数")
#     set_params_btn.clicked.connect(self.set_beam_parameters)
#     beam_params_layout.addWidget(set_params_btn)
#     beam_control_layout.addLayout(beam_params_layout)
#
#     beam_control_group.setLayout(beam_control_layout)
#     main_layout.addWidget(beam_control_group)