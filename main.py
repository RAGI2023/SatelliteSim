import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDialog
from PyQt5.QtGui import QSurfaceFormat
from FrontEnd.mainWindow.mainWindow import Ui_MainWindow
from FrontEnd.mainWindow.openGLwidget import OpenGLWindow
from FrontEnd.query.queryClass import QueryWindow
from FrontEnd.watcher.watcherClass import WatcherWindow, ensure_data_key
from FrontEnd.beam.beam_qt_ui import BeamControlUI
import BackEnd.plan_satellite_path as plan_satellite_path
import BackEnd.bpsk as bpsk
import BackEnd.ADtrans as ADtrans
import BackEnd.dsp as dsp
import BackEnd.wrapper as wrapper
import numpy as np
import time
import struct

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
        self.watcher_window = WatcherWindow()
        self.ground_control = BeamControlUI()

        layout = QVBoxLayout(self.ui.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.opengl_widget)

        palette = self.ui.widget.palette()
        palette.setColor(self.ui.widget.backgroundRole(), self.palette().color(self.backgroundRole()))
        self.ui.widget.setPalette(palette)
        self.ui.widget.setAutoFillBackground(True)

        self.ui.continue_btn.clicked.connect(self.process)
        self.ui.continue_btn.setEnabled(False)

        self.ui.SelectSatellites.clicked.connect(self.SelectSatellitesClicked)
        # 显示watcher
        self.ui.newwindow_bt.clicked.connect(self.watcher_window.show_watcher_window)
        # 显示输入窗口
        self.ui.input_btn.clicked.connect(self.show_input_window)
        self.ui.GroundButton.clicked.connect(self.ground_control.show)
        # 禁用Input按钮
        self.ui.input_btn.setEnabled(False)
        # 禁用Continue按钮
        self.ui.continue_btn.setEnabled(False)


        # 状态机
        """
        - 等待卫星:"SELECT-SAT"
        - 等待信号输入:"INPUT"
        - 准备编码:"ENCODE"
        - 准备协议封装:"WRAPPER"
        - 准备调制:"MODULATION"
        - 无缺失:"NONE"
        """
        self.status = "SELECT-SAT"

        # 开屏信息
        cat_img_path = "properties/pics/cat.png"
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
        
    def process(self):
        # 获取状态
        status = self.status
        if status == "ENCODE":
            # 开始编码
            self.add_log("Start encoding...")

            print("开始编码")
            self.encodeMethod = self.ui.encoderComboBox.currentText()
            self.ui.encoderComboBox.setEnabled(False)
            if self.encodeMethod == "CRC":
                self.add_log("Using CRC encoding...")
                print("使用CRC编码")
                crc_out = None
                # 进行CRC编码
                if self.watcher_window.analog_input_type == "TEXT":
                    crc_out = dsp.crc32(self.watcher_window.datas["input_text"]["x"])
                elif self.watcher_window.analog_input_type == "VOICE":
                    crc_out = dsp.crc32(self.watcher_window.datas["voice"]["y"])
                self.add_log(f"CRC32: {crc_out}")
                ensure_data_key(self.watcher_window.datas, "crc")
                self.watcher_window.datas["crc"]["x"] = crc_out
                self.watcher_window.ui.watcherSelect.addItem("CRC")
            elif self.encodeMethod == "Parity Check-Even":
                self.add_log("Using Parity Check-Even encoding...")
                print("使用偶校验编码")
                # 进行偶校验编码
                if self.watcher_window.analog_input_type == "TEXT":
                    data = self.watcher_window.datas["input_text"]["x"]
                    parity_bit = dsp.parity_check_auto(data, check_type="even")
                    self.add_log(f"Parity Check-Even: {parity_bit}")
                elif self.watcher_window.analog_input_type == "VOICE":
                    data = self.watcher_window.datas["voice"]["y"]
                    parity_bit = dsp.parity_check_auto(data, check_type="even")
                    self.add_log(f"Parity Check-Even: {parity_bit}")
                ensure_data_key(self.watcher_window.datas, "parity_even")
                self.watcher_window.datas["parity_even"]["x"] = parity_bit
                self.watcher_window.ui.watcherSelect.addItem("Parity Check-Even")
            elif self.encodeMethod == "Parity Check-Odd":
                self.add_log("Using Parity Check-Odd encoding...")
                print("使用奇校验编码")
                # 进行奇校验编码
                if self.watcher_window.analog_input_type == "TEXT":
                    data = self.watcher_window.datas["input_text"]["x"]
                    parity_bit = dsp.parity_check_auto(data, check_type="odd")
                    self.add_log(f"Parity Check-Odd: {parity_bit}")
                elif self.watcher_window.analog_input_type == "VOICE":
                    data = self.watcher_window.datas["voice"]["y"]
                    parity_bit = dsp.parity_check_auto(data, check_type="odd")
                    self.add_log(f"Parity Check-Odd: {parity_bit}")
                ensure_data_key(self.watcher_window.datas, "parity_odd")
                self.watcher_window.datas["parity_odd"]["x"] = parity_bit
                self.watcher_window.ui.watcherSelect.addItem("Parity Check-Odd")
            print("编码完成")
            self.add_log("Encoding finished.")
            html_content = """
            <h1>编码完成!</h1>
            <p>请点击Continue按钮进行协议封装</p>
            <p>请点击Watcher按钮查看数据</p>
            """
            self.ui.statusBox.setHtml(html_content)
            self.status = "WRAPPER"
        elif status == "WRAPPER":
            self.add_log("Begin wrapper")
            self.watcher_window.wrapper_method = self.ui.wrapper_comboBox.currentText()
            if self.watcher_window.analog_input_type == "TEXT":
                # 1. 获取文本内容
                text = self.watcher_window.datas["input_text"]["x"]  # 字符串
                text_bytes = text.encode('utf-8')  # 转为 UTF-8 字节流

                # 2. 获取 CRC 值（int）并打包为 4 字节
                crc_int = self.watcher_window.datas["crc"]["x"]
                crc_bytes = struct.pack(">I", crc_int)

                # 3. 拼接文本数据和 CRC
                data = text_bytes + crc_bytes
            elif self.watcher_window.analog_input_type == "VOICE":
                voice_list = self.watcher_window.datas["voice"]["y"]  # list of int
                voice_bytes = np.array(voice_list, dtype=np.int16).tobytes()

                # 2. 获取 CRC 值（如果是 int）
                crc_int = self.watcher_window.datas["crc"]["x"]
                crc_bytes = struct.pack(">I", crc_int)  # 4 字节，大端字节序

                data = voice_bytes + crc_bytes

            # 进行协议封装
            ensure_data_key(self.watcher_window.datas, "packed_data")
            packed_data = wrapper.pack_protocol(data, str(self.start_sat), str(self.end_sat))
            self.watcher_window.datas["packed_data"]["x"] = packed_data

            self.watcher_window.ui.watcherSelect.addItem("wrapper")
            self.ui.wrapper_comboBox.setEnabled(False)
            self.status = "MODULATION"
            html_content = """
            <h3>已经完成协议封装!</h3>
            <h3>按continue可以继续调制!</h3>
            """
            self.ui.statusBox.setHtml(html_content)
            self.add_log("Finished Wrapper")
            self.status = "MODULATION"
        elif status == "MODULATION":
            self.add_log("Begin modulation")
            # 进行调制
            self.modulation_method = self.ui.modulation_comboBox.currentText()
            self.ui.modulation_comboBox.setEnabled(False)
            if self.modulation_method == "bpsk":
                self.add_log("Using BPSK modulation...")
                print("使用BPSK调制")
                # 获取打包后的数据
                packed_data = self.watcher_window.datas["packed_data"]["x"]
                # 进行BPSK调制
                modulated_data = bpsk.bpsk_modulate(packed_data, self.watcher_window.datas["voice"]["DSPF"])
                


    
    


            
                

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
        self.start_sat = self.opengl_widget.clickQueue[-2]
        self.end_sat = self.opengl_widget.clickQueue[-1]
        self.add_log(f"Successfully select 2 satellites: {self.start_sat}, {self.end_sat}")
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
        

        self.opengl_widget.orbitQueue = plan_satellite_path.plan_satellite_path(sattelites_dics, self.start_sat, self.end_sat)
        log = "Best Path:" + ", ".join(map(str, self.opengl_widget.orbitQueue))
        self.add_log(log)

        self.status_html_content = f"""
        <h1>很好,现在你选择了两个卫星!</h1>
        <p>现在可以选择输入信号.输入一段音乐或者一段文本都可以</p>
        <h1>点一下Set Input吧!</h1>
        <p><img src="properties/pics/bug-fix.jpg" width="125"/></p>
        <p>你的Select Satellites按钮我先没收了</p>
        """
        self.ui.statusBox.setHtml(self.status_html_content)
        self.status = "INPUT"
        self.ui.SelectSatellites.setEnabled(False)
        self.ui.input_btn.setEnabled(True)

    def show_input_window(self):
        if self.status != "INPUT":
            self.add_log("OOPS! Select sats first", "WARN")
            return
        self.input_window = QueryWindow()
        
        self.input_window.show()
        receive = False
        result = self.input_window.exec_()

        if result == QDialog.Accepted:
            input_data = self.input_window.input_data
            data_type = self.input_window.inputType

            
            if data_type == "TEXT":
                ensure_data_key(self.watcher_window.datas, "input_text")
                self.watcher_window.datas["input_text"]["x"] = input_data
                print(self.watcher_window.datas["input_text"]["x"])
                self.watcher_window.datas["input_text"]["y"] = []
                print("主窗口获取的文本：", input_data)
                if (input_data != ""):
                    receive = True
                    self.add_log("Receive text content!")

            elif data_type == "VOICE":
                print("主窗口获取的音频路径：", input_data)
                try:
                    ddata_digi, rate_digi = ADtrans.extract_audio_segment(input_data, 1000*70, 1000)
                    ddata_ana, rate_ana = ADtrans.extract_audio_segment(input_data, 1000*70, 1000, 16000)
                    
                    # 16kHz 音乐，作为模拟量
                    ensure_data_key(self.watcher_window.datas, "voice_analog")
                    self.watcher_window.datas["voice_analog"]["x"] = np.linspace(0, len(ddata_ana) / rate_ana, num=len(ddata_ana)).tolist()
                    self.watcher_window.datas["voice_analog"]["y"] = ddata_ana.tolist()
                    self.watcher_window.datas["voice_analog"]["DSPF"] = int(len(ddata_ana) / 30)

                    # 8kHz 音乐，作为数字量
                    ensure_data_key(self.watcher_window.datas, "voice")
                    self.watcher_window.datas["voice"]["x"] = np.linspace(0, len(ddata_digi) / rate_digi, num=len(ddata_digi)).tolist()
                    self.watcher_window.datas["voice"]["y"] = ddata_digi.tolist()
                    self.watcher_window.datas["voice"]["DSPF"] = int(len(ddata_digi) / 30)

                    print(self.watcher_window.datas)
                    receive = True
                    self.add_log("Reading mp3 file...")
                except Exception as e:
                    self.add_log("Failed to read mp3 file. Try Again?", "WARN")
                    print("音频文件读取失败:", e)
                    print("try: apt install ffmpeg")
                    receive = False
            if receive:
                self.ui.input_btn.setEnabled(False)
                self.status_html_content = """
                <h3>收到了你的输入数据!</h3>
                <h3>完成了AD转换</h3>
                <h3>点一下Watcher可以看到数据</h3>
                <p><img src=properties/pics/smile.jpg width=125></p>
                <h3>在Encoder处选择编码方式</h3>
                <p>随后点击Continue</p>
                """
                self.ui.statusBox.setHtml(self.status_html_content)

                # 更新状态机
                self.status = "ENCODE"
                self.ui.continue_btn.setEnabled(True)
                self.ui.continue_btn.setEnabled(True)

                self.add_log(f"ANALOG INPUT TYPE: {data_type}")
                self.add_log("AD conversion finished.")
                
                # 记录模拟输入类型
                self.watcher_window.analog_input_type = data_type

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
