import numpy as np
import random
from typing import List, Dict, Tuple, Optional

# ===================== 波束信息 =====================
class Beam:
    def __init__(self, beam_id: int, center: Tuple[float, float], radius: float, max_users: int, freq: float):
        self.beam_id = beam_id
        self.center = center  # (纬度, 经度)
        self.radius = radius  # 覆盖半径（km）
        self.max_users = max_users
        self.freq = freq
        self.users = set()
        self.power = 1.0

    def is_within(self, user_pos: Tuple[float, float]) -> bool:
        lat1, lon1 = np.radians(self.center)
        lat2, lon2 = np.radians(user_pos)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        earth_radius = 6371  # km
        distance = earth_radius * c
        return distance <= self.radius

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

# ===================== 用户 =====================
class User:
    def __init__(self, user_id: int, pos: Tuple[float, float]):
        self.user_id = user_id
        self.pos = pos
        self.connected_beam: Optional[int] = None

# ===================== 波束控制系统 =====================
class BeamControlSystem:
    def __init__(self, n_beams: int, beam_radius: float, max_users_per_beam: int, freq_list: List[float]):
        self.beams: Dict[int, Beam] = {}
        self.users: Dict[int, User] = {}
        self.n_beams = n_beams
        self.time = 0
        # 均匀分布波束中心
        for i in range(n_beams):
            lat = random.uniform(-60, 60)
            lon = random.uniform(-180, 180)
            freq = freq_list[i % len(freq_list)]
            self.beams[i] = Beam(i, (lat, lon), beam_radius, max_users_per_beam, freq)

    def add_user(self, user_id: int, pos: Tuple[float, float]):
        self.users[user_id] = User(user_id, pos)

    def remove_user(self, user_id: int):
        if user_id in self.users:
            beam_id = self.users[user_id].connected_beam
            if beam_id is not None and beam_id in self.beams:
                self.beams[beam_id].remove_user(user_id)
            del self.users[user_id]

    def assign_users_to_beams(self):
        # 先清空所有beam的用户集合
        for beam in self.beams.values():
            beam.users.clear()
        # 重新分配
        for user in self.users.values():
            candidate_beams = [b for b in self.beams.values() if b.is_within(user.pos) and b.can_accept()]
            if candidate_beams:
                # 优先用户少的，其次功率高的
                best_beam = min(candidate_beams, key=lambda b: (len(b.users), -b.power))
                best_beam.add_user(user.user_id)
                user.connected_beam = best_beam.beam_id
            else:
                user.connected_beam = None

    def dynamic_beam_switch(self, user_id: int, new_pos: Tuple[float, float]):
        if user_id not in self.users:
            return
        self.users[user_id].pos = new_pos
        self.assign_users_to_beams()

    def set_beam_power(self, beam_id: int, power: float):
        if beam_id in self.beams:
            self.beams[beam_id].set_power(power)
            # 设置功率后自动重新分配用户
            self.assign_users_to_beams()

    def set_beam_center(self, beam_id: int, center: Tuple[float, float]):
        if beam_id in self.beams:
            self.beams[beam_id].set_center(center)

    def frequency_reuse(self):
        freq_beam_map = {}
        for beam in self.beams.values():
            freq_beam_map.setdefault(beam.freq, []).append(beam)
        reused_freqs = set()
        conflicts = []
        for freq, beams in freq_beam_map.items():
            for i in range(len(beams)):
                for j in range(i + 1, len(beams)):
                    dist = self._distance(beams[i].center, beams[j].center)
                    if dist < beams[i].radius + beams[j].radius:
                        reused_freqs.add(freq)
                        conflicts.append((beams[i].beam_id, beams[j].beam_id, freq, round(dist, 2)))
        return conflicts

    def get_beam_status(self):
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
        return [{
            "user_id": u.user_id,
            "pos": u.pos,
            "connected_beam": u.connected_beam
        } for u in self.users.values()]

    def auto_power_control(self):
        max_users = max((len(b.users) for b in self.beams.values()), default=1)
        for b in self.beams.values():
            b.set_power(1.0 + 2.0 * len(b.users) / max_users if max_users else 1.0)

    def interference_check(self):
        freq_beam_map = {}
        for b in self.beams.values():
            freq_beam_map.setdefault(b.freq, []).append(b)
        interference = []
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

    def simulate_step(self, user_move_func=None):
        if user_move_func:
            for user in self.users.values():
                new_pos = user_move_func(user.pos)
                user.pos = new_pos
        self.assign_users_to_beams()
        self.time += 1

    def visualize(self):
        return {
            "beams": self.get_beam_status(),
            "users": self.get_user_status(),
            "time": self.time
        }

