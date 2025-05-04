import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDialog
from PyQt5.QtGui import QSurfaceFormat
from FrontEnd.mainWindow.mainWindow import Ui_MainWindow
from FrontEnd.mainWindow.openGLwidget import OpenGLWindow
from FrontEnd.query.queryClass import QueryWindow
from FrontEnd.watcher.watcherClass import WatcherWindow
import BackEnd.plan_satellite_path as plan_satellite_path
import BackEnd.bpsk as bpsk
import BackEnd.ADtrans as ADtrans
import numpy as np
import time

def ensure_data_key(datas, key):
    if key not in datas:
        datas[key] = {"x": [], "y": []}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.widget.setAutoFillBackground(False)

        self.opengl_widget = OpenGLWindow(
            "properties/texture/8k_earth_daymap.jpg",
            "properties/models/satellite/10477_Satellite_v1_L3.obj",
            "properties/models/satellite/10477_Satellite_v1_Diffuse.jpg",
            parent=self.ui.widget
        )

        layout = QVBoxLayout(self.ui.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.opengl_widget)

        palette = self.ui.widget.palette()
        palette.setColor(self.ui.widget.backgroundRole(), self.palette().color(self.backgroundRole()))
        self.ui.widget.setPalette(palette)
        self.ui.widget.setAutoFillBackground(True)

        self.ui.SelectSatellites.clicked.connect(self.SelectSatellitesClicked)
        # 显示watcher
        self.ui.newwindow_bt.clicked.connect(self.show_watcher_window)
        # 显示输入窗口
        self.ui.input_btn.clicked.connect(self.show_input_window)

        self.watcher_window = WatcherWindow()

        # 状态机
        """
        - 等待卫星:"SELECT-SAT"
        - 等待信号输入:"INPUT"
        - 无缺失:"NONE"
        """
        self.status = "SELECT-SAT"

        # 开屏信息
        cat_img_path = "properties/cat.png"
        self.status_html_content = f"""
        <h3>欢迎来到神奇妙妙卫星仿真</h3>
        <p>这个UI设计简直是一坨屎</p>
        <p>那咋了</p>
        <p><img src="{cat_img_path}"/></p>
        <p>请点击左侧旋转的卫星的要通讯的卫星</p>
        
        """
        self.logs = []
        self.ui.statusBox.setHtml(self.status_html_content)

        self.add_log("Simulation Begin.")
        
    def add_log(self, log_message, log_level="INFO"):
            """
            添加日志信息，带有不同颜色的日志级别
            """
            # 获取当前时间戳
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 根据日志级别设置不同的颜色
            if log_level == "INFO":
                color = "green"
            elif log_level == "WARNING":
                color = "orange"
            elif log_level == "ERROR":
                color = "red"
            else:
                color = "black"  # 默认颜色

            # 格式化日志内容并添加颜色
            log_entry = f"<p style='color:{color}; font-size:10px;'><b>[{timestamp}] [{log_level}]</b> {log_message}</p>"

            # 将日志添加到日志列表
            self.logs.append(log_entry)

            # 更新 QTextBrowser 显示内容
            self.ui.logBox.setHtml("".join(self.logs))  # 将所有日志合并成 HTML 内容

            # 确保显示的视野自动滚动到最新日志
            self.ui.logBox.verticalScrollBar().setValue(self.ui.logBox.verticalScrollBar().maximum())

    def SelectSatellitesClicked(self):
        if (len(self.opengl_widget.clickQueue) < 2):
            print("Click more satellites...")
            self.add_log("Need to select more satelites.", "WARN")
            return
        index1 = self.opengl_widget.clickQueue[-2]
        index2 = self.opengl_widget.clickQueue[-1]
        self.add_log(f"Successfully select 2 satellites: {index1}, {index2}")
        sattelites_dics = []
        for sat in self.opengl_widget.satellites:
            sat_data = {
                "index": sat.index,
                "name": sat.name,
                "r": sat.r,
                "angle": round(sat.angle, 2),
                "speed": round(1000.0 / self.opengl_widget.update_delta_t * sat.delta_deg, 2)
            }
            sattelites_dics.append(sat_data)
        

        self.opengl_widget.orbitQueue = plan_satellite_path.plan_satellite_path(sattelites_dics, index1, index2)
        log = "Best Path:" + ", ".join(map(str, self.opengl_widget.orbitQueue))
        self.add_log(log)

    def show_input_window(self):
        self.input_window = QueryWindow()
        self.input_window.show()
        receive = False
        result = self.input_window.exec_()

        if result == QDialog.Accepted:
            self.input_data = self.input_window.input_data
            data_type = self.input_window.inputType
            if data_type == "TEXT":
                print("主窗口获取的文本：", self.input_data)
                if (self.input_data != ""):
                    receive = True

            elif data_type == "VOICE":
                print("主窗口获取的音频路径：", self.input_data)
                try:
                    ddata_8k, rate_8k = ADtrans.extract_audio_segment(self.input_data, 1000*70, 1000)
                    ensure_data_key(self.watcher_window.datas, "voice")
                    self.watcher_window.datas["voice"]["x"] = np.linspace(0, len(ddata_8k) / rate_8k, num=len(ddata_8k))
                    self.watcher_window.datas["voice"]["y"] = ddata_8k
                    self.watcher_window.DataSize_in_view = int(len(ddata_8k) / 30)

                    receive = True
                except Exception as e:
                    print("音频文件读取失败:", e)
                    receive = False
            if receive:

                self.ui.input_btn.hide()


    def show_watcher_window(self):
        # self.watcher_window = WatcherWindow()

        # TODO:添加选择数据的逻辑
        bits = [0, 1, 1, 0, 1]  # 示例比特流
        result = bpsk.bpsk_modulate(bits, carrier_freq=1000, sample_rate=10000)

        # xy数据存储
        ensure_data_key(self.watcher_window.datas, "bpsk")
        self.watcher_window.datas["bpsk"]["x"] = result[:, 0]
        self.watcher_window.datas["bpsk"]["y"] = result[:, 1]
        self.watcher_window.DataSize_in_view = int(len(result[:, 0]) / 30)
        self.watcher_window.show()

        # 隐藏Text1
        self.watcher_window.showText1(False)
        
        # subplot1显示数据
        self.watcher_window.widgetPlot1(
            self.watcher_window.datas["voice"]["x"][0:self.watcher_window.DataSize_in_view],
            self.watcher_window.datas["voice"]["y"][0:self.watcher_window.DataSize_in_view],
        )

def main():
    fmt = QSurfaceFormat()
    fmt.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
