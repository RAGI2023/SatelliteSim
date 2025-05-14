import sys
import random  # 新增随机模块
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QSpinBox, QMessageBox, QSlider,QCheckBox,
    QGroupBox  # 新增：导入QGroupBox
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from BackEnd.beam_control import BeamControlSystem
from BackEnd.beam_logic import BeamDataManager

class BeamControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam 控制系统 (Qt版)")
        # 修改n_beams为60（10站点×6波束）
        self.bcs = BeamControlSystem(
            n_beams=60,  # 关键修改：总波束数=10站点×6波束
            beam_radius=100000,
            max_users_per_beam=50000,
            freq_list=[800, 1800, 2600]
        )
        self.init_test_data()
        self.init_ui()  # 调用 init_ui 方法

    def init_ui(self):
        # 主布局使用QVBoxLayout，设置全局边距和间距
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)  # 全局边距
        main_layout.setSpacing(20)  # 控件间距

        # 1. 用户操作区（使用QGroupBox分组）
        user_ops_group = QGroupBox("用户操作")
        user_ops_layout = QHBoxLayout()
        user_ops_layout.setSpacing(15)

        # 用户输入控件
        input_widgets = QWidget()
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("用户ID:"))
        self.user_id_input = QSpinBox()
        self.user_id_input.setRange(0, 9999)  # 保持原有范围
        input_layout.addWidget(self.user_id_input)
        input_layout.addWidget(QLabel("纬度:"))
        self.lat_input = QLineEdit()
        self.lat_input.setValidator(QDoubleValidator(-90.0, 90.0, 6))
        input_layout.addWidget(self.lat_input)
        input_layout.addWidget(QLabel("经度:"))
        self.lon_input = QLineEdit()
        self.lon_input.setValidator(QDoubleValidator(-180.0, 180.0, 6))
        input_layout.addWidget(self.lon_input)
        input_widgets.setLayout(input_layout)

        # 操作按钮
        btn_widgets = QWidget()
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(self.add_user)
        remove_btn = QPushButton("删除用户")
        remove_btn.clicked.connect(self.remove_user)
        move_btn = QPushButton("移动用户")
        move_btn.clicked.connect(self.move_user)
        random_add_btn = QPushButton("随机生成用户")
        random_add_btn.clicked.connect(self.random_add_user)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(move_btn)
        btn_layout.addWidget(random_add_btn)
        btn_widgets.setLayout(btn_layout)

        user_ops_layout.addWidget(input_widgets)
        user_ops_layout.addWidget(btn_widgets)
        user_ops_group.setLayout(user_ops_layout)
        main_layout.addWidget(user_ops_group)

        # 2. 波束参数调整区（使用QGroupBox分组）
        beam_params_group = QGroupBox("波束参数调整")
        beam_params_layout = QVBoxLayout()
        beam_params_layout.setSpacing(15)

        # 波束半径调整
        radius_layout = QHBoxLayout()
        self.radius_input = QLineEdit()
        self.radius_input.setValidator(QDoubleValidator(100000, 1000000, 0))
        self.radius_input.setText("500000")
        set_radius_btn = QPushButton("设置波束半径")
        set_radius_btn.clicked.connect(self.set_beam_radius)
        radius_layout.addWidget(QLabel("波束半径(千米):"))
        radius_layout.addWidget(self.radius_input)
        radius_layout.addWidget(set_radius_btn)

        # 波束功率调整
        power_layout = QHBoxLayout()
        self.beam_id_power_input = QSpinBox()
        self.beam_id_power_input.setRange(0, 59)  # 修正范围为0-59（总60波束）
        self.power_slider = QSlider(Qt.Horizontal)
        self.power_slider.setMinimum(1)
        self.power_slider.setMaximum(100)
        self.power_slider.setValue(10)
        power_btn = QPushButton("设置Beam功率")
        power_btn.clicked.connect(self.set_beam_power)
        power_layout.addWidget(QLabel("Beam ID:"))
        power_layout.addWidget(self.beam_id_power_input)
        power_layout.addWidget(QLabel("功率(0.1~10):"))
        power_layout.addWidget(self.power_slider)
        power_layout.addWidget(power_btn)

        # 频率复用检查按钮
        reuse_btn = QPushButton("检查频率复用冲突")
        reuse_btn.clicked.connect(self.check_reuse)

        beam_params_layout.addLayout(radius_layout)
        beam_params_layout.addLayout(power_layout)
        beam_params_layout.addWidget(reuse_btn)
        beam_params_group.setLayout(beam_params_layout)
        main_layout.addWidget(beam_params_group)

        # 3. 状态监控区（表格）
        status_group = QGroupBox("系统状态监控")
        status_layout = QVBoxLayout()

        # 波束状态表
        self.beam_table = QTableWidget()
        self.beam_table.setColumnCount(7)
        self.beam_table.setHorizontalHeaderLabels(["BeamID", "功率", "频率", "用户数", "中心", "方位角(°)", "波束宽度(°)"])
        self.beam_table.setEditTriggers(QTableWidget.NoEditTriggers)
        status_layout.addWidget(QLabel("波束状态"))
        status_layout.addWidget(self.beam_table)

        # 用户状态表（修复重复添加问题）
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["用户ID", "位置", "连接Beam", "距离波束中心(km)"])
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        status_layout.addWidget(QLabel("用户状态"))
        status_layout.addWidget(self.user_table)

        # 自动控制按钮
        auto_btn_layout = QHBoxLayout()
        assign_btn = QPushButton("自动分配用户")
        assign_btn.clicked.connect(self.assign_users)
        auto_power_btn = QPushButton("自动功率控制")
        auto_power_btn.clicked.connect(self.auto_power)
        auto_btn_layout.addWidget(assign_btn)
        auto_btn_layout.addWidget(auto_power_btn)
        status_layout.addLayout(auto_btn_layout)

        # 在 init_ui 方法中添加以下代码

        # 波束控制区
        beam_control_group = QGroupBox("波束控制")
        beam_control_layout = QVBoxLayout()

        # 波束ID输入
        beam_id_layout = QHBoxLayout()
        beam_id_layout.addWidget(QLabel("Beam ID:"))
        self.beam_id_input = QSpinBox()
        self.beam_id_input.setRange(0, 59)  # 假设总波束数为60
        beam_id_layout.addWidget(self.beam_id_input)
        beam_control_layout.addLayout(beam_id_layout)

        # 开关控制
        beam_active_layout = QHBoxLayout()
        self.beam_active_checkbox = QCheckBox("开启/关闭")
        toggle_active_btn = QPushButton("应用")
        toggle_active_btn.clicked.connect(self.toggle_beam_active)
        beam_active_layout.addWidget(self.beam_active_checkbox)
        beam_active_layout.addWidget(toggle_active_btn)
        beam_control_layout.addLayout(beam_active_layout)

        # 角度和宽度设置
        beam_params_layout = QHBoxLayout()
        beam_params_layout.addWidget(QLabel("角度(°):"))
        self.azimuth_input = QLineEdit()
        self.azimuth_input.setValidator(QDoubleValidator(0.0, 360.0, 1))
        beam_params_layout.addWidget(self.azimuth_input)
        beam_params_layout.addWidget(QLabel("宽度(°):"))
        self.beamwidth_input = QLineEdit()
        self.beamwidth_input.setValidator(QDoubleValidator(0.0, 360.0, 1))
        beam_params_layout.addWidget(self.beamwidth_input)
        set_params_btn = QPushButton("设置参数")
        set_params_btn.clicked.connect(self.set_beam_parameters)
        beam_params_layout.addWidget(set_params_btn)
        beam_control_layout.addLayout(beam_params_layout)

        beam_control_group.setLayout(beam_control_layout)
        main_layout.addWidget(beam_control_group)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        self.setLayout(main_layout)
        self.refresh_tables()  # 刷新表格

    # 在 BeamControlUI 类中添加以下方法

    def toggle_beam_active(self):
        """开启或关闭指定波束"""
        try:
            beam_id = self.beam_id_input.value()
            active = self.beam_active_checkbox.isChecked()
            self.bcs.set_beam_active(beam_id, active)
            self.refresh_tables()
            QMessageBox.information(self, "成功", f"Beam {beam_id} 已{'开启' if active else '关闭'}")
        except Exception as e:
            QMessageBox.warning(self, "操作失败", str(e))

    def set_beam_parameters(self):
        """设置波束的宽度和角度"""
        try:
            beam_id = self.beam_id_input.value()
            azimuth = float(self.azimuth_input.text())
            beamwidth = float(self.beamwidth_input.text())
            self.bcs.set_beam_azimuth(beam_id, azimuth)
            self.bcs.set_beam_beamwidth(beam_id, beamwidth)
            self.refresh_tables()
            QMessageBox.information(self, "成功", f"Beam {beam_id} 参数已更新：角度={azimuth}°，宽度={beamwidth}°")
        except Exception as e:
            QMessageBox.warning(self, "设置失败", str(e))

    def init_test_data(self):
        """初始化测试用户和波束位置（使用真实分布）"""
        # 生成1000个真实分布的用户
        realistic_users = BeamDataManager.generate_realistic_users(1000)
        for uid, (lat, lon) in enumerate(realistic_users, start=1000):
            self.bcs.add_user(uid, (lat, lon))

        # 获取优化的站点中心（10个）
        optimized_centers = BeamDataManager.get_optimized_beam_centers()
        # 为每个站点的6个波束设置相同中心（总波束数60，站点数10）
        for site_idx, (lat, lon) in enumerate(optimized_centers):
            for beam_in_site in range(6):
                beam_id = site_idx * 6 + beam_in_site
                self.bcs.set_beam_center(beam_id, (lat, lon))  # 6个波束共享站点中心

        self.bcs.assign_users_to_beams()

    def refresh_tables(self):
        beams = self.bcs.get_beam_status()
        self.beam_table.setColumnCount(7)
        self.beam_table.setHorizontalHeaderLabels(["BeamID", "功率", "频率", "用户数", "中心", "方位角(°)", "波束宽度(°)"])
        self.beam_table.setRowCount(len(beams))
        for i, b in enumerate(beams):
            self.beam_table.setItem(i, 0, QTableWidgetItem(str(b["beam_id"])))
            self.beam_table.setItem(i, 1, QTableWidgetItem(f"{b['power']:.2f}"))
            self.beam_table.setItem(i, 2, QTableWidgetItem(str(b["freq"])))
            self.beam_table.setItem(i, 3, QTableWidgetItem(str(b["user_count"])))
            self.beam_table.setItem(i, 4, QTableWidgetItem(str(b["center"])))  # 显示站点中心（6个波束共享）
            self.beam_table.setItem(i, 5, QTableWidgetItem(f"{b['azimuth']:.1f}"))  # 0°,60°...300°
            self.beam_table.setItem(i, 6, QTableWidgetItem(f"{b['beamwidth']:.1f}"))  # 固定60°
        # 刷新用户表（新增距离计算）
        users = self.bcs.get_user_status()
        self.user_table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(str(u["user_id"])))
            self.user_table.setItem(i, 1, QTableWidgetItem(f"({u['pos'][0]:.2f}, {u['pos'][1]:.2f})"))
            self.user_table.setItem(i, 2, QTableWidgetItem(str(u["connected_beam"])))

            # 计算用户到连接波束中心的距离
            if u["connected_beam"] is not None and u["connected_beam"] in self.bcs.beams:
                beam = self.bcs.beams[u["connected_beam"]]
                distance = self.bcs._distance(u["pos"], beam.center)
                self.user_table.setItem(i, 3, QTableWidgetItem(f"{distance:.1f}"))
            else:
                self.user_table.setItem(i, 3, QTableWidgetItem("无连接"))
        self.beam_table.setItem(i, 5, QTableWidgetItem(f"{b['azimuth']:.1f}"))  # 显示角度
        self.beam_table.setItem(i, 6, QTableWidgetItem(f"{b['beamwidth']:.1f}"))  # 显示宽度
        self.beam_table.setItem(i, 7, QTableWidgetItem("开启" if b["active"] else "关闭"))  # 显示开关状态

    def random_add_user(self):
        """随机生成用户并自动填充输入框"""
        uid = random.randint(10000, 99999)
        lat = round(random.uniform(-90.0, 90.0), 6)
        lon = round(random.uniform(-180.0, 180.0), 6)
        self.user_id_input.setValue(uid)
        self.lat_input.setText(str(lat))
        self.lon_input.setText(str(lon))
        self.add_user()  # 调用已有添加逻辑

    def set_beam_radius(self):

        """设置波束覆盖半径（修正逻辑）"""
        try:
            radius = float(self.radius_input.text())

            # 更新所有波束的半径（或根据需求修改单个波束）
            for beam in self.bcs.beams.values():
                beam.radius = radius
            self.bcs.assign_users_to_beams()  # 重新分配用户
            QMessageBox.information(self, "成功", f"波束半径已设置为{radius}千米")

            self.refresh_tables()
        except Exception as e:
            QMessageBox.warning(self, "设置失败", str(e))

    def random_assign_freq(self):
        """随机为波束分配频率（辅助复用测试）"""
        freq_list = self.bcs.freq_list  # 假设系统保留了频率列表
        for bid in range(self.bcs.n_beams):
            random_freq = random.choice(freq_list)
            self.bcs.set_beam_frequency(bid, random_freq)  # 假设BackEnd有该方法
        QMessageBox.information(self, "完成", "已随机分配所有波束频率")
        self.refresh_tables()  # 更新频率显示

    def set_beam_direction(self):
        try:
            bid = self.beam_id_dir_input.value()
            azimuth = float(self.azimuth_input.text())
            beamwidth = float(self.beamwidth_input.text())
            if bid not in self.bcs.beams:
                raise ValueError(f"Beam {bid} 不存在")
            # 调用后端方法设置方向和宽度
            self.bcs.beams[bid].set_azimuth(azimuth)
            self.bcs.beams[bid].set_beamwidth(beamwidth)
            self.bcs.assign_users_to_beams()  # 重新分配用户
            self.refresh_tables()
            QMessageBox.information(self, "成功", f"Beam {bid} 方向设置为 {azimuth}°，宽度 {beamwidth}°")
        except Exception as e:
            QMessageBox.warning(self, "设置失败", str(e))

    def add_user(self):
        """处理用户添加逻辑"""
        try:
            # 从输入框获取用户ID、纬度、经度
            uid = self.user_id_input.value()
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())

            # 调用后端添加用户
            self.bcs.add_user(uid, (lat, lon))
            self.bcs.assign_users_to_beams()  # 重新分配波束
            self.refresh_tables()  # 刷新表格显示
        except Exception as e:
            QMessageBox.warning(self, "输入错误", f"添加用户失败：{str(e)}")

    def remove_user(self):
        """处理用户删除逻辑"""
        try:
            uid = self.user_id_input.value()
            self.bcs.remove_user(uid)  # 调用后端删除用户
            self.refresh_tables()  # 刷新表格
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"删除用户 {uid} 失败：{str(e)}")

    def move_user(self):
        """处理用户位置移动逻辑"""
        try:
            uid = self.user_id_input.value()
            new_lat = float(self.lat_input.text())
            new_lon = float(self.lon_input.text())
            self.bcs.dynamic_beam_switch(uid, (new_lat, new_lon))  # 调用后端移动用户并切换波束
            self.refresh_tables()  # 刷新表格
        except Exception as e:
            QMessageBox.warning(self, "移动失败", f"移动用户 {uid} 失败：{str(e)}")

    def check_reuse(self):
        """检查频率复用冲突并高亮显示"""
        conflicts = self.bcs.frequency_reuse()  # 调用后端获取冲突
        if not conflicts:
            QMessageBox.information(self, "频率复用", "当前无频率复用冲突")
        else:
            # 构建冲突信息
            msg = "检测到以下频率复用冲突（距离小于覆盖半径和）:\n"
            for a, b, f, d in conflicts:
                msg += f"Beam {a} 与 Beam {b}（频率 {f}MHz）距离 {d:.1f}km\n"

            # 弹出警告并高亮冲突波束
            QMessageBox.warning(self, "冲突警告", msg)
            self.highlight_conflict_beams(conflicts)

    def highlight_conflict_beams(self, conflicts):
        """高亮显示冲突波束（红色背景）"""
        conflict_ids = set()
        for a, b, _, _ in conflicts:
            conflict_ids.add(a)
            conflict_ids.add(b)

        for row in range(self.beam_table.rowCount()):
            beam_id = int(self.beam_table.item(row, 0).text())
            for col in range(self.beam_table.columnCount()):
                item = self.beam_table.item(row, col)
                if item:
                    item.setBackground(Qt.red if beam_id in conflict_ids else Qt.white)

    # 新增：将方法移动到类内部
    def assign_users(self):
        """触发后端自动分配用户到波束"""
        self.bcs.assign_users_to_beams()
        self.refresh_tables()  # 刷新显示

    def auto_power(self):
        """触发后端自动调整波束功率"""
        self.bcs.auto_power_control()
        self.refresh_tables()  # 刷新显示

    def set_beam_power(self):
        """设置指定波束的发射功率"""
        try:
            bid = self.beam_id_power_input.value()
            power = self.power_slider.value() / 10.0  # 滑块值/10转换为实际功率
            self.bcs.set_beam_power(bid, power)  # 调用后端设置功率
            self.refresh_tables()  # 刷新显示
        except Exception as e:
            QMessageBox.warning(self, "设置失败", f"设置Beam {bid} 功率失败：{str(e)}")

if __name__ == "__main__":
    # 关键修正：确保 QApplication 优先创建，且仅创建一次
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    win = BeamControlUI()  # 此时 QApplication 已存在
    win.show()
    sys.exit(app.exec_())