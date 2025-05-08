import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QSpinBox, QMessageBox, QSlider
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from BackEnd.beam_control import BeamControlSystem

class BeamControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam 控制系统 (Qt版)")
        self.bcs = BeamControlSystem(
            n_beams=5, beam_radius=500000, max_users_per_beam=5, freq_list=[800, 1800, 2600]
        )
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 用户输入区
        input_layout = QHBoxLayout()
        self.user_id_input = QSpinBox()
        self.user_id_input.setRange(0, 9999)
        self.lat_input = QLineEdit()
        self.lat_input.setValidator(QDoubleValidator(-90.0, 90.0, 6))
        self.lon_input = QLineEdit()
        self.lon_input.setValidator(QDoubleValidator(-180.0, 180.0, 6))
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(self.add_user)
        remove_btn = QPushButton("删除用户")
        remove_btn.clicked.connect(self.remove_user)
        move_btn = QPushButton("移动用户")
        move_btn.clicked.connect(self.move_user)
        input_layout.addWidget(QLabel("用户ID:"))
        input_layout.addWidget(self.user_id_input)
        input_layout.addWidget(QLabel("纬度:"))
        input_layout.addWidget(self.lat_input)
        input_layout.addWidget(QLabel("经度:"))
        input_layout.addWidget(self.lon_input)
        input_layout.addWidget(add_btn)
        input_layout.addWidget(remove_btn)
        input_layout.addWidget(move_btn)
        layout.addLayout(input_layout)

        # Beam 功率调整区
        power_layout = QHBoxLayout()
        self.beam_id_power_input = QSpinBox()
        self.beam_id_power_input.setRange(0, 99)
        self.power_slider = QSlider(Qt.Horizontal)
        self.power_slider.setMinimum(1)
        self.power_slider.setMaximum(100)
        self.power_slider.setValue(10)
        self.power_slider.setTickInterval(1)
        self.power_slider.setSingleStep(1)
        power_btn = QPushButton("设置Beam功率")
        power_btn.clicked.connect(self.set_beam_power)
        power_layout.addWidget(QLabel("Beam ID:"))
        power_layout.addWidget(self.beam_id_power_input)
        power_layout.addWidget(QLabel("功率(0.1~10):"))
        power_layout.addWidget(self.power_slider)
        power_layout.addWidget(power_btn)
        layout.addLayout(power_layout)

        # Beam 中心调整区
        beam_edit_layout = QHBoxLayout()
        self.beam_id_input = QSpinBox()
        self.beam_id_input.setRange(0, 99)
        self.center_x_input = QLineEdit()
        self.center_y_input = QLineEdit()
        self.center_x_input.setValidator(QDoubleValidator(-90.0, 90.0, 6))
        self.center_y_input.setValidator(QDoubleValidator(-180.0, 180.0, 6))
        set_center_btn = QPushButton("设置Beam中心")
        set_center_btn.clicked.connect(self.set_beam_center)
        beam_edit_layout.addWidget(QLabel("Beam ID:"))
        beam_edit_layout.addWidget(self.beam_id_input)
        beam_edit_layout.addWidget(QLabel("中心纬度:"))
        beam_edit_layout.addWidget(self.center_x_input)
        beam_edit_layout.addWidget(QLabel("中心经度:"))
        beam_edit_layout.addWidget(self.center_y_input)
        beam_edit_layout.addWidget(set_center_btn)
        layout.addLayout(beam_edit_layout)

        # 复用检查按钮
        reuse_btn = QPushButton("检查频率复用冲突")
        reuse_btn.clicked.connect(self.check_reuse)
        layout.addWidget(reuse_btn)

        # 自动分配、功率自适应按钮
        btn_layout = QHBoxLayout()
        assign_btn = QPushButton("自动分配")
        assign_btn.clicked.connect(self.assign_users)
        power_btn = QPushButton("自动功率控制")
        power_btn.clicked.connect(self.auto_power)
        btn_layout.addWidget(assign_btn)
        btn_layout.addWidget(power_btn)
        layout.addLayout(btn_layout)

        # 波束状态表
        self.beam_table = QTableWidget()
        self.beam_table.setColumnCount(5)
        self.beam_table.setHorizontalHeaderLabels(["BeamID", "功率", "频率", "用户数", "中心"])
        self.beam_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(QLabel("波束状态"))
        layout.addWidget(self.beam_table)

        # 用户状态表
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["用户ID", "位置", "连接Beam"])
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(QLabel("用户状态"))
        layout.addWidget(self.user_table)

        self.setLayout(layout)
        self.refresh_tables()

    def add_user(self):
        try:
            uid = self.user_id_input.value()
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            self.bcs.add_user(uid, (lat, lon))
            self.bcs.assign_users_to_beams()
            self.refresh_tables()
        except Exception as e:
            QMessageBox.warning(self, "输入错误", str(e))

    def remove_user(self):
        try:
            uid = self.user_id_input.value()
            self.bcs.remove_user(uid)
            self.refresh_tables()
        except Exception as e:
            QMessageBox.warning(self, "删除失败", str(e))

    def move_user(self):
        try:
            uid = self.user_id_input.value()
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            self.bcs.dynamic_beam_switch(uid, (lat, lon))
            self.refresh_tables()
        except Exception as e:
            QMessageBox.warning(self, "移动失败", str(e))

    def assign_users(self):
        self.bcs.assign_users_to_beams()
        self.refresh_tables()

    def auto_power(self):
        self.bcs.auto_power_control()
        self.refresh_tables()

    def set_beam_power(self):
        try:
            bid = self.beam_id_power_input.value()
            power = self.power_slider.value() / 10.0
            self.bcs.set_beam_power(bid, power)
            self.refresh_tables()
        except Exception as e:
            QMessageBox.warning(self, "设置失败", str(e))

    def set_beam_center(self):
        try:
            bid = self.beam_id_input.value()
            x = float(self.center_x_input.text())
            y = float(self.center_y_input.text())
            self.bcs.set_beam_center(bid, (x, y))
            self.bcs.assign_users_to_beams()
            self.refresh_tables()
        except Exception as e:
            QMessageBox.warning(self, "设置失败", str(e))

    def check_reuse(self):
        # 修正调用方法
        conflicts = self.bcs.frequency_reuse()
        if not conflicts:
            QMessageBox.information(self, "频率复用", "无冲突")
        else:
            msg = "\n".join([f"Beam {a} 与 Beam {b} 使用频率 {f}，距离 {d} km" for a, b, f, d in conflicts])
            QMessageBox.warning(self, "频率冲突", msg)

    def refresh_tables(self):
        beams = self.bcs.get_beam_status()
        self.beam_table.setRowCount(len(beams))
        for i, b in enumerate(beams):
            self.beam_table.setItem(i, 0, QTableWidgetItem(str(b["beam_id"])))
            self.beam_table.setItem(i, 1, QTableWidgetItem(f"{b['power']:.2f}"))
            self.beam_table.setItem(i, 2, QTableWidgetItem(str(b["freq"])))
            self.beam_table.setItem(i, 3, QTableWidgetItem(str(b["user_count"])))
            self.beam_table.setItem(i, 4, QTableWidgetItem(str(b["center"])))

        users = self.bcs.get_user_status()
        self.user_table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(str(u["user_id"])))
            self.user_table.setItem(i, 1, QTableWidgetItem(str(u["pos"])))
            self.user_table.setItem(i, 2, QTableWidgetItem(str(u["connected_beam"])))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BeamControlUI()
    win.show()
    sys.exit(app.exec_())
