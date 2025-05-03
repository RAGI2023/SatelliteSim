import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from FrontEnd.mainWindow import Ui_MainWindow
from FrontEnd.watcher import Ui_Watcher
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from FrontEnd.openGLwidget import OpenGLWindow
import json
import BackEnd.plan_satellite_path as plan_satellite_path
import BackEnd.bpsk as bpsk

class WatcherWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)
        self.ui.subSlider1.valueChanged.connect(self.slider1_changed)
        self.ui.subSlider2.valueChanged.connect(self.slider2_changed)
        self.datas = [{"x": [], "y": []}]
        
        self.DataSize_in_view = []
        
        # 子图1
        # 初始化时设置布局（只做一次）
        self.canvas1 = FigureCanvas(Figure(figsize=(4, 3)))
        self.ax1 = self.canvas1.figure.add_subplot(111)
        self.ui.subplt1.setLayout(QVBoxLayout())
        self.ui.subplt1.layout().addWidget(self.canvas1)

        # 子图2
        # 初始化时设置布局（只做一次）
        self.canvas2 = FigureCanvas(Figure(figsize=(4, 3)))
        self.ax2 = self.canvas2.figure.add_subplot(111)
        self.ui.subplt2.setLayout(QVBoxLayout())
        self.ui.subplt2.layout().addWidget(self.canvas2)



    def showORhidePlt1(self, show, show_slide = True):
        if show:
            self.ui.subplt1.show()
            self.ui.subtitle1.show()
            if show_slide:
                self.ui.subSlider1.show()
        else:
            self.ui.subplt1.hide()
            self.ui.subtitle1.hide()
            self.ui.subSlider1.hide()

    def showORhidePlt2(self, show, show_slide = True):
        if show:
            self.ui.subplt2.show()
            self.ui.subtitle2.show()
            if show_slide:
                self.ui.subSlider2.show()
        else:
            self.ui.subplt2.hide()
            self.ui.subtitle2.hide()
            self.ui.subSlider2.hide()
    
    def showORhideText1(self, show):
        if show:
            self.ui.text1.show()
        else:
            self.ui.text1.hide()

    def slider1_changed(self, value):
        print("Slider 1 changed:", value)
        if self.ui.SyncCheckBox.isChecked():
            self.ui.subSlider2.setValue(value)
        # 更新图表
        total_data_len = len(self.datas[0]["x"])
        show_data_index = (total_data_len - self.DataSize_in_view) * (value / 100.0)
        try:
            x = self.datas[0]["x"][int(show_data_index):int(show_data_index + self.DataSize_in_view)]
            y = self.datas[0]["y"][int(show_data_index):int(show_data_index + self.DataSize_in_view)]
            self.widgetPlot1(x, y)
        except:
            print("无法更新图表!")

    def slider2_changed(self, value):
        print("Slider 2 changed:", value)
        if self.ui.SyncCheckBox.isChecked():
            self.ui.subSlider1.setValue(value)

    def widgetPlot1(self, x, y, title = "", xlabel = "x", ylabel = "y", grid = True):
        """
        绘制图像
        Args:
            x (array-like): x轴数据
            y (array-like): y轴数据
            title (str, optional): 图像标题. Defaults to "".
            xlabel (str, optional): 横轴标签. Defaults to "x".
            ylabel (str, optional): 纵轴标签. Defaults to "y".
            grid (bool, optional): 是否显示网格. Defaults to True.
        """
        # layout = QVBoxLayout(self.ui.subplt1)  # 把 layout 加到你设置的 subplt1 上
        # fig = Figure(figsize=(4, 3))
        # canvas = FigureCanvas(fig)
        # ax = fig.add_subplot(111)

        # try:
        #     ax.plot(x, y)
        #     ax.set_title(title)
        #     ax.set_xlabel(xlabel)
        #     ax.set_ylabel(ylabel)

        #     if grid:
        #         ax.grid()
        # except:
        #     print("无法绘制数据")
        #     return
        # layout.addWidget(canvas)
        # canvas.draw()

        self.ax1.clear()  # 清除旧图
        self.ax1.plot(x, y)
        self.ax1.set_title(title)
        self.ax1.set_xlabel(xlabel)
        self.ax1.set_ylabel(ylabel)
        if grid:
            self.ax1.grid()
        self.canvas1.draw()  # 重绘

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
        self.ui.newwindow_bt.clicked.connect(self.show_new_window)
        
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


    def show_new_window(self):
        self.watcher_window = WatcherWindow()
        bits = [0, 1, 1, 0, 1]  # 示例比特流
        result = bpsk.bpsk_modulate(bits, carrier_freq=1000, sample_rate=10000)

        self.watcher_window.datas[0]["x"] = result[:, 0]
        self.watcher_window.datas[0]["y"] = result[:, 1]
        self.watcher_window.DataSize_in_view = len(result[:, 0]) / 30
        self.watcher_window.show()
        self.watcher_window.showORhideText1(False)

    def orbitRoute_cb(self, msg):
        print("收到服务端回复：", msg)
        try:
            data = json.loads(msg)  # 解析 JSON 字符串
            if "path" in data and isinstance(data["path"], list):
                sat_queue = [int(x) for x in data["path"]]  # 确保每个是整数
                self.opengl_widget.orbitQueue = sat_queue
            else:
                print("回复格式错误，缺少 'path' 字段或格式不正确")
        except (json.JSONDecodeError, ValueError) as e:
            print("无法解析 JSON 或转换为整数：", e)


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
