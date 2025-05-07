
import numpy as np
import random
import time
from typing import List, Dict, Tuple, Optional

# ===================== 波束信息 =====================
class Beam:
    # ----------------------初始化波束---------------------
    def __init__(self, beam_id: int, center: Tuple[float, float], radius: float, max_users: int, freq: float):
        self.beam_id = beam_id #波束的唯一标识
        self.center = center  # (纬度, 经度)
        self.radius = radius  # 距离（km）
        self.max_users = max_users # 最大使用者
        self.freq = freq  # 频率（MHz）
        self.users = set() # 使用的人的集合
        self.power = 1.0  # 默认功率（可动态调整）
    # -------------------波束的相关方法------------------
    # 判断是否在波束覆盖范围内
    def is_within(self, user_pos: Tuple[float, float]) -> bool:
        # 计算实际距离
        lat1, lon1 = np.radians(self.center)
        lat2, lon2 = np.radians(user_pos)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        earth_radius = 6371  # km
        distance = earth_radius * c
        # 和覆盖范围比较，给出结果
        if distance <= self.radius:
            return True
        else:
            return False
    # 判断波束是否已经饱和
    def can_accept(self):
        return len(self.users) < self.max_users
    # 添加用户
    def add_user(self, user_id):
        # 先判断 后添加
        if self.can_accept():
            self.users.add(user_id)
            return True
        return False
    # 移除用户
    def remove_user(self, user_id):
        self.users.discard(user_id)
    # 设置功率
    def set_power(self, power: float):
        self.power = power

# ===================== 用户 =====================
class User:
    def __init__(self, user_id: int, pos: Tuple[float, float]):
        self.user_id = user_id # 标识符
        self.pos = pos  # 位置 (纬度, 经度)
        self.connected_beam: Optional[int] = None #初始为None，保存连接的波束ID

