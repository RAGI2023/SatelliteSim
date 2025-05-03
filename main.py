import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDialog
from PyQt5.QtGui import QSurfaceFormat
from FrontEnd.mainWindow.mainWindow import Ui_MainWindow
from FrontEnd.mainWindow.openGLwidget import OpenGLWindow
from FrontEnd.query.queryClass import QueryWindow
from FrontEnd.watcher.watcherClass import WatcherWindow
import BackEnd.plan_satellite_path as plan_satellite_path
import BackEnd.bpsk as bpsk

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.widget.setAutoFillBackground(False)

        self.opengl_widget = OpenGLWindow(
            "texture/8k_earth_daymap.jpg",
            "models/satellite/10477_Satellite_v1_L3.obj",
            "models/satellite/10477_Satellite_v1_Diffuse.jpg",
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

    def submit_input(self):
        return
        
    def SelectSatellitesClicked(self):
        if (len(self.opengl_widget.clickQueue) < 2):
            print("Click more satellites...")
            return
        index1 = self.opengl_widget.clickQueue[-2]
        index2 = self.opengl_widget.clickQueue[-1]
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

    def show_input_window(self):
        self.input_window = QueryWindow()
        self.input_window.show()
        
        result = self.input_window.exec_()

        if result == QDialog.Accepted:
            self.input_date = self.input_window.input_text
            print("主窗口获取的文本：", self.input_date)


    def show_watcher_window(self):
        self.watcher_window = WatcherWindow()
        bits = [0, 1, 1, 0, 1]  # 示例比特流
        result = bpsk.bpsk_modulate(bits, carrier_freq=1000, sample_rate=10000)

        self.watcher_window.datas[0]["x"] = result[:, 0]
        self.watcher_window.datas[0]["y"] = result[:, 1]
        self.watcher_window.DataSize_in_view = int(len(result[:, 0]) / 30)
        self.watcher_window.show()
        
        self.watcher_window.widgetPlot1(
            self.watcher_window.datas[0]["x"][0:self.watcher_window.DataSize_in_view],
            self.watcher_window.datas[0]["y"][0:self.watcher_window.DataSize_in_view],
        )

        # 隐藏Text1
        self.watcher_window.showText1(False)

        # subplot1显示数据

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
