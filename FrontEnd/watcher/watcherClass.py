from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from FrontEnd.watcher.watcher import Ui_Watcher

def ensure_data_key(datas, key):
    if key not in datas:
        datas[key] = {"x": [], "y": []}

class WatcherWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)
        self.ui.subSlider1.valueChanged.connect(self.slider1_changed)
        self.ui.subSlider2.valueChanged.connect(self.slider2_changed)
        # 空字典
        self.datas = {}

        # 当前在显示什么数据？
        self.currentShowData = ""
            
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



    def showPlt1(self, show, show_slide = True):
        if show:
            self.ui.subplt1.show()
            self.ui.subtitle1.show()
            if show_slide:
                self.ui.subSlider1.show()
        else:
            self.ui.subplt1.hide()
            self.ui.subtitle1.hide()
            self.ui.subSlider1.hide()

    def showPlt2(self, show, show_slide = True):
        if show:
            self.ui.subplt2.show()
            self.ui.subtitle2.show()
            if show_slide:
                self.ui.subSlider2.show()
        else:
            self.ui.subplt2.hide()
            self.ui.subtitle2.hide()
            self.ui.subSlider2.hide()
    
    def showText1(self, show):
        if show:
            self.ui.text1.show()
        else:
            self.ui.text1.hide()

    def slider1_changed(self, value):
        print("Slider 1 changed:", value)
        if self.ui.SyncCheckBox.isChecked():
            self.ui.subSlider2.setValue(value)
        # 更新图表

        total_data_len = len(self.datas["voice"]["x"])
        show_data_index = (total_data_len - self.DataSize_in_view) * (value / 100.0)
        try:
            x = self.datas["voice"]["x"][int(show_data_index):int(show_data_index + self.DataSize_in_view)]
            y = self.datas["voice"]["y"][int(show_data_index):int(show_data_index + self.DataSize_in_view)]
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

        self.ax1.clear()  # 清除旧图
        self.ax1.plot(x, y)
        self.ax1.set_title(title)
        self.ax1.set_xlabel(xlabel)
        self.ax1.set_ylabel(ylabel)
        if grid:
            self.ax1.grid()
        self.canvas1.draw()  # 重绘

    def widgetPlot2(self, x, y, title = "", xlabel = "x", ylabel = "y", grid = True):
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

        self.ax2.clear()  # 清除旧图
        self.ax2.plot(x, y)
        self.ax2.set_title(title)
        self.ax2.set_xlabel(xlabel)
        self.ax2.set_ylabel(ylabel)
        if grid:
            self.ax2.grid()
        self.canvas2.draw()  # 重绘