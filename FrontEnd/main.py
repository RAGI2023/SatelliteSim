import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from mainWindow import Ui_MainWindow
from watcher import Ui_Watcher
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from openGLwidget import OpenGLWindow
import json

class WatcherWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)

    def widgetPlot(self, x, y, title = "", xlabel = "x", ylabel = "y", grid = True):
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
        layout = QVBoxLayout(self.ui.subplt1)  # 把 layout 加到你设置的 subplt1 上
        fig = Figure(figsize=(4, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        try:
            ax.plot(x, y)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)

            if grid:
                ax.grid()
        except:
            print("无法绘制数据")
            return
        layout.addWidget(canvas)
        canvas.draw()

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
        # message = {
        #     "satellites": [],
        #     "start": [index1],
        #     "end": [index2],
        # }

        # for sat in self.opengl_widget.satellites:
        #     sat_data = {
        #         "index": sat.index,
        #         "name": sat.name,
        #         "r": sat.r,
        #         "angle": round(sat.angle, 2),
        #         "speed": round(1000.0 / self.opengl_widget.update_delta_t * sat.delta_deg, 2)
        #     }
        #     message["satellites"].append(sat_data)


    def show_new_window(self):
        self.watcher_window = WatcherWindow()
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        self.watcher_window.widgetPlot(x, y, xlabel="x", ylabel="sin(x)")
        self.watcher_window.show()

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

    def watcher_cb(self, message: str):
        """
        接收 socket 消息，解析后绘图
        消息格式：x1,x2,x3|y1,y2,y3
        """
        print(f"[WatcherWindow] 收到绘图数据: {message}")
        try:
            if '|' not in message:
                raise ValueError("格式错误，缺少分隔符 '|'")

            x_str, y_str = message.strip().split('|')
            x = list(map(float, x_str.split(',')))
            y = list(map(float, y_str.split(',')))

            if len(x) != len(y):
                raise ValueError("x 与 y 数量不一致")

            # 调用你定义的绘图函数
            self.widgetPlot(x, y, title="实时绘图", xlabel="时间", ylabel="值")

        except Exception as e:
            print(f"[WatcherWindow] 数据处理失败: {e}")


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