# ===================== 波束控制系统 =====================
class BeamControlSystem:
    def __init__(self, n_beams: int, beam_radius: float, max_users_per_beam: int, freq_list: List[float]):
        self.beams: Dict[int, Beam] = {}# 波束字典
        self.users: Dict[int, User] = {}# 用户字典
        self.time = 0                   # 系统时间从0开始
        # 随机构造波束中心
        for i in range(n_beams):
            center = (random.uniform(-60, 60), random.uniform(-180, 180))
            freq = freq_list[i % len(freq_list)]
            self.beams[i] = Beam(i, center, beam_radius, max_users_per_beam, freq)

    def add_user(self, user_id: int, pos: Tuple[float, float]):
        # 新的对象实例
        self.users[user_id] = User(user_id, pos)

    def remove_user(self, user_id: int):
        # 检查找id -> 有用户找连接的波束 -> 符合判断
        if user_id in self.users:
            beam_id = self.users[user_id].connected_beam
            if beam_id is not None and beam_id in self.beams:
                self.beams[beam_id].remove_user(user_id)
            del self.users[user_id]

    # 思路：选择功率最大或用户最少的波束
    # 具体内容没看， 别问
    def assign_users_to_beams(self):
        for user in self.users.values():
            candidate_beams = [b for b in self.beams.values() if b.is_within(user.pos) and b.can_accept()]
            if candidate_beams:
                best_beam = min(candidate_beams, key=lambda b: (len(b.users), -b.power))
                if user.connected_beam is not None and user.connected_beam != best_beam.beam_id:
                    self.beams[user.connected_beam].remove_user(user.user_id)
                if best_beam.add_user(user.user_id):
                    user.connected_beam = best_beam.beam_id
            else:
                # 无法分配
                if user.connected_beam is not None:
                    self.beams[user.connected_beam].remove_user(user.user_id)
                user.connected_beam = None

    # 更新用户位置 + 重新分配
    def dynamic_beam_switch(self, user_id: int, new_pos: Tuple[float, float]):
        if user_id not in self.users:
            return
        self.users[user_id].pos = new_pos
        self.assign_users_to_beams()

    # 设置波束功率
    def set_beam_power(self, beam_id: int, power: float):
        if beam_id in self.beams:
            self.beams[beam_id].set_power(power)

    #
    def frequency_reuse(self):
        # 高级频率复用策略：考虑波束间的干扰和频率分配优化
        freq_beam_map = {}
        for beam in self.beams.values():
            freq_beam_map.setdefault(beam.freq, []).append(beam)

        reused_freqs = set()
        conflicts = []
        for freq, beams in freq_beam_map.items():
            for i in range(len(beams)):
                for j in range(i + 1, len(beams)):
                    # 检查波束是否重叠
                    dist = self._distance(beams[i].center, beams[j].center)
                    if dist < beams[i].radius + beams[j].radius:
                        reused_freqs.add(freq)
                        conflicts.append((beams[i].beam_id, beams[j].beam_id, freq))

        # 返回复用频率、总频率数和冲突信息
        return {
            "reused_freqs": list(reused_freqs),
            "total_freqs": len(freq_beam_map),
            "conflicts": conflicts
        }

    def get_beam_status(self):
        # 返回所有波束的状态
        return [{
            "beam_id": b.beam_id,
            "center": b.center,
            "radius": b.radius,
            "freq": b.freq,
            "power": b.power,
            "user_count": len(b.users),
            "users": list(b.users)
        } for b in self.beams.values()]

    def get_user_status(self):
        # 返回所有用户的状态
        return [{
            "user_id": u.user_id,
            "pos": u.pos,
            "connected_beam": u.connected_beam
        } for u in self.users.values()]

    #遍历每个波束，根据其用户数量动态调整功率。功率分配为：1.0 + 2.0 * len(b.users) / max_users
    def auto_power_control(self):
        # 简单功率自适应：用户多的波束提升功率
        max_users = max((len(b.users) for b in self.beams.values()), default=1)
        for b in self.beams.values():
            b.set_power(1.0 + 2.0 * len(b.users) / max_users if max_users else 1.0)

    # 检查同频波束间的用户重叠，返回干扰警告
    def interference_check(self):
        # 构建频率到波束的映射关系
        freq_beam_map = {}
        for b in self.beams.values():
            freq_beam_map.setdefault(b.freq, []).append(b)
        interference = []# 存储干扰信息
        for freq, beams in freq_beam_map.items():
            for i in range(len(beams)):
                for j in range(i+1, len(beams)):
                    dist = self._distance(beams[i].center, beams[j].center)
                    if dist < beams[i].radius + beams[j].radius:
                        interference.append((beams[i].beam_id, beams[j].beam_id, freq))
        return interference

    @staticmethod
    def _distance(pos1, pos2):
        lat1, lon1 = np.radians(pos1)
        lat2, lon2 = np.radians(pos2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        earth_radius = 6371
        return earth_radius * c


    # ------------不是很有用的函数，前面的已经将用户移动和分配位置结合，这里只是为了丰富功能----------
    def simulate_step(self, user_move_func=None):
        if user_move_func:
            for user in self.users.values():
                new_pos = user_move_func(user.pos)
                user.pos = new_pos
        self.assign_users_to_beams()
        self.time += 1
    # ---------------也不是很有用的函数，只是将前面的进行打包，方便数据获取-------------------
    def visualize(self):
        # 输出可视化数据（可用于前端绘图）
        return {
            "beams": self.get_beam_status(),
            "users": self.get_user_status(),
            "time": self.time
        }
# ===================== 示例用法 =====================

if __name__ == "__main__":
    # 波束控制系统参数
    n_beams = 3
    beam_radius = 800  # km
    max_users_per_beam = 10
    freq_list = [2000, 2100, 2200]  # MHz
    # 用户
    user_positions = []  # 用于存储生成的用户位置
    for uid in range(10):
        lat = random.uniform(-60, 60)
        lon = random.uniform(-180, 180)
        user_positions.append((uid, lat, lon))  # 存储用户ID和位置
    # 初始化波束控制系统
    bcs = BeamControlSystem(n_beams, beam_radius, max_users_per_beam, freq_list)
for uid, lat, lon in user_positions:
    bcs.add_user(uid, (lat, lon))

    # 系统工作
    bcs.assign_users_to_beams()
    bcs.auto_power_control()

    # 可视化数据输出
    vis_data = bcs.visualize()
    print("Visualization data:", vis_data)

    # 动态仿真：用户移动
    def random_move(pos):
        lat, lon = pos
        lat += random.uniform(-0.5, 0.5)
        lon += random.uniform(-0.5, 0.5)
        lat = max(min(lat, 90), -90)
        lon = (lon + 180) % 360 - 180
        return (lat, lon)

    for t in range(5):
        bcs.simulate_step(user_move_func=random_move)
        bcs.auto_power_control()
        print(f"Step {t}:")
        print("Beam status:", bcs.get_beam_status())
        print("User status:", bcs.get_user_status())
        print("Interference:", bcs.interference_check())
        print("="*40)

    # 可视化数据输出
    vis_data = bcs.visualize()
    print("Visualization data:", vis_data)
