from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from FrontEnd.watcher.watcher import Ui_Watcher
import binascii
import struct
import datetime
def ensure_data_key(datas, key):
    if key not in datas:
        datas[key] = {"x": [], "y": [], "DSPF": 0}

class WatcherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)
        self.ui.subSlider1.valueChanged.connect(self.slider1_changed)
        self.ui.subSlider2.valueChanged.connect(self.slider2_changed)

        # 模拟输入类型 “TEXT” “VOICE”
        self.analog_input_type = ""
        self.currentComboBox = "AD"
        self.ui.watcherSelect.currentTextChanged.connect(self.watcherSelectChanged)

        self.wrapper_method = ""
        # 空字典
        self.datas = {}

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

    def watcherSelectChanged(self, value):
        """
        根据选择更新显示内容
        """
        self.currentComboBox = value
        if value == "AD":
            if self.analog_input_type == "TEXT":
                self.showPlt1(False)
                self.showPlt2(False)
                self.ui.text1.show()
                self.ui.text2.show()
                text_data = self.datas.get("input_text", {}).get("x", "")
                self.ui.text1.setText(str(text_data))
                
                hex_raw = binascii.hexlify(text_data.encode('utf-8')).decode('utf-8').upper()
                hex_str = ' '.join(hex_raw[i:i+2] for i in range(0, len(hex_raw), 2))
                self.ui.text2.setText(hex_str)
            elif self.analog_input_type == "VOICE":
                self.showPlt1(True)
                self.showPlt2(True)
                self.ui.text1.hide()
                self.ui.text2.hide()
                # 更新图表
                voice_data_ana = self.datas.get("voice_analog", {})
                x_data1 = voice_data_ana.get("x", [])
                y_data1 = voice_data_ana.get("y", [])
                data_size1 = self.datas["voice_analog"]["DSPF"]

                voice_data_dis = self.datas.get("voice", {})
                x_data2 = voice_data_dis.get("x", [])
                y_data2 = voice_data_dis.get("y", [])
                data_size2 = self.datas["voice"]["DSPF"]

                self.widgetPlot1(x_data1[0:data_size1], y_data1[0:data_size1], "ANALOG")
                self.widgetPlot2(x_data2[0:data_size2], y_data2[0:data_size2], "DIGITAL")
        elif value == "CRC":
            crc_data = self.datas.get("crc", {}).get("x", "")
            if self.analog_input_type == "TEXT":
                self.showPlt1(False)
                self.showPlt2(False)
                self.ui.text1.show()
                self.ui.text2.show()
                self.ui.text1.setText(str(self.datas.get("input_text", {}).get("x", "")))
            elif self.analog_input_type == "VOICE":
                self.showPlt1(True)
                self.showPlt2(False)
                self.ui.text1.hide()
                self.ui.text2.show()
            hex_raw = binascii.hexlify(str(crc_data).encode()).decode().upper()
            hex_str = ' '.join(hex_raw[i:i+2] for i in range(0, len(hex_raw), 2))
            self.ui.text2.setText(hex_str)
        elif value == "Parity Check-Odd" or value == "Parity Check-Even":
            if value == "Parity Check-Odd":
                parity_data = self.datas.get("parity_odd", {}).get("x", "")
            else:
                parity_data = self.datas.get("parity_even", {}).get("x", "")
            
            if self.analog_input_type == "TEXT":
                self.showPlt1(False)
                self.showPlt2(False)
                self.ui.text1.show()
                self.ui.text2.show()
                self.ui.text1.setText(str(self.datas.get("input_text", {}).get("x", "")))
            elif self.analog_input_type == "VOICE":
                self.showPlt1(True)
                self.showPlt2(False)
                self.ui.text1.hide()
                self.ui.text2.show()
            self.ui.text2.setText(str(parity_data))
        elif value == "wrapper":
            if self.analog_input_type == "TEXT":
                self.showPlt1(False)
                self.showPlt2(False)
                self.ui.text1.show()
                self.ui.text2.show()
                self.ui.text1.setText(str(self.datas.get("input_text", {}).get("x", "")))
            elif self.analog_input_type == "VOICE":
                self.showPlt1(True)
                self.showPlt2(False)
                self.ui.text1.hide()
                self.ui.text2.show()

            def parse_protocol_header(header: bytes, checksum_method: str = "sha256") -> str:
                """
                将协议 header 解析为 HTML 格式字符串，支持彩色显示各字段
                使用新版协议格式（timestamp 为 8 字节）
                """

                header_format = "!B16s16sQI32sBBI"
                header_size = struct.calcsize(header_format)
                if len(header) < header_size:
                    return "<span style='color:red;'>Header 长度不足，无法解析。</span>"

                unpacked = struct.unpack(header_format, header[:header_size])

                version, source, dest, timestamp, data_len, checksum, priority, data_type, sequence = unpacked
                source = source.rstrip(b'\x00').decode('utf-8')
                dest = dest.rstrip(b'\x00').decode('utf-8')
                checksum_hex = binascii.hexlify(checksum).decode('utf-8')
                time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                html = f"""
                <b>🌐 Protocol Header ({checksum_method.upper()}, {header_size} bytes):</b><br>
                <span style="color:red;">Version:</span> {version}<br>
                <span style="color:blue;">Source:</span> {source}<br>
                <span style="color:green;">Destination:</span> {dest}<br>
                <span style="color:orange;">Timestamp:</span> {timestamp} <i>({time_str})</i><br>
                <span style="color:purple;">Data Length:</span> {data_len} bytes<br>
                <span style="color:brown;">Checksum ({checksum_method}):</span><br>
                <code style="color:#444;">{checksum_hex}</code><br>
                <span style="color:teal;">Priority:</span> {priority}<br>
                <span style="color:darkcyan;">Data Type:</span> {data_type}<br>
                <span style="color:gray;">Sequence:</span> {sequence}
                """
                return html
            
         
            self.ui.text2.setHtml(parse_protocol_header(self.datas["packed_data"]["x"], self.wrapper_method))
        elif value == "bpsk_modulated":
            mod_data = self.datas.get("bpsk_modulated", {}).get("x", [])
           # 解包 x 和 y
            x_data = mod_data[:, 0]
            y_data = mod_data[:, 1]
            self.showPlt1(True)
            self.showPlt2(False)
            self.ui.text1.hide()
            self.ui.text2.hide()
            self.widgetPlot1(x_data, y_data, "BPSK")

    def showPlt1(self, show, show_slide = True):
        if show:
            self.ui.subplt1.show()
            self.ui.subtitle1.show()
            if show_slide:
                self.ui.subSlider1.show()
            self.ui.stackedWidget.setCurrentIndex(0)  # 显示 subplt1 页
            
        else:
            self.ui.subplt1.hide()
            self.ui.subtitle1.hide()
            self.ui.subSlider1.hide()
            self.ui.stackedWidget.setCurrentIndex(1)  # 显示 text1 页

    def showPlt2(self, show, show_slide = True):
        if show:
            self.ui.subplt2.show()
            self.ui.subtitle2.show()
            if show_slide:
                self.ui.subSlider2.show()
            self.ui.stackedWidget_2.setCurrentIndex(0)  # 显示 subplt1 页
            
        else:
            self.ui.subplt2.hide()
            self.ui.subtitle2.hide()
            self.ui.subSlider2.hide()
            self.ui.stackedWidget_2.setCurrentIndex(1)  # 显示 subplt1 页

    def slider1_changed(self, value):
        print("Slider 1 changed:", value)
        if self.ui.SyncCheckBox.isChecked():
            self.ui.subSlider2.setValue(value)
        # 更新图表

        show_data_index = (len(self.datas[self.displayTAG[0]]["x"]) - self.datas[self.displayTAG[0]]["DSPF"]) * (value / 100.0)
        try:
            x = self.datas[self.displayTAG[0]]["x"][int(show_data_index):int(show_data_index + self.datas[self.displayTAG[0]]["DSPF"])]
            y = self.datas[self.displayTAG[0]]["y"][int(show_data_index):int(show_data_index + self.datas[self.displayTAG[0]]["DSPF"])]
            self.widgetPlot1(x, y)
        except:
            print("无法更新图表!")

    def slider2_changed(self, value):
        print("Slider 2 changed:", value)
        if self.ui.SyncCheckBox.isChecked():
            self.ui.subSlider1.setValue(value)

        show_data_index = (len(self.datas[self.displayTAG[1]]["x"]) - self.datas[self.displayTAG[1]]["DSPF"]) * (value / 100.0)
        try:
            x = self.datas[self.displayTAG[1]]["x"][int(show_data_index):int(show_data_index + self.datas[self.displayTAG[1]]["DSPF"])]
            y = self.datas[self.displayTAG[1]]["y"][int(show_data_index):int(show_data_index + self.datas[self.displayTAG[1]]["DSPF"])]
            self.widgetPlot2(x, y)
        except:
            print("无法更新图表!")

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
        self.ui.subtitle1.setText(title)
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
        self.ui.subtitle2.setText(title)
        if grid:
            self.ax2.grid()
        self.canvas2.draw()  # 重绘


    def show_watcher_window(self):
        try:
            self.show()
            self.ui.watcherSelect.show()

            # 当前 watcher 类型（如 "AD"）
            watcher_type = self.currentComboBox
            
            # AD 类型查看
            if watcher_type == "AD":
                # 当前输入类型（如 "TEXT" 或 "VOICE"）
                input_type = self.analog_input_type
                
                if input_type == "TEXT":
                    # 切换到文本页面
                    self.ui.stackedWidget.setCurrentIndex(1)  # text_page
                    self.ui.stackedWidget_2.setCurrentIndex(1)  # text_page
                    self.showPlt1(False)
                    self.showPlt2(False)

                    text_data = self.datas.get("input_text", {}).get("x", "")
                    self.ui.text1.setText(str(text_data))
                    
                    hex_raw = binascii.hexlify(text_data.encode('utf-8')).decode('utf-8').upper()
                    hex_str = ' '.join(hex_raw[i:i+2] for i in range(0, len(hex_raw), 2))
                    self.ui.text2.setText(hex_str)
                    self.ui.text2.show()
                    self.ui.text1.show()

                # VOICE 类型输入
                elif input_type == "VOICE":
                    # 切换到图表页面
                    self.ui.stackedWidget.setCurrentIndex(0)  # plt_page
                    self.ui.stackedWidget_2.setCurrentIndex(0)  # text_page

                    self.ui.text1.hide()
                    self.showPlt1(True, True)
                    self.showPlt2(True, True)

                    self.displayTAG = ["voice_analog", "voice"]

                    voice_data_ana = self.datas.get(self.displayTAG[0], {})
                    x_data1 = voice_data_ana.get("x", [])
                    y_data1 = voice_data_ana.get("y", [])
                    self.total_data_len1 = len(x_data1)
                    data_size1 = self.datas[self.displayTAG[0]]["DSPF"]

                    voice_data_dis = self.datas.get(self.displayTAG[1], {})
                    x_data2 = voice_data_dis.get("x", [])
                    y_data2 = voice_data_dis.get("y", [])
                    self.total_data_len2 = len(x_data2)
                    data_size2 = self.datas[self.displayTAG[1]]["DSPF"]

                    
                    self.widgetPlot2(x_data2[0:data_size2], y_data2[0:data_size2], "DIGITAL")

                    self.widgetPlot1(x_data1[0:data_size1], y_data1[0:data_size1],"ANALOG")

                else:
                    raise ValueError("Invalid input type selected.")

        except Exception as e:
            print("错误：", e)